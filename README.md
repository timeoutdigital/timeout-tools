timeout-tools
=============

Tools for developers


Installation
------------

First, install UV if you don't have it:

```
timeout-tools uv-install
```

Or install UV manually:
- macOS: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`

Then install timeout-tools globally:

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
- Installs python version specified in repos `PYTHON_VERSION` file, using UV
- Creates a standard `.venv` virtual environment
- Installs requirements.txt (and requirements-dev.txt if it exists) using UV's fast pip
- Installs and runs `pre-commit install`

### Working with the Virtual Environment

After creating a workspace:

**Traditional activation**:
```
cd <branch_name>--<app>
source .venv/bin/activate
```

### Other Commands

- **Install UV**: `timeout-tools uv-install`
- **Setup Python environment**: `timeout-tools python-setup` (from within a repo)
- **Remove Python environment**: `timeout-tools python-remove`

### Migrating from pyenv

If you were using the old pyenv-based version:
1. Install UV: `timeout-tools uv-install`
2. Remove old pyenv virtualenvs: `pyenv virtualenv-delete <name>`
3. Use the new UV-based commands

