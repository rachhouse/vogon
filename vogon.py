import argparse
import os
import sys
import pathlib
import random
import subprocess
import random

from datetime import datetime
from typing import Tuple

VOGON_DESCRIPTORS = """
    freddled plurdled lurgid mordious earted grumbling rancid festering confectious
    jurpling slayjid slurping jowling meated foonting hooptious crinkly ravenous
"""

VOGON_NOUNS = """
    gobberwart blurglecruncheon bindlewurdle mashurbitrie glupule gruntbuggly
    micturation gabbleblotchit jurtle organsquealer agrocrustle axlegrurt liverslime
    turlingdrome dentrassis jeltz jennings bureaucrat prostetnic bugblatter kwaltz
"""

subcommands = ["poet", "explorer"]

parser = argparse.ArgumentParser(description="~@ vogon @~")
subparsers = parser.add_subparsers()

subparser_poet = subparsers.add_parser("poet")
subparser_explorer = subparsers.add_parser("explorer")

for name, subparser in {"poet": subparser_poet, "explorer": subparser_explorer}.items():

    subparser.set_defaults(variant=name)

    subparser.add_argument(
        "-r",
        "--repo",
        help="Mount a local directory as a repo (defaults to the current directory)",
        default=".",
    )

    subparser.add_argument(
        "-m", "--mnt-dir", help="Mount a local directory as a docker volume"
    )

    subparser.add_argument(
        "-j", "--jupyterlab", help="start a jupyterlab session", action="store_true",
    )

    subparser.add_argument(
        "-p",
        "--python-version",
        choices=["3.8", "3.9"],
        help="Python version to use",
        default="3.8",
    )


def header_art(variant: str) -> str:
    if variant == "poet":
        return """
~@ vogon poet @~
        """
    elif variant == "explorer":
        return """
~@ vogon explorer @~
        """
    else:
        return None


def colorize(color: str, text: str):
    color_style = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
    }

    return f"\033[{color_style[color]}m{text}\033[0m"


def get_jupyterlab_url(container_id: str) -> Tuple[str, str]:
    start_jupyterlab_cmd = """
        docker exec -d {} \
        bash -c 'jupyter lab --ip=0.0.0.0 --no-browser --allow-root'
    """.format(
        container_id
    )

    subprocess.getoutput(start_jupyterlab_cmd)

    jupyter_get_url_cmd = "docker exec {} bash -c 'jupyter notebook list'".format(
        container_id
    )

    tries, notebook_url, notebook_mnt_dir = 0, None, None

    while (notebook_url is None) or (tries > 3):
        running_notebooks = subprocess.check_output(
            f"docker exec {container_id} bash -c 'jupyter notebook list'", shell=True
        ).decode("utf-8")

        running_notebooks = running_notebooks.split("\n")
        if running_notebooks[1]:
            # also check if url matches expected pattern
            notebook_url, notebook_mnt_dir = running_notebooks[1].split(" :: ")

        tries += 1

    if notebook_url is None:
        raise Exception("Unable to launch jupyterlab.")

    return notebook_url, notebook_mnt_dir


def main():
    args = parser.parse_args()
    random.seed(datetime.now())

    repo_dir, mnt_dir, mnt_volume = None, None, None

    if args.variant == "poet":
        print(colorize("green", header_art("poet")))

    elif args.variant == "explorer":
        print(header_art("explorer"))

    else:
        raise Exception("whaaaa")

    repo_dir = pathlib.Path(args.repo).absolute()

    print(f"Repo directory:\t{repo_dir}")

    repo_name = repo_dir.parts[-1]
    print(f"Repo name is: {repo_name}")

    if args.mnt_dir:
        mnt_dir = pathlib.Path(args.mnt_dir).absolute()
        print(f"Mnt directory:\t{mnt_dir}")

    repo_volume = f"-v {repo_dir}:/repos/{repo_name} \\" if repo_dir else "\\"
    mnt_volume = f"-v {mnt_dir}:/mnt \\" if mnt_dir else "\\"

    print(f"Python version:\t{args.python_version}")
    print(f"Jupyterlab:\t{'yes' if args.jupyterlab else 'no'}")

    print()
    print("Starting docker container.")

    container_name = "{}_{}".format(
        random.choice(VOGON_DESCRIPTORS.split()), random.choice(VOGON_NOUNS.split())
    )

    run_container_cmd = """
        docker run -it -d --rm \
            --name {container_name} \
            --env CONTAINER_NAME={container_name} \
            -p 8888:8888 \
            {add_repo_volume}
            {add_mnt_volume}
            vogon \
            bash
    """.format(
        container_name=container_name,
        add_repo_volume=repo_volume,
        add_mnt_volume=mnt_volume,
    )

    print(run_container_cmd)

    container_id = subprocess.getoutput(run_container_cmd)

    print(f"Container id: {container_id}")

    # try to poetry install the repo

    if args.jupyterlab:
        notebook_url, notebook_mnt_dir = get_jupyterlab_url(container_id)
        print(f"JupyterLab launched from {notebook_mnt_dir}:\n{notebook_url}")

    print("\n", colorize("green", ".~@ | @~" * 5), "\n")

    subprocess.call([f"docker container attach {container_id}"], shell=True)

    print(colorize("yellow", "\n** vogon destruct **"))


if __name__ == "__main__":
    sys.exit(main())
