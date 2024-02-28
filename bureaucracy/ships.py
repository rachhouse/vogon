""" Contains classes to run the core vogon functions: VogonBase and VogonPoet."""

import abc
import json
import os
import pathlib
import random
import re
import subprocess

from datetime import datetime
from typing import Dict, Optional, Tuple

from bureaucracy.names import VOGON_DESCRIPTORS, VOGON_NOUNS
from bureaucracy.output import colorize

class VogonBase(abc.ABC):
    """ Base class for other Vogon* classes. Contains common functionality to run
        bash commands and orchestrate docker containers.
    """

    def _get_absolute_path(self, dir: Optional[str] = None) -> Optional[pathlib.Path]:
        """ If a string dir is passed, returns pathlib.Path object referencing 
            absolute directory path of dir. If None is passed, returns None.
        """
        if dir:
            return pathlib.Path(dir).absolute()
        else:
            return None

    def _issue_command(
        self,
        command: str,
        capture_output: bool = False,
        multiline: bool = False,
        wait_for_completion: bool = False,
    ) -> Optional[str]:
        """ Run a bash command using subprocess.

            Args:
                command: string command to execute
                capture_output: bool to control if command output is returned
                multiline: bool to indicate if command output is expected to span
                    multiple lines
                wait_for_completion: bool to control if program execution should waits
                    until command completes to continue
        """

        if wait_for_completion:
            subprocess.call([command], shell=True)
        elif multiline and capture_output:
            return subprocess.check_output(command, shell=True).decode("utf-8")
        else:
            output = subprocess.getoutput(command)
            if capture_output:
                return output

    def _get_container_name(self) -> str:
        """Return a randomly generated vogon-flavor docker container name."""

        random.seed(datetime.now())
        return "{}_{}".format(
            random.choice(VOGON_DESCRIPTORS.split()), random.choice(VOGON_NOUNS.split())
        )

    def _start_docker_container(
        self,
        image_name: str,
        container_name: str,
        mnt_dir: Optional[pathlib.Path] = None,
        repo_dir: Optional[pathlib.Path] = None,
        repo_name: Optional[str] = None,
        config: Optional[Dict] = {}
    ) -> str:
        """ Start a docker container with `docker run` using input args.

            Args:
                image_name: str name of docker image to use for started container
                container_name: str name to use for started container
                mnt_dir: path of directory to mount to docker /mnt
                repo_dir: path of repo to mount to docker /repos/repo_name
                repo_name: str name of repo (final folder in repo_dir path)
                config: Dict containing vogon config details specifying run parameters

            Returns:
                container_id: str id of started container
        """

        # Assemble flag strings to mount mnt_dir and repo_dir as docker volumes.
        repo_volume = f"-v {repo_dir}:/repos/{repo_name} \\" if repo_dir else "\\"
        mnt_volume = f"-v {mnt_dir}:/mnt \\" if mnt_dir else "\\"

        config_ports, config_volumes, config_envs = [], [], []

        # Config-specified ports.
        if config.get("ports", None) is not None:
            for host_port, container_port in config["ports"].items():
                config_ports.append(f"-p {host_port}:{container_port}")

        config_ports_str = " ".join(config_ports)

        # Config-specified mounted volumes.
        if config.get("volumes", None) is not None:
            for host_path, container_path in config["volumes"].items():
                config_volumes.append(f"-v {host_path}:{container_path}")

        config_volumes_str = " ".join(config_volumes)

        # Config-specified environment variables.
        if config.get("envs", None) is not None:
            for env_name, env_value in config["envs"].items():
                if os.getenv(env_value, None) is not None:
                    environ_value = os.getenv(env_value).strip()
                    config_envs.append(f"--env {env_name}='{environ_value}'")
                else:
                    config_envs.append(f"--env {env_name}={env_value}")

        config_envs_str = " ".join(config_envs)

        start_docker_container = """
            docker run -it -d --rm \
                --name {container_name} \
                --env CONTAINER_NAME={container_name} \
                {config_envs} \
                -p 8888:8888 \
                {config_ports} \
                {add_repo_volume}
                {add_mnt_volume}
                {config_volumes} \
                {image_name} \
                bash
        """.format(
            container_name=container_name,
            add_repo_volume=repo_volume,
            add_mnt_volume=mnt_volume,
            image_name=image_name,
            config_ports=config_ports_str,
            config_volumes=config_volumes_str,
            config_envs=config_envs_str
        )

        return self._issue_command(start_docker_container, capture_output=True)

    def _attach_to_container(self, container_id: str) -> None:
        """ Attach to a running docker container.

            Args:
                container_id: string id of running container to attach to
        """
        attach_to_container = f"docker container attach {container_id}"
        self._issue_command(attach_to_container, wait_for_completion=True)

    def _start_jupyterlab(self, container_id: str) -> Tuple[str, str]:
        """ Start a jupyterlab session in a running docker container.

            Args:
                container_id: string id of running container to attach to

            Returns:
                jupyterlab url: url of running (localhost) jupyterlab, with token
                mnt directory: directory from which jupyterlab was launched
        """

        start_jupyterlab = """
            docker exec -d {} \
            bash -c 'jupyter lab --ip=0.0.0.0 --no-browser --allow-root'
        """.format(
            container_id
        )

        self._issue_command(start_jupyterlab)

        tries, jupyter_server_url, jupyter_server_mount_dir = 0, None, None

        while (jupyter_server_url is None) and (tries < 3):

            try:
                get_jupyterlab_server_url = (
                    f"docker exec {container_id} bash -c 'jupyter server list'"
                )

                # I don't know why, but for some reason this command needs to be run twice
                # for subprocess to capture the output.
                self._issue_command(get_jupyterlab_server_url, capture_output=True)
                running_servers = self._issue_command(
                    get_jupyterlab_server_url, capture_output=True
                )

                # Expected output pattern:
                # [JupyterServerListApp] Currently running servers:
                # [JupyterServerListApp] http://827c20250b6c:8888/?token=efd4e8853cbe26f40225d82fa18f15b9ea3d7b7f15a34868 :: /mnt

                running_servers = running_servers.split("\n")

                if running_servers[1]:
                    jupyter_server_url, jupyter_server_mount_dir = running_servers[1].split(" :: ")

                    # Pull out jupyterlab token and assemble URL.
                    token = re.search(r"^.*token=(.*)$", jupyter_server_url).group(1)
                    jupyter_server_url = f"http://127.0.0.1:8888/lab?token={token}"

            except Exception as err:
                print(colorize("error", f"Problem launching jupyterlab: {err}"))
                pass

            tries += 1

        if jupyter_server_url is None:
            raise Exception(f"Unable to launch jupyterlab after {tries} tries.")

        return jupyter_server_url, jupyter_server_mount_dir


