# vogon

`vogon` is a python library development tool that I created for my own personal use and convenience. However, if, like me, you also dig containerization and think `poetry` is a pretty awesome tool for building & packaging python libraries, you may also find `vogon` useful.

The **TL;DR** of `vogon` is that it is a Python script, masquerading as a command line utility, which automates:
1. Starting a Docker container,
1. Installing your poetry-managed Python library within the container, and
1. Hosting JupyterLab, with a kernel for the poetry venv, from the container.

[Skip to `vogon` installation and usage.](#How-to-install-and-use-vogon)

## What's the point of `vogon`, and could it work for me?
### The cool stuff.
`vogon` enables you to code locally (i.e. using your IDE/editor of choice) but execute your code within an isolated, reproducible, one-stop-shop development container. It uses Docker to isolate the install of poetry and your library dependencies from your local machine environment.

![vogon system diagram](https://raw.githubusercontent.com/rachhouse/vogon/improve-README/docs/_static/vogon_system.svg)

`vogon` sets you up with a container that you can connect to via a terminal. Within the container, you can execute your code, run your tests, and play with your code in JupyterLab.

And, bonus, if you are using VS Code, you can just connect to the Docker container directly via the [**Remote - Containers** plugin](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), and use the installed poetry venv as your Python interpreter. This is totally rad.

### Uh, couldn't I do this all without `vogon` and/or Docker and/or just use `poetry` and `pyenv` locally?
Yup, totally. There's nothing magical going on here - everything that `vogon` does can be accomplished manually, or via other tools and means. However, since I prefer a containerized workflow and dislike repetitively typing commands, I automated the process and bundled it up into a tool that orchestrates workflow setup with a few simple commands.

Plus, like any good developer, I have some opinionated opinions:tm: on local development:

* Your local environment generally has a lot more going on than a simple ubuntu Docker container. If you're working with `pyenv`/`poetry`/`virtualenv`/`conda`/`homebrew`/etc, or any combination of those tools, often

Working out of a docker container where you understand the

* I'm a big fan of disaster preparedness when it comes to development.

### The caveats.
1. It helps to be relatively familiar with Docker if you need to diagnose any unexpected behavior.
2. `vogon` is not rigorously tested, and to-date I've just used it on MacOS with Docker Desktop for Mac, and a local Python ^3.7 install.
3. `vogon` is not a installed library. To run it, you need at least one Python 3 install on your local system.
4. There's currently no versioning on `vogon`. I'd like to add this down the road

## How to install and use `vogon`
Note that vogon acts like a command line utility, but is actually a Python script. Thus, you'll need at least one Python 3 install on your local system to run it. However, you don't need any specific packages; `vogon` just uses standard Python built-ins.

### Installation
To get up and running:
1. `git clone` this repo to your local machine.
1. Add the cloned vogon directory path to the beginning of your `PATH` variable, e.g. `export PATH="/Users/you/pathto/vogon:$PATH"` in your `~/.bashrc` (or other appropriate profile file). Source your profile file and/or start a new terminal.
1. Run `vogon build` to build the default vogon Mothership image and create your `~/.vogonconfig` file.
1. Run `vogon poet` from whichever repo directory you want to use. Note that any repo/library you want to develop with vogon must be a poetry-managed library with a `pyproject.toml` file present.

### `vogon` arguments
`-m`/`--mnt-dir`
`-j`/`--mnt-dir`
`i`

## FAQ
I don't want to use the default vogon Docker image, but I do want to use the vogon workflow. What should I do?
Good news! You can use vogon with your Docker image of choice. Simply use the `-i` argument and supply the name of the container that you'd like to use.

If you want to use a different image for vogon by default, edit your `~/.vogonconfig` file and change the `default_image` to the image name of your preferred Docker image.

Note that any Docker image you use with vogon needs to have the following installed:
* python
* poetry

## Miscellaneous
The git prompt and completion goodies that `vogon` uses are compliments of the [official git git repo](https://github.com/git/git/tree/master/contrib/completion).

## Planned, but currently unscheduled, improvements
