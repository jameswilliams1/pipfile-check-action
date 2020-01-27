#!/usr/bin/env python3
"""
Compare Pipfile.lock packages and versions against a requirements.txt.

Raises AssertionError if packages and versions do not exactly match in both.
"""
import json

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
            # Dict of {package: {version: xxx}}
            package_info = json.loads(req_file.read())["default"]
            packages = []
            for name, info in package_info.items():
                try:
                    # Standard package==version
                    packages.append(name + info["version"])
                except KeyError:
                    # Package installed from git
                    url = info["git"]
                    branch = info["ref"]
                    package = name
                    packages.append(f"git+{url}@{branch}#egg={package}")
                # TODO check if other ways of installing packages are missed
        else:
            ...
        packages.sort()  # Sanity check, should already be sorted
        return packages


if __name__ == "__main__":
    print(get_requirements("Pipfile.lock", is_piplock=True))
    # print(get_requirements("requirements.txt"))