class VogonPoet(VogonBase):
    """ Class to manage `vogon poet` operations.

        Example Usage:
            vogon = VogonPoet(
                docker_image_name="vogon",
                repo_dir=path_to_repo_dir,
                mnt_dir=path_to_mnt_dir,
                start_jupyter_lab=True,
            )
            vogon.launch()
    """

    def __init__(
        self,
        docker_image_name: str,
        repo_dir: str,
        mnt_dir: Optional[str] = None,
        start_jupyter_lab: bool = False,
        config: Optional[Dict] = {}
    ):
        """ Init a VogonPoet object.

            Args:
                docker_image_name: string name of docker image to use
                repo_dir: string path to repository directory
                    (repo must contain a pyproject.toml file)
                mnt_dir: Optional string path to a directory that will be mounted
                    as a docker volume at /mnt
                start_jupyter_lab: bool that controls whether a jupyterlab session is
                    started within the docker container
                config: Dict containing vogon config details specifying run parameters
        """

        self._image_name = docker_image_name
        self._mnt_dir = self._get_absolute_path(mnt_dir)
        self._repo_dir = self._get_absolute_path(repo_dir)
        self._repo_name = self._repo_dir.parts[-1]

        self._jupyter = start_jupyter_lab
        self._config = config

        self._check_for_pyproject_toml()

    def launch(self):
        """ Entry method for VogonPoet, orchestrates:
                * Outputs vogon details
                * Starts the docker container
                * Installs the repo via poetry
                * Creates an ipykernel for the poetry environment
                * Starts a jupyterlab (if requested)
                * Joins the docker container
        """

        self._container_name = self._get_container_name()

        print(colorize("info", self._header_art()))

        print(f"Container:\t{colorize('emphasis', self._container_name)}")
        print(f"Repo directory:\t{self._repo_dir}")
        print(f"Repo name is:\t{colorize('emphasis', self._repo_name)}")

        if self._mnt_dir:
            print(f"Mnt directory:\t{self._mnt_dir}")

        print(f"Jupyterlab:\t{'yes' if self._jupyter else 'no'}")

        print()
        print("Starting docker container.")

        self._container_id = self._start_docker_container(
            image_name=self._image_name,
            container_name=self._container_name,
            mnt_dir=self._mnt_dir,
            repo_dir=self._repo_dir,
            repo_name=self._repo_name,
            config=self._config
        )

        print(f"Container id: {self._container_id}")

        print(f"Running poetry install for {self._repo_name}.")
        self._install_repo()

        if self._jupyter:
            print("Creating ipykernel for installed poetry environment.")

            if self._create_ipykernel():
                notebook_url, notebook_mnt_dir = self._start_jupyterlab(
                    self._container_id
                )
                print(
                    f"JupyterLab launched from {notebook_mnt_dir}:"
                    f"\n{colorize('emphasis', notebook_url)}"
                )

        print("\n", colorize("info", ".~@ | @~" * 5), "\n")
        self._attach_to_container(self._container_id)

        print(colorize("comment", "\n** vogon destruct **"))

    def _install_repo(self):
        """ Poetry install the repo in the container and create an ipykernel for it.

            TODO: Make this function intelligently decide whether to `poetry install`
                  or `poetry update`, depending on lock file freshness. For now, if it
                  errors, try deleting poetry.lock file before starting vogon.

                  https://github.com/python-poetry/poetry/pull/1954
        """

        poetry_install_repo = (
            f"docker exec {self._container_id} "
            f"bash -c 'cd /repos/{self._repo_name}; poetry install'"
        )
        self._issue_command(poetry_install_repo, wait_for_completion=True)

    def _create_ipykernel(self) -> bool:
        """ Create an ipykernel for the installed poetry environment.

            Returns True if ipykernel exists as a poetry dependency (i.e. is installed)
            and the ipykernel was created, else returns False.
        """

        # Check for ipykernel as a poetry dependency, warn if not.
        poetry_check_for_ipykernel = (
            f"docker exec {self._container_id} "
            f"bash -c 'cd /repos/{self._repo_name}; poetry show | grep ipykernel'"
        )

        poetry_ipykernel = self._issue_command(
            poetry_check_for_ipykernel, capture_output=True
        )

        if not poetry_ipykernel:
            print(
                colorize(
                    "error",
                    (
                        "ipykernel is not one of your poetry dependencies. No "
                        "jupyterlab for you until you add it as a poetry dev dependency."
                    ),
                )
            )
            return False

        else:
            create_ipykernel = (
                f"docker exec {self._container_id} "
                f"bash -c 'cd /repos/{self._repo_name}; "
                f"poetry run python -m ipykernel install --user --name={self._repo_name}'"
            )
            self._issue_command(create_ipykernel, wait_for_completion=True)
            return True

    def _check_for_pyproject_toml(self) -> bool:
        """Throws an error if self._repo_dir does not contain a pyproject.toml file."""

        if not (self._repo_dir / "pyproject.toml").exists():
            raise Exception(
                f"No pyproject.toml file found in repo dir: {self._repo_dir}. "
                f"`vogon poet` only supports poetry-managed libraries. Don't make me "
                f"feed you to the ravenous Bugblatter Beast of Traal."
            )

    def _header_art(self) -> str:
        return "\n~@ vogon poet @~\n"