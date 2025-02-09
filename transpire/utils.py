import pathlib
import tomllib
from typing import Dict, cast


def get_file(caller, filename: str) -> pathlib.Path:
    """
    Given the __file__ parameter of the calling file and
    the filename of an adjacent file, return the path to
    that file.
    """
    return pathlib.Path(caller).parent.resolve() / filename


def get_versions(caller) -> Dict[str, Dict[str, str]]:
    """
    Given the __file__ parameter of the calling file, return
    the contents of versions.toml cast to a dict.
    """
    file = get_file(caller, "versions.toml")

    return cast(
        Dict[str, Dict[str, str]],
        tomllib.loads(file.read_text()),
    )
