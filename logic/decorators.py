from os import path
from .exceptions import NoConfFile


def check_path_exists_decorator(func):
    def wrapper(self, file_path, *args, **kwargs):
        if not path.exists(file_path):
            raise NoConfFile
        else:
            func(self, file_path, *args, **kwargs)
    return wrapper