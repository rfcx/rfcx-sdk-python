import datetime
import requests
import shutil
import os
import multiprocessing as mp
from functools import partial
from rfcx._api_rfcx import guardianAudio

def __save_file(url, local_path):
    """ Download the file from `url` and save it locally under `local_path` """
    response = requests.get(url, stream=True)
    if (response.status_code == 200):
        with open(local_path, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
    else:
        print("Can not download {} with status {}".format(url, response.status_code))

def __local_audio_file_path(path, audio_name, audio_extension):
    """ Create string for the name and the path """    
    return path + '/' + audio_name + "." + audio_extension

def save_audio_file(destination_path, audio_id, source_audio_extension='opus'):
    """ Prepare `url` and `local_path` and save it using function `__save_file` 
        Args:
            destination_path: Audio save path.
            audio_id: RFCx audio id.
            source_audio_extension: (optional, default= '.opus') Extension for saving audio files.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
    
    """
    url = "https://assets.rfcx.org/audio/" + audio_id + "." + source_audio_extension
    local_path = __local_audio_file_path(destination_path, audio_id, source_audio_extension)
    __save_file(url, local_path)
    print('File {}.{} saved to {}'.format(audio_id, source_audio_extension, destination_path))

def __generate_date_list_in_isoformat(start, end):
    """ Generate list of date in iso format ending with `Z` """
    delta = end - start
    dates = [(start + datetime.timedelta(days=i)).replace(microsecond=0).isoformat() + 'Z' for i in range(delta.days + 1)]
    return dates

def __segmentDownload(audio_path, file_ext, segment):
    audio_id = segment['guid']
    audio_name = "{}_{}_{}".format(segment['guardian_guid'], segment['measured_at'].replace(':', '-').replace('.', '-'), audio_id)
    url = "https://assets.rfcx.org/audio/" + audio_id + "." + file_ext
    local_path = __local_audio_file_path(audio_path, audio_name, file_ext)
    __save_file(url, local_path)

def downloadGuardianAudio(token, destination_path, guardian_id, min_date, max_date, file_ext='opus', parallel=True):
    """ Download RFCx audio on specific time range using `guardianAudio` to get audio segments information
        and save it using function `__save_file`
        Args:
            token: RFCx client token.
            destination_path: Audio save path.
            guardian_id: RFCx guardian id
            min_date: Download start date
            max_date: Download end date
            file_ext: (optional, default= '.opus') Extension for saving audio file.
            parallel: (optional, default= True) Enable to parallel download audio from RFCx

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
    
    """
    audio_path = destination_path + '/' + guardian_id
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)
    dates = __generate_date_list_in_isoformat(min_date, max_date)

    for date in dates:
        date_end = date.replace('00:00:00', '23:59:59')
        segments = guardianAudio(token, guardian_id, date, date_end, limit=1000, descending=False)

        if segments:
            if(parallel):
                pool = mp.Pool(processes=mp.cpu_count())
                func = partial(__segmentDownload, audio_path, file_ext)
                res = pool.map(func, segments)
            else:
                for segment in segments:
                    __segmentDownload(audio_path, file_ext, segment)
            print("Finish download on", guardian_id, date[:-10])
        else:
            print("No data on date:", date[:-10])