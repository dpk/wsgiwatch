# wsgiwatch

[![PyPI version](https://badge.fury.io/py/wsgiwatch.svg)](https://pypi.python.org/pypi/wsgiwatch)&nbsp;[![CircleCI build](https://circleci.com/gh/dpk/wsgiwatch.svg?style=shield)](https://circleci.com/gh/dpk/wsgiwatch)

So you're developing a Python web application, and you have lots of assets that need to be compiled when you change them on your development machine. You change your CoffeeScript file, and the JavaScript needs to be rebuilt; you change the SCSS or LESS and the CSS needs to change. Recompiling these things is a bore.

`wsgiwatch` to the rescue! You can tell wsgiwatch to look for changes in files and it'll call a function or run a shell command when they do, interrupting the WSGI request until everything's up-to-date. It should be safe to run on multithreaded and multiprocess servers, but the latter might behave a bit strangely due to the thing that keeps track of what files are up-to-date not being shared between processes.

Essentially, it's [LiveReload][lr] or [ServeIt][si], but as <100 lines of WSGI middleware.

Compatible with at least Python 3.4. Tested on the latest Python 2.7 but with no support plan for Python 2 going forward — if it breaks, it breaks.

[lr]: https://livereload.readthedocs.org/en/latest/
[si]: https://github.com/garybernhardt/serveit

## Usage

```python
watcher = WSGIWatch(app)
```

Once you've wrapped your WSGI app in a `WSGIWatch` instance, you can add files and directories to be watched, and the commands to be run when they change. You can also specify a glob pattern:

```python
watcher.watch('assets', 'make')
watcher.watch('assets/*.js', 'make static/bundle.js')
watcher.watch('assets/*.js', build_js_bundle)
```

Then just pass the `watcher` instance to your development HTTP server instead of the normal `app`.

### With Flask

```python
from flask import Flask
import wsgiwatch
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    # this is the wsgiwatch bit
    watcher = wsgiwatch.WSGIWatch(app.wsgi_app)
    watcher.watch('assets/js', 'make static/scripts.js')
    app.wsgi_app = watcher

    app.debug = True
    app.run()

``` 
