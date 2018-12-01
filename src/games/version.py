import os

_version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.txt')
_version = None


class IncorrectVersion(Exception):
    pass


def get_version():
    global _version
    if not _version:
        _version = _read_version()

    return _version


def _read_version():
    with open(_version_file) as version_file:
        v = version_file.readline().strip()

    if v:
        return v
    raise IncorrectVersion("Incorrect version of application")
