## FIXME: these tests are very repetitive in places
## and could be made more portable etc using pytest functions (for a temporary file, directory, etc)
import os
import os.path
import uuid
import shutil
import subprocess
import time

import pytest
from werkzeug.test import Client
from werkzeug.testapp import test_app as wsgi_app
from werkzeug.wrappers import BaseResponse

from wsgiwatch import *


def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()

def filename():
    return '/tmp/%s' % uuid.uuid4()
def make_client(app):
    return Client(app, BaseResponse)

@pytest.fixture
def directory(request):
    name = filename()
    os.mkdir(name)
    request.addfinalizer(lambda: shutil.rmtree(name))

    return name

@pytest.fixture
def file(request):
    name = filename()
    open(name, 'a').close()
    request.addfinalizer(lambda: os.remove(name))

    return name

@pytest.fixture
def watcher():
    return WSGIWatch(wsgi_app)

class CallChecker:
    def __init__(self): self.called = False
    def __call__(self): self.called = True
    def reset(self): self.called = False
@pytest.fixture
def builder():
    return CallChecker()


def test_without_paths(watcher):
    client = make_client(watcher)
    resp = client.get('/')

    assert resp.status_code == 200

def test_builds_first_time(watcher, file, builder):
    client = make_client(watcher)
    watcher.watch(file, builder)

    resp = client.get('/')
    assert resp.status_code == 200
    assert builder.called

def test_doesnt_build_second_time(watcher, file, builder):
    client = make_client(watcher)
    watcher.watch(file, builder)

    resp1 = client.get('/')
    builder.reset()

    resp2 = client.get('/')

    assert resp2.status_code == 200
    assert not builder.called

def test_build_with_shell_command(watcher, file, capfd):
    client = make_client(watcher)
    watcher.watch(file, 'printf "hello world"')

    resp = client.get('/')
    out, err = capfd.readouterr()

    assert resp.status_code == 200
    assert out == 'hello world'

def test_rebuild_after_file_update(watcher, file, builder):
    client = make_client(watcher)
    watcher.watch(file, builder)

    resp1 = client.get('/')
    called = False

    time.sleep(1)
    touch(file)

    resp2 = client.get('/')
    assert resp2.status_code == 200
    assert builder.called

def test_watch_directory_contents(watcher, directory, builder):
    client = make_client(watcher)
    watcher.watch(directory, builder)

    resp1 = client.get('/')
    called = False

    time.sleep(1)
    touch(os.path.join(directory, 'testfile'))

    resp2 = client.get('/')
    assert resp2.status_code == 200
    assert builder.called

def test_build_function_raises_exception(watcher, file):
    client = make_client(watcher)

    def builder():
        raise Exception
    watcher.watch(file, builder)

    with pytest.raises(Exception) as excinfo:
        resp2 = client.get('/')

def test_shell_nonzero_exit(watcher, file):
    client = make_client(watcher)
    watcher.watch(file, 'exit 1')

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        resp2 = client.get('/')

def test_glob_matches_new_file(watcher, directory, builder):
    client = make_client(watcher)

    watcher.watch(directory + '/test*', builder)
    resp1 = client.get('/')
    builder.reset()

    touch(directory + '/test1')
    resp2 = client.get('/')

    assert resp2.status_code == 200
    assert builder.called

def test_glob_matches_deleted_file(watcher, directory, builder):
    touch(directory + '/test1')
    touch(directory + '/test2')

    client = make_client(watcher)

    watcher.watch(directory + '/test*', builder)
    resp1 = client.get('/')
    builder.reset()

    os.remove(directory + '/test2')
    resp2 = client.get('/')

    assert resp2.status_code == 200
    assert builder.called

def test_glob_matches_modified_file(watcher, directory, builder):
    touch(directory + '/test1')
    client = make_client(watcher)

    watcher.watch(directory + '/test*', builder)
    resp1 = client.get('/')
    builder.reset()

    time.sleep(1)
    touch(directory + '/test1')
    resp2 = client.get('/')

    assert resp2.status_code == 200
    assert builder.called
