# Developer Onboarding Guide

This guide will help you set up your development environment for contributing to MKCentral. For a complete understanding of the system architecture, see [Architecture Overview](architecture.md) after completing this guide.

## Operating system
Since we will be running our apps inside linux containers, and we are also going to use a ubuntu dev container for the dev environment, it is easiest if we clone the repo onto a unix-based machine. For Windows users, you should install WSL for this purpose using [these instructions](https://docs.microsoft.com/en-us/windows/wsl/setup/environment). 

If you have never used linux before, I would recommend at minimum to go through a tutorial to understand how to use the command line and some basic commands. Ubuntu's [Command Line for Beginners](https://ubuntu.com/tutorials/command-line-for-beginners) tutorial should be enough to get you started.

## Cloning the repo
Once you have your operating system of choice set up, you need to get the code onto your machine (WSL for Windows users). If you are not part of the developer team, make sure that you fork the repo first and clone your fork instead. To clone the repo, I recommend using the [Github CLI](https://cli.github.com/) as it makes authenticating to your Github account much easier. Installation instructions for Ubuntu/WSL can be [found here](https://github.com/cli/cli/blob/trunk/docs/install_linux.md#debian-ubuntu-linux-raspberry-pi-os-apt). 

Once you have the Github CLI installed, run `gh auth login` to authenticate to your github account (select HTTPS as the preferred auth option), navigate to the folder that you want to clone your code, and run `gh repo clone MarioKartCentral/MarioKartCentral`. 

If you want to clone just using git the old-fashioned way, I would strongly encourage you to clone using HTTPS with a [PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) as using SSH will cause issues when needing to use git from within the dev containers.

## Docker
We will be running our services (and development environment) inside docker containers, so you will need to install docker. For Windows I recommend installing [Docker Desktop](https://docs.docker.com/desktop/windows/install/) outside of WSL on your Windows host and configuring it to use WSL as the backend. 

## IDE
It is recommended to use [Visual Studio Code](https://code.visualstudio.com/) as your editor as this repo contains a number of files that are used to improve the developer experience when using VS Code. For Windows users, you should install VS Code on your Windows host outside of WSL, you can then follow [these instructions](https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode) to use your Windows installation of VS Code to open folders inside WSL. 

Next you will want to install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code. After this is installed, press `CTRL+SHIFT+P` and select `Remote-Containers: Open Folder in Container` and select the root folder of this repo. When you do this, docker will start creating a container for the development environment as well as the containers for all the service in this repo. This process will only be slow for the first time you create the container, and will be cached for whenever you open the project again.

Once the container has been created, open the `MarioKartCentral.code-workspace` file inside the explorer and click the `Open Workspace` button in the bottom-right.

## Dev containers
Your VS Code window should now be inside the context of a "dev container". This is a docker container that contains all the right tools and packages that you need to develop the project. It also has a bunch of VS Code extensions that are included and installed by default for you. If you want to learn more about Dev Containers, you can find [documentation here](https://code.visualstudio.com/docs/remote/containers).

## Docker compose
In addition to the dev container, there are three other containers which will have been created. These additional containers are defined using Docker Compose with the [`docker-compose.yml`](/docker-compose.yml) file at the root of the repo.

The docker compose file defines three services which each run in their own container:
- `api`: A web API written in Python using Starlette. See [Backend Architecture](backend.md) for implementation details.
- `frontend`: A web server that serves the client-side portion of the site using Svelte.
- `cf-worker`: A cloudflare worker project that forwards requests onto the API or Frontend based on the URL.

For details on how these components interact, see [Architecture Overview: System Components](architecture.md#system-components).

The cf-worker project is listening to requests on `localhost:5000`. An example request that will go through the cf-worker to the frontend is `localhost:5000/en-us` and a request that will go through the cf-worker to the API is `localhost:5000/api/user/list`. You can test both of these URLs in the browser and you should get back a response.

Hot reloading is enabled for the Starlette API and Svelte-Kit Frontend which means that edits to the code will reflect immediately, but if you want to rebuild a container after making some changes you can always do so by presing `CTRL+SHIFT+P` and running `Remote-Containers: Rebuild Container`.

## Frontend localizations
Localizations are handled by the typesafe-i18n npm package. It works by taking as input the localization files and generating code files containing types representing what localizations are available. If you are adding a new localization:

1. Add your new locale to [`/src/frontend/src/i18n/`](/src/frontend/src/i18n/)
2. Run `npx typesafe-i18n` inside the `/src/frontend` folder to regenerate type files
3. Update the routes configuration if needed

## Debugging the Starlette API
It is often useful to use breakpoints when developing to debug your app and step things through line by line to look for errors. The container for the API is set up with debugpy which allows us to connect to a debugging server inside the container from within VS Code. 

To enable this, set `DEBUG` to `True` inside [`/src/backend/api/app.py`](/src/backend/api/app.py). This will cause the app to restart since the files have changed and it will reach the `wait_for_client` line to wait until you have attached your editor to the debugger. Assuming you had the code workspace opened from earlier, you should be able to open the debug menu on the sidebar (or `CTRL+SHIFT+D`) and select the `Python: Remote Attach` launch task and run it. 

After you have done this breakpoints should be working. Also after you have done this once you will be able to use F5 to attach to the debugger rather than having to use the debug menu.

## Debugging the Svelte app
Svelte's debugging story is not as good as Starlette's, but if you need to debug some javascript code you can place down a `debugger;` line in the code and the browser will allow you to debug from within the browser rather than from within VS Code.

## Testing Emails Locally
The project includes Mailpit in the Docker Compose setup which captures all emails sent during local development. To access the Mailpit interface, open http://localhost:8025 in your browser.

## Discord Integration
If you wish to test discord integration locally, you will need to do the following: 
1. Log in to the [Discord Developer Portal](https://discord.com/developers/applications)
1. Create a new application. Name the app anything you want, e.g. "MKC Development" 
1. After creating, go to the OAuth2 tab and copy your client ID and client secret to the `.env` file at the root of this repository. You may need to click "Reset Secret" to see the client secret
1. On the same page, click "Add Redirect" and set it to `http://localhost:5000/api/user/discord_callback`
1. Save your changes
1. Ensure you have `ENABLE_DISCORD=true` in your `.env` file
1. Restart the dev container to ensure the environment variables are applied