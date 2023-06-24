"""
Install Polars dependencies as defined in pyproject.toml without building Polars.

In our dev workflow, we often want to either not build (Rust) Polars at all, or in
develop mode. Unfortunately, `pip install .` or `pip install . -e` will always call
`maturin build` to build Polars. This is very slow compared to `maturin develop`.
We work around this by calling `maturin develop`, and for the Python dependencies,
this script collects the relevant tags from pyproject.toml and pass to `pip install`.
"""

import argparse
import subprocess
import sys
from itertools import chain
from typing import Any

import tomllib


def parse_toml_file(fp) -> dict[str, dict[str, Any]]:
    if sys.version_info < (3, 11):
        subprocess.run(["pip", "install", "tomli"], capture_output=True, text=True)
        import tomlli

        return tomlli.load(fp)
    else:
        return tomllib.load(fp)


def collect_dependencies_from_pyproject_toml(tag: str | None = None, include_mandatory: bool = True) -> list[str]:
    """
    Collects all dependencies, mandatory and optional, from pyproject.toml.

    Parameters
    ----------
    tag
        Select only dependencies under this tag defined in optional-dependencies
    include_mandatory
        Whether to return dependencies specified under `dependencies` in pyproject.toml.

    """
    with open("pyproject.toml", mode="rb") as fp:
        config = parse_toml_file(fp)

    if tag:
        deps = []
        if "," in tag:
            for t in tag.split(","):
                deps += config["project"]["optional-dependencies"][t]
        else:
            deps += config["project"]["optional-dependencies"][tag]
        if include_mandatory:
            deps += config["project"]["dependencies"]
    else:
        # collect everything
        mandatory_deps = config["project"]["dependencies"]
        opt_deps = list(chain(*config["project"]["optional-dependencies"].values()))
        deps = mandatory_deps + opt_deps

    return deps


def pip_install(specifiers: list[str]) -> None:
    cmd = ["pip", "install"] + specifiers
    subprocess.run(cmd, capture_output=False, text=True)


def install_dependencies(tag: str | None = None):
    deps = collect_dependencies_from_pyproject_toml(tag)

    # remove polars to avoid building
    deps_no_polars = list(filter(lambda x: not x.startswith("polars"), deps))

    pip_install(deps_no_polars)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install Polars dependencies from pyproject.toml without building Polars"
    )
    parser.add_argument(
        "--tag", type=str, help="Optional-dependency tag(s) in pyproject.toml. Provide multiple by separating with commas."
    )
    parser.add_argument("--include_mandatory", type=bool, default=True, help="Include mandatory dependencies")
    args = parser.parse_args()
    install_dependencies(args.tag)
