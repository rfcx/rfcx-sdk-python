import pandas as pd
import urllib.request
import shutil
import os    
import csv
import rfcx 
import math
import json
import librosa
from operator import itemgetter
from pydub import AudioSegment

def csv_download(destination_path, csv_file_name, audio_extension='opus'):
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
        raise Exception('No "{}" directory in current path.'.format(destination_path))
    if not os.path.isfile(csv_file_name):
        raise Exception('No "{}" file in current path.'.format(csv_file_name))
    if audio_extension not in ['opus', 'wav', 'json', 'png']:
        raise Exception('Audio extension should be opus, wav, json, or png. Not accept: {}'.format(audio_extension))

    csv_input = pd.read_csv(csv_file_name, header=None).values
    for i in csv_input:
        raw_name = ''.join(i)                         
        audio_id = (os.path.splitext(os.path.basename(raw_name))[0])  
        save_audio_file(destination_path, audio_id, audio_extension)

def csv_slice_audio(save_path, csv_file_name, slice_second=2):
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
    with open(csv_file_name, 'r') as f:
        reader = csv.reader(f)
        audio_info_list = list(reader)
    for info in audio_info_list:
        audio_id = info[0]
        info[1] = int(info[1])
        info[2] = int(info[2])
    full_duration = math.floor(librosa.get_duration(filename=audio_id + '.wav'))
    __slice_audio(save_path, audio_info_list, full_duration, slice_second)     

def praat_slice_audio(save_path, praat_file_name, slice_second=2):
    """ Read praat file for cutting audio.
        Args:
            praat_file_name: Name of the praat file using for cut audio.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
            FileNotFoundError: if missing required audio file.
    """
    audio_info_list = list()
    tg = rfcx.TextGrid.fromFile(praat_file_name, strict=False)
    intervals = tg[0]
    audio_id = intervals.name
    for interval in intervals:
        audio_info_list.append([audio_id, math.floor(interval.minTime), math.ceil(interval.maxTime), interval.mark])
   
    for info in audio_info_list:
        audio_id = info[0]
        info[1] = int(info[1])
        info[2] = int(info[2])

    full_duration = math.floor(librosa.get_duration(filename=audio_id + '.wav'))
    __slice_audio(save_path, audio_info_list, full_duration, slice_second)

def __slice_audio(save_path, audio_list, full_duration, slice_second):
    count = 0
    audio_save_path = save_path
    full_info = __get_audio_info(audio_list, full_duration)

    if not os.path.exists(audio_save_path):
        os.mkdir(audio_save_path)
        print("Create {} directory".format(audio_save_path))

    for info in full_info:
        audio_id, x1, x2, label = info
        duration = x2-x1
        audio = AudioSegment.from_wav(audio_id + ".wav")

        if not os.path.exists('{}/{}'.format(audio_save_path, label)):
            os.mkdir('{}/{}'.format(audio_save_path, label))
            print("Create {} directory in {} directory".format(label, audio_save_path))
        if(duration < slice_second):
            start = x1 * 1000
            stop = x2 * 1000
            audio = audio[start:stop] * slice_second
            duration = int(audio.duration_seconds)
            x1 = 0
        for i in range(duration-1):
            count = count + 1
            start = (x1+i) * 1000
            stop = (x1+(i+2)) * 1000
            print(start, stop, audio.duration_seconds, label)
            audioFragment = audio[start:stop]
            audioFragment.export('{}/{}/{}.{}.wav'.format(audio_save_path, label, audio_id, count), format="wav")
            print('File {}.{}.wav saved to {}'.format(audio_id, count, label))
    count = 0


def __save_file(url, local_path):
    """ Download the file from `url` and save it locally under `local_path` """
    with urllib.request.urlopen(url) as response, open(local_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def __local_audio_file_path(path, audio_id, audio_extension):
    """ Create string for the name and the path """    
    return path + '/' + audio_id + "." + audio_extension

def save_audio_file(destination_path, audio_id, source_audio_extension='opus'):
    """ Prepare `url` and `local_path` and save it using function `__save_file` 
        Args:
            destination_path: Path to the save directory.
            audio_id: RFCx audio id.
            source_audio_extension: (optional, default= '.opus') Extension for saving audio files.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
    
    """
    url = "https://assets.rfcx.org/audio/" + audio_id + "." + source_audio_extension
    print(url)
    local_path = __local_audio_file_path(destination_path, audio_id, source_audio_extension)
    __save_file(url, local_path)
    print('File {}.{} saved to {}'.format(audio_id, source_audio_extension, destination_path))

def __get_environment_info(audio_annotated_info, audio_full_duration):
    audio_envirnoment_info = list()
    audio_id = audio_annotated_info[0][0]

    if len(audio_annotated_info) == 1:
        audio_envirnoment_info.append([audio_id, 0, audio_full_duration, "environment"])
        return audio_envirnoment_info

    start_env_time = 0
    stop_env_time = 0

    for i in range(len(audio_annotated_info)):
        # Check if the start of annotated is 0 or not
        if(audio_annotated_info[0][1] == 0):
            start_env_time = audio_annotated_info[i][2]
            # Check if it is the last sub info or not
            if(i < len(audio_annotated_info)-1):
                stop_env_time = audio_annotated_info[i+1][1]
                # In case start time and stop time is the same ex. 2,5 5,6
                if(start_env_time < stop_env_time):
                    audio_envirnoment_info.append([audio_id, start_env_time, stop_env_time, "environment"])
            else:
                # Check if the last sub info is equal to the full duration or not
                if(audio_annotated_info[-1][2] < audio_full_duration):
                    start_env_time = audio_annotated_info[i][2]
                    stop_env_time = audio_full_duration
                    if(start_env_time < stop_env_time):
                        audio_envirnoment_info.append([audio_id, start_env_time, stop_env_time, "environment"])
        
        else:  
            stop_env_time = audio_annotated_info[i][1]
            if(start_env_time < stop_env_time):
                audio_envirnoment_info.append([audio_id, start_env_time, stop_env_time, "environment"])
            start_env_time = audio_annotated_info[i][2]
            if(i == len(audio_annotated_info)-1):
                if(audio_annotated_info[-1][2] < audio_full_duration):
                    start_env_time = audio_annotated_info[i][2]
                    stop_env_time = audio_full_duration
                    if(start_env_time < stop_env_time):
                        audio_envirnoment_info.append([audio_id, start_env_time, stop_env_time, "environment"])
    return audio_envirnoment_info

def __get_audio_info(audio_annotated_list, audio_full_duration):
    audio_environment_list = __get_environment_info(audio_annotated_list, audio_full_duration)
    full_information_list = sorted(audio_annotated_list + audio_environment_list, key=itemgetter(1))
    return full_information_list