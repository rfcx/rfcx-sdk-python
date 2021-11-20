# Rainforest Connection SDK for Python

If you are would like to use the SDK then please [see the documentation](https://rfcx.github.io/rfcx-sdk-python/) 
or [try an example](https://gist.github.com/antonyharfield/93231b3df86cd58fecee4f4d1ec9cc5b).

This README is designed for developers who are building or contributing to the SDK.

## Setup your development environment

The easiest way (if you have Docker installed) is to first build the docker image:

`docker build -t rfcx-sdk-python .`

Then run scripts directly, for example:

`docker run -it --rm -v ${PWD}/package-rfcx:/usr/src/app rfcx-sdk-python python example.py`

Or run a terminal and execute scripts inside the container:

`docker run -it --rm -v ${PWD}/package-rfcx:/usr/src/app rfcx-sdk-python bash`

`python example.py`

(Scripts like example.py in the root directory can `import rfcx` from the source -- making it easy to develop new SDK features.)


### Packaging for distribution

*To build a new version:*

Increment the version in `package-rfcx/setup.py` and `package-rfcx-utils/setup.py`.

Create a distribution (source and wheel):

`python package-rfcx/setup.py sdist bdist_wheel`

`python package-rfcx-utils/setup.py sdist bdist_wheel`

Alternatively through docker:

`docker run -it --rm -v ${PWD}:/usr/src/app rfcx-sdk-python python package-rfcx/setup.py sdist bdist_wheel`

`docker run -it --rm -v ${PWD}:/usr/src/app rfcx-sdk-python python package-rfcx-utils/setup.py sdist bdist_wheel`

### Uploading to Python Package Index (PyPI)

First time only:

`pip install --user --upgrade twine`

Upload:

`twine upload dist/*` (or if it fails to find twine then `python -m twine upload dist/*`)

Enter your username and password.

### Testing

#### Unit tests

`docker run -it --rm -v ${PWD}:/usr/src/app rfcx-sdk-python python package-rfcx-utils/setup.py test`

#### Package tests

Simple test: `pip install --no-deps rfcx`

Better test:
- Create a new notebook/colab
- Run the following code:
    ```python
    !pip install rfcx

    import rfcx

    rfcx.name
    ```
- Result should be:
    ![Example in colab](docs/images/package-test-colab.png?raw=true)


### Building documentation

The documentation is generated from docstrings in the source code. To generate
it, run:

`docker run -it --rm -v ${PWD}:/usr/src/app rfcx-sdk-python pdoc3 --html --force --template-dir docs_src/template --output-dir docs package-rfcx/rfcx package-rfcx-utils/rfcx-utils`

To generate a PDF:

```
docker run -it --rm -v ${PWD}:/usr/src/app rfcx-sdk-python pdoc3 --pdf --force --template-dir docs_src/template package-rfcx/rfcx package-rfcx-utils/rfcx-utils > docs.md
docker run --rm -v ${PWD}:/data pandoc/latex docs.md -o docs.pdf
```
