timeout-tools
=============

Tools for developers


Installation
------------

Requires recent pip

```
sudo pip3 install -U pip
```

Install globally so its always avalible

```
sudo pip3 install git+https://github.com/timeoutdigital/timeout-tools
```

Usage
-----

- Create a workspace

```
timeout-tools ws <app_repo_name> <new_branch_name>
eg
timeout-tools ws envars TOPS-1234
```

This:

- Clones the app into `<branch_name>--<app>`
- Installs python version from repos `PYTHON_VERSION` file using pyenv
- Creates a pyenv virtualenv named `<app>-<version>`
- Installs requirements.txt and requirements-dev.txt if it exists, in the virtualenv
- Creates `.python-version` file for pyenv-virtualenv to read
- Runs `pre-commit install`
