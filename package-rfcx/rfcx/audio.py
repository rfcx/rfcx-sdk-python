import datetime
import requests
import shutil
import os
import concurrent.futures
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

def __generate_date_in_isoformat(date):
    """ Generate date in iso format ending with `Z` """
    return date.replace(microsecond=0).isoformat() + 'Z'

def __get_all_segments(token, guardian_id, start, end):
    all_segments = []
    empty_segment = False
    offset = 0

    while not empty_segment:
        # No data will return `None` from server
        segments = guardianAudio(token, guardian_id, start, end, limit=1000, offset=offset, descending=False)
        if segments:
            all_segments.extend(segments)
            offset = offset + 1000
        else:
            empty_segment = True

    return all_segments

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

    start = __generate_date_in_isoformat(min_date)
    end = __generate_date_in_isoformat(max_date)

    segments = __get_all_segments(token, guardian_id, start, end)

    if segments:
        print("Downloading {} audio from {}".format(len(segments), guardian_id))
        if(parallel):
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                futures = []
                for segment in segments:
                    futures.append(executor.submit(__segmentDownload, audio_path=audio_path, file_ext=file_ext, segment=segment))

                futures, _ = concurrent.futures.wait(futures)
        else:
            for segment in segments:
                __segmentDownload(audio_path, file_ext, segment)
        print("Finish download on {}".format(guardian_id))
    else:
        print("No data found on {} - {} at {}".format(start[:-10], end[:-10], guardian_id))
