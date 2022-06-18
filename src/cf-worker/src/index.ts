export interface Env {
  API_ENDPOINT: string;
  FRONTEND_ENDPOINT: string;
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
      url.host = env.API_ENDPOINT;
    }
    else
    {
      url.host = env.FRONTEND_ENDPOINT;
    }

    return await fetch(new Request(url.toString(), request));
  },
};
