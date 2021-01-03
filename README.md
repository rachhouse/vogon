# vogon

Corral `poetry` and `jupyterlab` into docker for containerized python development.

To get up and running:
1. `git clone` this repo to your local machine.
1. Add the cloned vogon directory path to the beginning of your `PATH` variable, e.g. `export PATH="/Users/you/pathto/vogon:$PATH"` in your `~/.bashrc` (or other appropriate profile file). Source your profile file and/or start a new terminal.
1. Run `vogon build` to build the default vogon Mothership image and create your `~/.vogonconfig` file.
1. run `vogon poet` from whichever repo directory you want to use. Note that any repo/library you want to develop with vogon must be a poetry-managed library with a `pyproject.toml` file present.
