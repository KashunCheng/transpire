import importlib
import sys
from contextvars import Context
from types import ModuleType
from typing import Iterable, List, Optional

import click
import yaml

from transpire.internal import context, render
from transpire.internal.argocd import make_app
from transpire.internal.config import (
    ClusterConfig,
    ModuleConfig,
    RemoteModuleConfig,
    load_py_module_from_file,
)
from transpire.internal.context import get_app_name


def build_to_lists(module: ModuleType) -> list[dict]:
    manifests: list[dict] = list()

    def emit_backend(objs: Iterable[dict]):
        manifests.extend(objs)

    def go():
        render._emit_backend.set(emit_backend)
        context._current_app.set(module.name)
        module.objects()

    ctx = Context()
    ctx.run(go)

    return manifests


@click.group()
def commands(**kwargs) -> None:
    """tools related to Kubernetes objects (.transpire.py)"""
    pass


@commands.command()
@click.argument("out_path", envvar="TRANSPIRE_OBJECT_OUTPUT", type=click.Path())
def build(out_path, **kwargs) -> None:
    """build objects, write them to a folder"""
    apps_manifests = {}  # build_to_lists()

    for app_name, manifests in apps_manifests.items():
        make_app(app_name)
        render.write_manifests(manifests, app_name, out_path)


@commands.command("print")
@click.argument("app_name", required=False)
def list_manifests(app_name: Optional[str] = None, **kwargs) -> None:
    """build objects, pretty-list them to stdout"""
    py_module = None
    if app_name:
        config = ClusterConfig.from_cwd()
        module = config.modules.get(app_name)

        # Failure: The module isn't in the config file.
        if not module:
            raise ModuleNotFoundError(f"Couldn't find {app_name} in cluster.toml.")
        # Failure: The module is a remote module.
        if isinstance(module, RemoteModuleConfig):
            raise ValueError(
                f"{app_name} is a remote module, you should run transpire in the remote repository instead."
            )

        py_module = module.load_py_module(app_name)
    else:
        raise NotImplementedError(
            "Need to iterate upwards to git root / fs boundary and get .transpire.py / load that."
        )

    apps_manifests = build_to_lists(py_module)
    yaml.safe_dump_all(apps_manifests, sys.stdout)


@commands.command()
def apply(**kwargs) -> None:
    """build objects, apply them to current kubernetes context"""
    raise NotImplementedError("Not yet implemented!")
