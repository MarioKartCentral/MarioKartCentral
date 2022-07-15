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

export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> {
    const url = new URL(request.url);
    
    if (url.pathname.startsWith("/api"))
    {
      url.host = env.API_HOST;
      url.port = env.API_PORT || "";
    }
    else
    {
      url.host = env.FRONTEND_HOST;
      url.port = env.FRONTEND_PORT || "";
      if (env.FRONTEND_USE_S3)
      {
        console.log("Using S3")
        url.protocol = "https"
        
        if (url.pathname.length == 0) {
          url.pathname = "/index.html";
        } else if (url.pathname.endsWith("/")) {
          url.pathname += "index.html";
        } else {
          const filename = url.pathname.substring(1 + url.pathname.lastIndexOf("/"));
          if (filename.indexOf(".") == -1)
          {
            url.pathname += ".html";
          }
        }

        url.pathname = `/${env.S3_BUCKET}/${env.S3_FOLDER}${url.pathname}`;
        const aws = new AwsClient({
          accessKeyId: env.S3_ACCESS_KEY,
          secretAccessKey: env.S3_SECRET_KEY,
          service: "s3",
          region: env.S3_REGION
        })
        
        console.log(url.toString())
        return await aws.fetch(url);
      }
    }

    return await fetch(new Request(url.toString(), request));
  },
};
