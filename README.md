# vogon

`vogon` is a Python library development tool that I created for my own personal use and convenience. However, if, like me, you dig containerization and think **Poetry**(https://python-poetry.org) is a pretty awesome tool for building & packaging Python libraries, you may also find `vogon` useful.

The **TL;DR** of `vogon` is that it is a Python script, masquerading as a command line utility, which automates:
1. Starting a Docker container,
1. Installing your Poetry-managed Python library within the container, and
1. Hosting JupyterLab, with a kernel for the Poetry virtualenv, from the container.

[Skip to `vogon` installation and usage.](#How-to-install-and-use-vogon)

## What's the point of `vogon`, and could it work for me?
### The cool stuff.
`vogon` enables you to code locally (i.e. using your IDE/editor of choice) but execute your code within an isolated, reproducible, one-stop-shop development container. It uses [Docker](https://www.docker.com/products/docker-desktop) to isolate the install of Poetry and your library dependencies from your local machine environment.

![vogon system diagram](https://raw.githubusercontent.com/rachhouse/vogon/improve-README/docs/_static/vogon_system.svg)

`vogon` sets you up with a container that you can connect to via a terminal. Within the container, you can execute your code, run your tests, and play with your code in [JupyterLab](http://jupyterlab.io).

And, bonus, if you are using [VS Code](https://code.visualstudio.com), you can just connect to the Docker container directly via the [**Remote - Containers** plugin](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), and use the installed Poetry virtualenv as your Python interpreter. This is totally rad.

### Uh, couldn't I do this all without `vogon` and/or Docker and/or just use Poetry and pyenv locally?
Yup, totally. There's nothing magical going on here - everything that `vogon` does can be accomplished manually, or via other tools and means. However, since I prefer a containerized workflow and dislike repetitively typing commands, I automated the process and bundled it up into a tool that orchestrates workflow setup with a few simple commands.

Plus, like any good developer, I have some opinionated opinions:tm: on local development:

* Your local environment generally has a lot more going on than a simple ubuntu Docker container. If you're working on MacOS with `pyenv`/`poetry`/`virtualenv`/`conda`/`homebrew`/etc., or any combination of those tools, often there are unanticipated environmental variables (literal and metaphorical) that can hinder development in unanticipated ways. I think the simplicity and - perhaps more importantly - control & reproducibility of a Docker container makes local development cleaner and ultimately more successful.

* I'm a big fan of disaster preparedness when it comes to development. You don't want to have your productivity sidelined for days because of an inopportune `pip install` command which forces you to rebuild your entire local Python setup. When your development environment can be both source controlled, isolated, *and* reproducibly instantiated, your worst case scenario is generally just restarting a container.

### The caveats of using `vogon`
1. It helps to be relatively familiar with Docker if you need to diagnose any unexpected behavior.
2. `vogon` is not rigorously tested, and to-date I've just used it on MacOS with Docker Desktop for Mac, and a local Python ^3.7 install.
3. `vogon` is not an installed library, it is a Python script that needs to be run by a local Python 3 interpreter.
4. There's currently no versioning on `vogon`. I'd like to add this down the road, but currently, it's just a rough, as-is, works-for-me type of tool.

## How to install and use `vogon`
Note that `vogon` acts like a command line utility, but is actually a Python script. Thus, you'll need at least one Python 3 install on your local system to run it. However, you don't need any specific packages; `vogon` just uses standard Python built-ins.

### Installation
To get up and running:
1. `git clone` this repo to your local machine.
1. Add the cloned `vogon` directory path to the beginning of your `PATH` variable, e.g. `export PATH="/Users/you/pathto/vogon:$PATH"` in your `~/.bashrc` (or other appropriate profile file). Source your profile file and/or start a new terminal.
1. Run **`vogon build`** to build the default `vogon` Mothership image and create your `~/.vogonconfig` file.
1. Run **`vogon poet`** from whichever repo directory you want to use. Note that any repo/library you want to develop with `vogon` must be a Poetry-managed library with a `pyproject.toml` file present.

### `vogon` arguments
Check out `vogon poet --help` to get the full list of args, however, here are the most commonly used and helpful:
```
  -i IMAGE, --image IMAGE
                        Name of Docker image to start the vogon container, if
                        not using the vogon default.
  -r REPO, --repo REPO  Mount a local host directory to /repos within the
                        container. Defaults to the current directory.
  -m MNT_DIR, --mnt-dir MNT_DIR
                        Mount a local host directory to /mnt within the
                        container.
  -j, --jupyterlab      Run a JupyterLab session out of the container, using
                        /mnt.
```

## FAQ
*I don't want to use the default `vogon` Docker image, but I do want to use the `vogon` workflow. What should I do?*

Good news! You can use `vogon` with your Docker image of choice. Simply use the `-i` argument and supply the name of the container that you'd like to use.

If you want to use a different image for vogon by default, edit your `~/.vogonconfig` file and change the `default_image` to the image name of your preferred Docker image.

Note that any Docker image you use with `vogon` needs to have the following installed:
* Python
* Poetry
* JupyterLab < `3.0.0` (3.0 introduced a change in behavior that was incompatible with `vogon`'s use of `jupyter lab` and `jupyter notebook` listings, and I haven't had time to check in if it's been fixed.)

## Miscellaneous
The git prompt and completion goodies that `vogon` uses are compliments of the [official git git repo](https://github.com/git/git/tree/master/contrib/completion).