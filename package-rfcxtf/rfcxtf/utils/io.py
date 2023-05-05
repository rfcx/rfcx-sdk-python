import numpy as np
import pysndfile
from .exceptions import UnexpectedAudioFormat

def read_wav(filename):
    data, sample_rate, _ = pysndfile.sndio.read(filename, dtype=np.float32)
    if data.ndim != 1:
        raise UnexpectedAudioFormat()
    return data, sample_rate