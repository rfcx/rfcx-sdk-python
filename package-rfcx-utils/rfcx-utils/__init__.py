"""## Getting started

1. Get the latest version from [RFCx's Github releases page](https://github.com/rfcx/rfcx-sdk-python/releases)

2. Install with pip: `pip install rfcx-utils-x.x.x-py3-none-any.whl`

3. Use `import rfcx-utils`
"""

from ._textgrid import TextGrid
from .audio import save_audio_file
from .audio import praat_slice_audio
from .audio import csv_slice_audio
from .audio import csv_download
name = "rfcx-utils"
