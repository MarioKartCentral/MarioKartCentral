# Contributing to Mario Kart Central
Thank you for taking the time to contribute! 

Mario Kart Central is a community run by volunteers, and so any help we can get is greatly appreciated! Whether you are looking to add new features or fix some bugs, this guide will help get you started. If you get stuck at any point in these instructions, feel free to raise an issue and someone will be able to help resolve it for you.

## Getting Started

### Operating system
Our production machines run Ubuntu, so it is best if your development environment is also using Ubuntu or another unix-based system. For Windows users, you can install WSL for this purpose using [these instructions](https://docs.microsoft.com/en-us/windows/wsl/setup/environment#set-up-windows-terminal).

### Cloning the repo
Once you have your operating system of choice set up, you need to get the code onto your machine (WSL for Windows users). If you are not part of the developer team, make sure that you fork the repo first and clone your fork instead. To clone the repo, I recommend using the [Github CLI](https://cli.github.com/) as it makes authenticating to your Github account much easier. Installation instructions for Ubuntu/WSL can be [found here](https://github.com/cli/cli/blob/trunk/docs/install_linux.md#debian-ubuntu-linux-raspberry-pi-os-apt). 

Once you have the Github CLI installed, run `gh auth login` to authenticate to your github account (select HTTPS as the preferred auth option), navigate to the folder that you want to clone your code, and run `gh repo clone MarioKartCentral/MarioKartCentral`. 

If you want to clone just using git the old-fashioned way, I would strongly encourage you to clone using HTTPS with a [PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) as using SSH will cause issues when needing to use git from within the dev containers.

### Docker
We will be running our services (and development environment) inside docker containers, so you will need to install docker. For Windows I recommend installing [Docker Desktop](https://docs.docker.com/desktop/windows/install/) outside of WSL on your Windows host and configuring it to use WSL as the backend.

### IDE
It is recommended to use [Visual Studio Code](https://code.visualstudio.com/) as your editor as this repo contains a number of files that are used to improve the developer experience when using VS Code. For Windows users, you should install VS Code on your Windows host outside of WSL, you can then follow [these instructions](https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode) to use your Windows installation of VS Code to open folders inside WSL. 

Next you will want to install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code. After this is installed, press `CTRL+SHIFT+P` and select `Remote-Containers: Open Folder in Container` and select the root folder of this repo. When you do this, docker will start creating a container for the development environment as well as the containers for all the service in this repo. This process will only be slow for the first time you create the container, and will be cached for whenever you open the project again.

Once the container has been created, open the `MarioKartCentral.code-workspace` file inside the explorer and click the `Open Workspace` button in the bottom-right.

### Dev containers
Your VS Code window should now be inside the context of a "dev container". This is a docker container that contains all the right tools and packages that you need to develop the project. It also has a bunch of VS Code extensions that are included and installed by default for you. If you want to learn more about Dev Containers, you can find [documentation here](https://code.visualstudio.com/docs/remote/containers).

### Docker compose
In addition to the dev container, there are three other containers which will have been created. These additional containers are defined using Docker Compose with the `docker-compose.yml` file at the root of the repo.

The docker compose file defines three services which each run in their own container:
- `api`: A web API written in Python using a framework called Starlette.
- `frontend`: A web server that serves the client-side portion of the site using a framework called Svelte.
- `cf-worker`: A cloudflare worker project that will forwards requests onto the API or Frontend based on the URL.

The cf-worker project is listening to requests on `localhost:5000`. An example request that will go through the cf-worker to the frontend is `localhost:5000/en-us` and a request that will go through the cf-worker to the API is `localhost:5000/api/user/list`. You can test both of these URLs in the browser and you should get back a response.

Hot reloading is enabled for the Starlette API and Svelte-Kit Frontend which means that edits to the code will reflect immediately, but if you want to redeploy a service container after making some changes you can always do so by right clicking the `docker-compose.yml` file in the explorer and selecting `Compose Up - Select Services`.

### Frontend Localizations
Localizations are handled by the typesafe-i18n npm package. It works by taking as input the localization files and generating code files containing types representing what localizations are available. If you are adding a new localization, make sure to run `npx typesafe-i18n` inside the `/src/frontend` folder and it will generate the files again.