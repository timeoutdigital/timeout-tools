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

If you're running a DA app and are having trouble with timeout-tools installing, please check [this guide](https://timeoutgroup.atlassian.net/wiki/spaces/TD/pages/3220537347/Run+a+Data+App+for+the+first+time).

Usage
-----

- Create a workspace

```
timeout-tools ws <app_repo_name> <branch_name>
eg
timeout-tools ws envars TOPS-1234
```

This:

- Clones the app into `<branch_name>--<app>`
- Checkout branch `<branch_name>` if it exists or creates it
- Installs python version specified in repos `PYTHON_VERSION` file, using pyenv
- Creates a pyenv virtualenv named `<app>-<version>`
- Installs requirements.txt (and requirements-dev.txt if it exists) in the virtualenv
- Creates `.python-version` file for pyenv-virtualenv to read
- Runs `pre-commit install`
