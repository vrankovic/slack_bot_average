from os import path
from .exceptions import NoConfFile


def check_path_exists_decorator(func):
    """
    This decorator is used to check if path to some file exists before
    it is passed to decorated function as an argument
    """
    def wrapper(self, file_path, *args, **kwargs):
        if not path.exists(file_path):
            raise NoConfFile
        func(self, file_path, *args, **kwargs)
    return wrapper
