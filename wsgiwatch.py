import glob
import os
import os.path
import subprocess
import time
from multiprocessing import RLock


class WSGIWatch:
    def __init__(self, app):
        self.app = app

        self.lock = RLock()
        self.paths = {}
        self.last_build_time = 0

    def watch(self, path, task):
        if os.path.isfile(path):
            self.paths[FilePath(path)] = self.task(task)
        elif os.path.isdir(path):
            self.paths[DirectoryPath(path)] = self.task(task)
        elif isinstance(path, str) and ('*' in path or '[' in path or '?' in path):
            self.paths[GlobPath(path)] = self.task(task)
        elif hasattr(path, 'last_modified') and callable(path.last_modified):
            self.paths[path] = self.task(task)

    def task(self, task):
        if callable(task):
            return task
        elif isinstance(task, str):
            def run_process():
                subprocess.check_call(task, shell=True)
            return run_process

    def __call__(self, environ, start_response):
        with self.lock:
            for path, task in self.paths.items():
                if path.last_modified() > self.last_build_time:
                    task()

        self.last_build_time = time.time()
        return self.app(environ, start_response)

class FilePath:
    def __init__(self, file):
        self.file = file

    def last_modified(self):
        return os.path.getmtime(self.file)

    def __hash__(self): return hash(self.file)

class DirectoryPath:
    def __init__(self, directory):
        self.directory = directory

    def last_modified(self):
        def mtimes():
            yield 0 # otherwise we fail on empty directories
            for subdir, subsubdirs, files in os.walk(self.directory):
                for subsubdir in subsubdirs:
                    yield os.path.getmtime(os.path.join(subdir, subsubdir))
                for file in files:
                    yield os.path.getmtime(os.path.join(subdir, file))

        return max(mtimes())

    def __hash__(self): return hash(self.directory)

class GlobPath:
    def __init__(self, pattern):
        self.pattern = pattern
        # this is a bit of a hack really
        self.last_match = []

    def last_modified(self):
        matches = glob.glob(self.pattern)
        if self.last_match != matches:
            self.last_match = matches
            return time.time()

        return max([0] + [os.path.getmtime(match) for match in matches])

    def __hash__(self): return hash(self.pattern)
