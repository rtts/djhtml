import nox


@nox.session(name="lint-isort")
def lint_isort(session):
    session.install("isort==5.8.0")
    session.run("python", "-m", "isort", ".")


@nox.session(name="lint-black")
def lint_black(session):
    session.install("black==21.5b0")
    session.run("python", "-m", "black", ".")


@nox.session(name="lint-flake8")
def lint_flake8(session):
    session.install("flake8==3.9.1")
    session.run("python", "-m", "flake8", ".")


@nox.session(python=["3.6", "3.7", "3.8", "3.9"])
def tests(session):
    session.run("python", "-m", "unittest", "discover", "-v")
