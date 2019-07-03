# RFCx (Rainforest Connection) Client SDK for Python

## Getting started

TODO: Explain how to use this package...

## Development

If you want to use docker to create a separate environment for packaging then try:

`docker run -it --rm -v "$PWD":/app -w /app tensorflow/tensorflow:latest-py3 bash`

### Packaging

First time only:

`pip install --user --upgrade setuptools`

`python setup.py register`
(not sure if this is needed)

Increment the version in `setup.py`.

To create a source distribution:

`python setup.py sdist`


### Uploading

First time only:

`pip install --user --upgrade twine`

Upload:

`twine upload dist/*` (or if it fails to find twine then `python -m twine upload dist/*`)

Enter your username and password.

### Testing

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

