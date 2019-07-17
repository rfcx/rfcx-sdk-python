import pandas as pd
import urllib.request
import shutil
import os    
import csv 
from pydub import AudioSegment

def csv_download(destination_path, csv_file_name, audio_extension='.opus'):
    """ Read csv file for downloading audio from RFCx in user format supported: wav, opus, png, etc.
        Args:
            destination_path: Path to the save directory.
            csv_file_name: Name of the csv file using for download audio.
            audio_extension: (optional, default= '.opus') Extension for saving audio files.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
    """

    if not os.path.exists(destination_path):  
        raise Exception('No "{}" directory.'.format(destination_path))
    if not os.path.isfile(csv_file_name):
        raise Exception('No "{}" file in this directory.'.format(csv_file_name))
    if audio_extension not in ['.opus', '.wav', '.json', '.png']:
        raise Exception('Audio extension should be opus, wav, json, or png. Not accept: {}'.format(audio_extension))

    csv_input = pd.read_csv(csv_file_name).values
    for i in csv_input:
        raw_name = ''.join(i)                         
        audio_id = (os.path.splitext(os.path.basename(raw_name))[0])  
        __save_audio_file(destination_path, audio_id, audio_extension)

def csv_slice_audio(csv_file_name):
    """ Read csv file for cutting audio.
        Args:
            csv_file_name: Name of the csv file using for cut audio.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
            FileNotFoundError: if missing required audio file.
    """
    audio_info_list = list()
    count = 0
    with open(csv_file_name, 'r') as f:
        reader = csv.reader(f)
        audio_info_list = list(reader)
    for info in audio_info_list:
        audio_id = info[0]
        start = int(info[1]) * 1000
        stop = int(info[2]) * 1000
        label = info[3]
        if not os.path.exists(label):  
            os.mkdir(label)
            print('Success create {} directory'.format(label))
        newAudio = AudioSegment.from_wav(audio_id + '.wav')
        newAudio = newAudio[start:stop]
        newAudio.export('{}\\{}.{}.wav'.format(label, audio_id, count), format="wav")
        print('File {}.{}.wav saved to {}'.format(audio_id, count, label))
        count = count + 1        

def __save_file(url, local_path):
    """ Download the file from `url` and save it locally under `local_path` """
    with urllib.request.urlopen(url) as response, open(local_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def __local_audio_file_path(path, audio_id, audio_extension):
    """ Create string for the name and the path """    
    return path + '/' + audio_id + "." + audio_extension

def __save_audio_file(destination_path, audio_id, source_audio_extension):
    """ Prepare `url` and `local_path` and save it using function `__save_file` """
    url = "https://assets.rfcx.org/audio/" + audio_id + "." + source_audio_extension
    local_path = __local_audio_file_path(destination_path, audio_id, source_audio_extension)
    __save_file(url, local_path)
    print('File {}.{} saved to {}'.format(audio_id, source_audio_extension, destination_path))