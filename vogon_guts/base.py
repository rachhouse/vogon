import subprocess
import pathlib
import random
from datetime import datetime

from typing import Optional, Tuple
from vogon_guts.output import colorize
from vogon_guts.names import VOGON_DESCRIPTORS, VOGON_NOUNS

DEFAULT_PYTHON_VERSION = "3.8"


class VogonBase:
    def __init__(
        self,
        docker_image_name: str,
        mnt_dir: Optional[str] = None,
        start_jupyter_lab: bool = False,
        python_version: str = DEFAULT_PYTHON_VERSION,
    ):
        self._image_name = docker_image_name

        if mnt_dir:
            self._mnt_dir = pathlib.Path(mnt_dir).absolute()
        else:
            self._mnt_dir = None

        self._jupyter = start_jupyter_lab
        self._python_version = python_version

    def _get_container_name(self) -> str:
        """Return a randomly generated vogon-flavor docker container name."""
        random.seed(datetime.now())
        return "{}_{}".format(
            random.choice(VOGON_DESCRIPTORS.split()), random.choice(VOGON_NOUNS.split())
        )

    def run(self):
        print(colorize("info", self.header_art_()))
        print(self._get_container_name())

    def _start_docker_container(self):
        pass

    def issue_command(self, command: str, capture_output: bool) -> None:
        pass

        # getoutput
        # check_output (shell=True)
        # call (shell=True)


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

    def header_art_(self) -> str:
        return "\n~@ vogon explorer @~\n"


class VogonPoet(VogonBase):
    def __init__(
        self,
        docker_image_name: str,
        repo_dir: str,
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

        self._repo_dir, self._repo_name = self._parse_repo(repo_dir)
        self._check_for_pyproject_toml()

    def _parse_repo(self, repo_dir: str) -> Tuple[str, str]:
        repo_filepath = pathlib.Path(repo_dir).absolute()
        repo_name = repo_filepath.parts[-1]
        return repo_filepath, repo_name

    def _check_for_pyproject_toml(self) -> bool:
        """Check that a pyproject.toml file exists in the root repo dir."""
        # TODO: Do this!
        return True

    def header_art_(self) -> str:
        return "\n~@ vogon poet @~\n"
