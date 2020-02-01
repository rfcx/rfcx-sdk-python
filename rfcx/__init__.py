"""## Installation guide:

    1. Using `python setup.py bdist_wheel` inside the directory to generate the `.whl` file

    2. After got the `.whl`, it can install using `pip install rfcx-x.x.x-py3-none-any.whl`
"""

name = "rfcx"

from .client import Client
from .audio import csv_download
from .audio import csv_slice_audio
from .audio import praat_slice_audio
from .audio import save_audio_file
from ._textgrid import TextGrid
