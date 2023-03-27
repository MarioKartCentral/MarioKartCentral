import { AwsClient } from "aws4fetch";

export interface Env {
  API_HOST: string;
  API_PORT: string | undefined;
  FRONTEND_HOST: string;
  FRONTEND_PORT: string | undefined;
  FRONTEND_USE_S3: boolean;
  S3_ACCESS_KEY: string;
  S3_SECRET_KEY: string;
  S3_REGION: string;
  S3_BUCKET: string;
  S3_FOLDER: string;
}

const validLanguages : {[key: string]: boolean} = {
  "de": true,
  "en-gb": true,
  "en-us": true,
  "es": true,
  "fr": true,
  "ja": true
}

function isValidLanguage(language: string) {
  return validLanguages[language] === true;
}

function getCookie(request: Request, cookieName: string) {
  const cookieHeader = request.headers.get('Cookie');
  if (cookieHeader === null) {
    return null;
  }

  let i = 0;
  while (i < cookieHeader.length) {
    let valueEndIndex = cookieHeader.indexOf(';', i);
    if (valueEndIndex === -1) {
      valueEndIndex = cookieHeader.length;
    }

    if (cookieHeader.startsWith(cookieName + '=', i)) {
      return cookieHeader.slice(i + cookieName.length + 1, valueEndIndex)
    }

    i = valueEndIndex + 2; // Add 2 for length of "; "
  }

  return null;
}

const languagePreferenceCookieName = "language"
function getLanguageFromCookie(request: Request) {
  return getCookie(request, languagePreferenceCookieName);
}

function getLanguageFromAcceptLanguageHeader(request: Request) {
  const acceptLanguageHeader = request.headers.get('Accept-Language');
  if (acceptLanguageHeader === null) {
    return null;
  }

  let bestWeight = 0;
  let bestLanguage = null;
  let i = 0;
  while (i < acceptLanguageHeader.length) {
    let langEndIndex = acceptLanguageHeader.indexOf(',', i);
    if (langEndIndex === -1) {
      langEndIndex = acceptLanguageHeader.length;
    }

    const lang = acceptLanguageHeader.slice(i, langEndIndex).trim();
    const langSemicolonIndex = lang.indexOf(';');
    const langName = (langSemicolonIndex === -1 ? lang : lang.slice(0, langSemicolonIndex)).toLowerCase();
    if (isValidLanguage(langName)) {
      // With no weight assigned, then we can assume this language is the best one to use
      if (langSemicolonIndex === -1) {
        return langName;
      }

      const weight = Number.parseFloat(lang.slice(langSemicolonIndex + 3)); // Add 3 for ";q="
      if (weight === 1.0) {
        return langName;
      }

      if (weight > bestWeight) {
        bestWeight = weight;
        bestLanguage = langName;
      }
    }

    i = langEndIndex + 1;
  }

  return bestLanguage;
}

function getLanguagePreference(request: Request) {
  let language = getLanguageFromCookie(request);
  if (language !== null) { 
    // TODO: What if the language cookie is not a valid language?
    return { language, hasLanguageCookie: true };
  }

  language = getLanguageFromAcceptLanguageHeader(request);
  if (language !== null) {
    return { language, hasLanguageCookie: false };
  }

  return { language: "en-us", hasLanguageCookie: false };
}

function isStaticResource(pathName: string) {
  // All static resources in production will be under _app
  // Other paths here are used during local development
  return pathName.startsWith("/_app/") || pathName.startsWith("/@id/") || pathName.startsWith("/@vite/") || pathName.startsWith("/node_modules/") || pathName.startsWith("/.svelte-kit/") || pathName.startsWith("/usr/src/app/.svelte-kit/") || pathName.startsWith("/src/") || pathName === "/favicon.png";
}

function convertUrlPathToFilePath(pathName: string) {
  if (pathName === '' || pathName === '/') {
    return "/index.html";
  } else {
    const filename = pathName.substring(1 + pathName.lastIndexOf("/"));
    if (filename.indexOf(".") == -1) {
      return pathName + ".html";
    }
  }

  return pathName;
}

