import os

# TODO Work in progress!

def validate(saved_model_package_path: str) -> str:
    if not saved_model_package_path.endswith('.tar.gz'):
        return 'Package must be a .tar.gz file'
