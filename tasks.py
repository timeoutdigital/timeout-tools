from invoke import task


@task
def python_build_requirements(ctx):
    ctx.run("pip-compile --resolver=backtracking")
    ctx.run("pip install -r requirements.txt")


@task
def python_upgrade_requirements(ctx):
    ctx.run("pip-compile --resolver=backtracking -U")
    ctx.run("pip install -r requirements.txt")
