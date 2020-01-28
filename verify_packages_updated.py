#!/usr/bin/env python3
"""
Compare Pipfile.lock packages and versions against a requirements.txt.

Raises AssertionError if packages and versions do not exactly match in both.
"""
import json
import re

"""
Copyright 2020 James Williams

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


def get_requirements(file_path: str, is_piplock: bool = False):
    """Return a requirements.txt or Pipfile.lock as a list.

    Pipfile.lock files are parsed and returned in requirements.txt format.
    """
    with open(file_path) as req_file:
        if is_piplock:
            # Dict of {package: {version: xxx ...}}
            package_info = json.loads(req_file.read())["default"]
            packages = []
            for name, info in package_info.items():
                try:
                    # Standard 'package[extras]==version ; markers'
                    package = name
                    if info.get("extras"):
                        package += f"[{','.join(info['extras'])}]"
                    package += info["version"]
                    if info.get("markers"):
                        package += f" ; {info['markers']}"
                    packages.append(package)
                except KeyError:
                    # Package installed from git
                    url = info["git"]
                    branch = info["ref"]
                    egg = name  # TODO raises NameError if used directly?
                    # TODO the egg may be incorrect here in certain cases
                    # TODO branch may be undefined
                    packages.append(f"git+{url}@{branch}#egg={egg}")
                # TODO check if other ways of installing packages are missed
        else:
            # Could possibly contain lines such as '-i https://pypi.org/simple'
            all_lines = req_file.read().splitlines()
            # Match anything that is either a normal or git installed package
            is_package = re.compile(r"[A-Za-z0-9-\[\]]+==\d+|git\+[htps]+.+")
            packages = [line for line in all_lines if is_package.match(line)]

        packages.sort()  # Sanity check, should already be sorted
        return packages


if __name__ == "__main__":
    lockfile = get_requirements("Pipfile.lock", is_piplock=True)
    pip = get_requirements("requirements.txt")
    print(list(set(lockfile) - set(pip)))
    print(list(set(pip) - set(lockfile)))
