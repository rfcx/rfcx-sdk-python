"""## Getting started

1. Get the latest version from [RFCx's Github releases page](https://github.com/rfcx/rfcx-sdk-python/releases)

2. Install with pip: `pip install rfcx-x.x.x-py3-none-any.whl`

3. Use `import rfcx` and [try an example](https://gist.github.com/antonyharfield/93231b3df86cd58fecee4f4d1ec9cc5b)
"""

from ._textgrid import TextGrid
from .audio import save_audio_file
from .audio import praat_slice_audio
from .audio import csv_slice_audio
from .audio import csv_download
from .client import Client
name = "rfcx"
