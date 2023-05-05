import logging
logging.getLogger("tensorflow").setLevel(logging.WARNING)

import numpy as np
import tensorflow as tf
from .utils.io import read_wav
from .utils.exceptions import UnexpectedAudioFormat
from .utils.postprocessor import map_to_classes
from .ClassifierBase import ClassifierBase, DETECTIONS

## Throw an exception if TF is less than 2
if tf.__version__ < "2.0.0":
    raise Exception("Incompatible TensorFlow version (need 2.0 or greater)")

class ClassifierTF2(ClassifierBase):

    def __init__(self, saved_model_path, step_seconds=None):
        self._module = tf.saved_model.load(saved_model_path)

        # Gets model expectations, usually once to know if you need to resample.
        metadata_fn = self._module.signatures["metadata"]
        metadata = metadata_fn()

        self._sample_rate = int(metadata["input_sample_rate"])
        self._context_width_samples = int(metadata["context_width_samples"])
        self._class_names = [name.numpy().decode("utf-8") for name in metadata["class_names"]]
        if step_seconds is None:
            self._step_samples = int(self._context_width_samples)
        else:
            self._step_samples = int(float(self._sample_rate) * step_seconds)
        self._codec = 'pcm_s24le'

        # Keeps references to input/output Tensors of scoring signature.
        self._score_fn = self._module.signatures["score"]

    @property
    def score_output(self):
        return DETECTIONS

    @property
    def class_names(self):
        return self._class_names

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def window_duration(self):
        return float(self._context_width_samples) / self._sample_rate
    
    @property
    def window_step(self):
        return float(self._step_samples) / self._sample_rate

    @property
    def codec(self):
        return self._codec

    def score(self, filename):
        # Reads WAV file.
        data, sample_rate = read_wav(filename)
        if sample_rate != self._sample_rate:
            raise UnexpectedAudioFormat()

        # Prepares feed for waveform input Tensor.
        batch_size = 1
        num_channels = 1
        waveform_values = np.array(data, dtype=np.float32).reshape(
            (batch_size, len(data), num_channels))

        # Calls TensorFlow scoring.
        score_values = next(iter(self._score_fn(
            waveform=tf.constant(waveform_values),
            context_step_samples=tf.constant(self._step_samples, tf.int64),
        ).values())).numpy()

        return map_to_classes(score_values, self._class_names)
