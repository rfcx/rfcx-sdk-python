import time
import sys
from rfcxtf.validate import validate

if len(sys.argv) != 2:
    print('Usage: example-validate.py PACKAGE_PATH')
    exit(1)

model_path = sys.argv[1]
timing_start = time.time()
result = validate(model_path, 'example/guardian_audio.wav')
if result is None:
    print(f'Passed validation: {time.time() - timing_start:.3f}s')
else:
    print('Failed validation:', result)
