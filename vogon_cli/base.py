import subprocess

class VogonBase:

    def __init__(self):
        pass

    def issue_command(self, command: str, capture_output: bool) -> None:
        pass

        # getoutput
        # check_output (shell=True)
        # call (shell=True)


class VogonExplorer:
    def __init__(self):
        pass

class VogonPoet:

    def __init__(self, repo_dir: str, jupyterlab: bool, mnt_dir: str):
        pass