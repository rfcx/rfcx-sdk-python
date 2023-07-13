import os
import numpy as np
import tarfile
import tempfile
import tensorflow as tf
from typing import Optional
from .utils.io import read_wav

def validate(saved_model_package_path: str) -> Optional[str]:
    # Must have tar.gz extension
    if not saved_model_package_path.endswith('.tar.gz'):
        return 'Package must be a .tar.gz file'
    
    # Must be able to extract tar.gz
    temp_folder = tempfile.mkdtemp()
    try:
        tar = tarfile.open(saved_model_package_path, "r:gz")
        tar.extractall(path=temp_folder)
        tar.close()
    except:
        return 'Package must be a valid/extractable .tar.gz file'

    # Must have a model folder in the package
    saved_model_path = os.path.join(temp_folder, 'model')
    if not os.path.exists(saved_model_path):
        return 'Extracted package must contain a folder named model'
    
    # Must be a saved model
    try:
        model = tf.saved_model.load(saved_model_path)
    except:
        return 'Extracted model folder must be in SavedModel format'

    # Metadata exists
    if 'metadata' not in model.signatures:
        return 'Model must contain `metadata` signature'
    
    # Metadata is in correct format
    metadata = model.signatures['metadata']()
    if 'input_sample_rate' not in metadata or metadata['input_sample_rate'].get_shape() != () or not metadata['input_sample_rate'].dtype.is_floating:
        return 'Signature `metadata` must contain `input_sample_rate` and be a float'
    if 'context_width_samples' not in metadata or metadata['context_width_samples'].get_shape() != () or not metadata['context_width_samples'].dtype.is_integer:
        return 'Signature `metadata` must contain `context_width_samples` and be an integer'
    if 'class_names' not in metadata or len(metadata['class_names'].get_shape()) != 1 or metadata['class_names'].dtype.name != 'string':
        return 'Signature `metadata` must contain `class_names` and be a 1-dim array of strings'

    # Score signature exists
    if 'score' not in model.signatures:
        return 'Model must contain `score` signature'
    
    # Score input
    score_fn = model.signatures['score']
    input_signature = score_fn.structured_input_signature[1]
    if len(input_signature) != 2 or 'context_step_samples' not in input_signature or 'waveform' not in input_signature:
        return 'Signature `score` must have 2 inputs, `context_step_samples` and `waveform`'
    waveform_shape = input_signature['waveform'].shape
    if waveform_shape[1] != None or waveform_shape[2] != 1:
        return 'Input `waveform` must have shape (?, None, 1)'

    # Score output
    if len(score_fn.outputs[0].get_shape()) != 3:
        return 'Signature `score` must have 1 output as a 3-element tuple'
    (expected_classes,) = metadata['class_names'].get_shape()
    (_, _, actual_classes) = score_fn.outputs[0].get_shape()
    if expected_classes != actual_classes:
        return 'Length of `class_names` in `metadata` must match size of `score` output'

    # Can score an input
    data, _ = read_wav('example/guardian_audio.wav')
    waveform_values = np.array(data, dtype=np.float32).reshape((1, len(data), 1)) 
    try:
        _ = next(iter(score_fn(
            waveform=tf.constant(waveform_values),
            context_step_samples=tf.constant(int(metadata['input_sample_rate']), tf.int64),
        ).values())).numpy()
    except Exception as e:
        return 'Score function should return results'

    # Looks good
    return None
