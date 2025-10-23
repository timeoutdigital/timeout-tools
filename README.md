timeout-tools
=============

Tools for developers


Installation
------------

```
uv tool install git+https://github.com/timeoutdigital/timeout-tools
```

or

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
- Sets up python using uv pip for `PYTHON_VERSION` or uv sync for `.python-version`
- Runs `pre-commit install`
