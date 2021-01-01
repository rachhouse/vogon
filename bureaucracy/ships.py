import pathlib
import random
import subprocess
from datetime import datetime
from typing import Optional, Tuple

from bureaucracy.names import VOGON_DESCRIPTORS, VOGON_NOUNS
from bureaucracy.output import colorize

DEFAULT_PYTHON_VERSION = "3.8"


class VogonBase:
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

        if wait_for_completion:
            subprocess.call([command], shell=True)
        elif multiline and capture_output:
            return subprocess.check_output(command, shell=True).decode("utf-8")
        else:
            output = subprocess.getoutput(command)

            if capture_output:
                return output

    def _get_container_name(self) -> str:
        """ Return a randomly generated vogon-flavor docker container name. """
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
    ) -> str:
        """ Start a docker container with `docker run` using input args.

            Args:
                image_name: str name of docker image to use for started container
                container_name: str name to use for started container
                mnt_dir: path of directory to mount to docker /mnt
                repo_dir: path of repo to mount to docker /repos/repo_name
                repo_name: str name of repo (final folder in repo_dir path)

            Returns:
                container_id: str id of started container
        """

        # Assemble flag strings to mount mnt_dir and repo_dir as docker volumes.
        repo_volume = f"-v {repo_dir}:/repos/{repo_name} \\" if repo_dir else "\\"
        mnt_volume = f"-v {mnt_dir}:/mnt \\" if mnt_dir else "\\"

        start_docker_container = """
            docker run -it -d --rm \
                --name {container_name} \
                --env CONTAINER_NAME={container_name} \
                -p 8888:8888 \
                {add_repo_volume}
                {add_mnt_volume}
                {image_name} \
                bash
        """.format(
            container_name=container_name,
            add_repo_volume=repo_volume,
            add_mnt_volume=mnt_volume,
            image_name=image_name,
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

        start_jupyterlab = """
            docker exec -d {} \
            bash -c 'jupyter lab --ip=0.0.0.0 --no-browser --allow-root'
        """.format(
            container_id
        )

        self._issue_command(start_jupyterlab)

        tries, notebook_url, notebook_mnt_dir = 0, None, None

        while (notebook_url is None) and (tries < 3):
            get_jupyterlab_url = (
                f"docker exec {container_id} bash -c 'jupyter notebook list'"
            )

            running_notebooks = self._issue_command(
                get_jupyterlab_url, capture_output=True, multiline=True
            )

            running_notebooks = running_notebooks.split("\n")
            if running_notebooks[1]:
                # also check if url matches expected pattern
                notebook_url, notebook_mnt_dir = running_notebooks[1].split(" :: ")

            tries += 1

        if notebook_url is None:
            raise Exception("Unable to launch jupyterlab.")

        return notebook_url, notebook_mnt_dir


class VogonPoet(VogonBase):
    def __init__(
        self,
        docker_image_name: str,
        repo_dir: str,
        mnt_dir: Optional[str] = None,
        start_jupyter_lab: bool = False,
        python_version: str = DEFAULT_PYTHON_VERSION,
    ):

        self._image_name = docker_image_name
        self._mnt_dir = self._get_absolute_path(mnt_dir)
        self._repo_dir = self._get_absolute_path(repo_dir)
        self._repo_name = self._repo_dir.parts[-1]

        self._jupyter = start_jupyter_lab
        self._python_version = python_version

        self._check_for_pyproject_toml()

    def run(self):

        print(colorize("info", self._header_art()))

        print(f"Repo directory:\t{self._repo_dir}")
        print(f"Repo name is:\t{self._repo_name}")

        if self._mnt_dir:
            print(f"Mnt directory:\t{self._mnt_dir}")

        print(f"Python version:\t{self._python_version}")
        print(f"Jupyterlab:\t{'yes' if self._jupyter else 'no'}")

        print()
        print("Starting docker container.")
        self._container_name = self._get_container_name()

        self._container_id = self._start_docker_container(
            image_name=self._image_name,
            container_name=self._container_name,
            mnt_dir=self._mnt_dir,
            repo_dir=self._repo_dir,
            repo_name=self._repo_name,
        )

        print(f"Container id: {self._container_id}")

        print(f"Running poetry install for {self._repo_name} and creating ipykernel.")
        self._install_repo()

        if self._jupyter:
            notebook_url, notebook_mnt_dir = self._start_jupyterlab(self._container_id)
            print(f"JupyterLab launched from {notebook_mnt_dir}:\n{notebook_url}")

        print("\n", colorize("info", ".~@ | @~" * 5), "\n")
        self._attach_to_container(self._container_id)

        print(colorize("comment", "\n** vogon destruct **"))

    def _install_repo(self):
        """ Poetry install the repo in the container and create an ipykernel for it.
        
            TODO: Make this function intelligently decide whether to `poetry install` 
                  or `poetry update`, depending on lock file freshness. For now, if it
                  errors, try deleting poetry.lock file before starting vogon.
        """

        poetry_install_repo = f"docker exec {self._container_id} bash -c 'cd /repos/{self._repo_name}; poetry install'"
        self._issue_command(poetry_install_repo, wait_for_completion=True)

        create_ipykernel = f"docker exec {self._container_id} bash -c 'cd /repos/{self._repo_name}; poetry run python -m ipykernel install --user --name={self._repo_name}'"
        self._issue_command(create_ipykernel, wait_for_completion=True)

    def _check_for_pyproject_toml(self) -> bool:
        """ Throws an error if self._repo_dir does not contain a pyproject.toml file. """

        if not (self._repo_dir / "pyproject.toml").exists():
            raise Exception(
                f"No pyproject.toml file found in repo dir: {self._repo_dir}. `vogon poet` only supports poetry-managed libraries."
            )

    def _header_art(self) -> str:
        return "\n~@ vogon poet @~\n"


class VogonExplorer(VogonBase):
    def __init__(
        self,
        docker_image_name: str,
        mnt_dir: Optional[str] = None,
        start_jupyter_lab: bool = False,
        python_version: str = DEFAULT_PYTHON_VERSION,
    ):
        super().__init__(
            docker_image_name=docker_image_name,
            mnt_dir=mnt_dir,
            start_jupyter_lab=start_jupyter_lab,
            python_version=python_version,
        )

    def _header_art(self) -> str:
        return "\n~@ vogon explorer @~\n"
