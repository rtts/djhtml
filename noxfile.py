import nox


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session):
    session.run("python", "-m", "unittest", "discover", "-v")
