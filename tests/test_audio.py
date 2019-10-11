from unittest import TestCase

import rfcx
import os
from pydub import AudioSegment

class AudioTests(TestCase):
    def test_can_slice_audio(self):
        # Arrange
        duration = 2
        filename = 'tests/audio_for_slicing.csv'
        input_path = 'tests/audio'
        output_path = '/tmp/audio_for_slicing_test'
        if not os.path.exists(output_path):
            os.mkdirs(output_path)

        # Act
        rfcx.audio.csv_slice_audio(filename, output_path, input_path, slice_second=duration)

        # Assert
        labels = os.listdir(output_path)
        bark_files = os.listdir(output_path + "/bark")
        squeak_files = os.listdir(output_path + "/squeak")
        audio = AudioSegment.from_wav(output_path + "/squeak/" + squeak_files[6])
        self.assertEqual(3, len(labels))
        self.assertEqual(2, len(bark_files))
        self.assertEqual(7, len(squeak_files))
        self.assertEqual(duration, audio.duration_seconds)
        