function getLanguageSegmentFromUrlPath(pathName: string) {
  if (pathName.length == 0) {
    return null;
  }

  let firstSegmentEndIndex = pathName.indexOf('/', 1); // Ignore starting slash by starting at index 1
  if (firstSegmentEndIndex === -1) {
    firstSegmentEndIndex = pathName.length;
  }

  const firstSegment = pathName.slice(1, firstSegmentEndIndex);
  return isValidLanguage(firstSegment) ? firstSegment : null;
}

async function handleApi(request: Request, env: Env) {
  const url = new URL(request.url);
  url.host = env.API_HOST;
  url.port = env.API_PORT || "";
  return await fetch(new Request(url.toString(), request));
}

async function fetchFrontendFromS3(url: URL, env: Env) {
  url.protocol = "https";
  url.pathname = `/${env.S3_BUCKET}/${env.S3_FOLDER}${convertUrlPathToFilePath(url.pathname)}`;
  const aws = new AwsClient({
    accessKeyId: env.S3_ACCESS_KEY,
    secretAccessKey: env.S3_SECRET_KEY,
    service: "s3",
    region: env.S3_REGION
  })
  
  return await aws.fetch(url);
}

async function fetchFrontend(request: Request, env: Env) {
  const url = new URL(request.url);
  url.host = env.FRONTEND_HOST;
  url.port = env.FRONTEND_PORT || "";

  let response : Response;
  if (env.FRONTEND_USE_S3) {
    response = await fetchFrontendFromS3(url, env);
  } else {
    response = await fetch(new Request(url.toString(), request));
  }

  return response;
}

async function handleFrontend(request: Request, env: Env) {
  const url = new URL(request.url);

  // always normalise URLs so that there are no trailing slashes
  if (url.pathname.endsWith('/') && url.pathname !== '/') {
    url.pathname = url.pathname.slice(0, url.pathname.length - 1);
    return Response.redirect(url.toString(), 301); // use a permanent redirect
  }
  
  let headers = [];

  let response : Response;
  if (!isStaticResource(url.pathname)) {
    const languageFromUrl = getLanguageSegmentFromUrlPath(url.pathname);
    const languagePreference = getLanguagePreference(request);

    // Set a language cookie if none exists yet
    if (!languagePreference.hasLanguageCookie) {
      let expirationDate = new Date();
      expirationDate.setDate(expirationDate.getDate() + 90);
      // If the URL has a language, use that instead of the one from Accept-Language
      // We need to set the language to the one from the URL even if it isn't correct for SEO reasons
      // In practice, we will encourage people to share links where the language is not in the URL
      const lang = languageFromUrl === null ? languagePreference.language : languageFromUrl;
      const langCookieVal = `${languagePreferenceCookieName}=${languagePreference.language}; Expires=${expirationDate.toUTCString()}`
      headers.push({ key: "Set-Cookie", value: langCookieVal})
    }

    if (languageFromUrl === null) {
      url.pathname = "/" + languagePreference.language + (url.pathname === '/' ? '' : url.pathname);
      response = Response.redirect(url.toString(), 302);
    } else if (languageFromUrl !== languagePreference.language && languagePreference.hasLanguageCookie) {
      url.pathname = "/" + languagePreference.language + url.pathname.slice(1 + languageFromUrl.length);
      response = Response.redirect(url.toString(), 302);
    } else {
      response = await fetchFrontend(request, env);
    }
  } else {
    response = await fetchFrontend(request, env);
  }

  // Clone so that we can mutate
  response = new Response(response.body, response);

  for (let header of headers) {
    response.headers.append(header.key, header.value);
  }

  return response;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    
    if (url.pathname.startsWith("/api")) {
      return await handleApi(request, env);
    } else {
      return await handleFrontend(request, env);
    }
  },
};
