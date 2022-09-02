import datetime
import requests
import shutil
import os
import concurrent.futures
from rfcx._api_rfcx import stream_segments

def __save_file(url, local_path, token):
    """ Download the file from `url` and save it locally under `local_path` """
    headers = {
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers, stream=True)

    if (response.status_code == 200):
        with open(local_path, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
            print('Saved {}'.format(local_path))
    else:
        print("Can not download", url)
        reason = response.json()
        print("Reason:", response.status_code, reason["message"])

def __local_audio_file_path(path, audio_name, audio_extension):
    """ Create string for the name and the path """    
    return path + '/' + audio_name + "." + audio_extension

def __generate_date_in_isoformat(date):
    """ Generate date in iso format ending with `Z` """
    return date.replace(microsecond=0).isoformat() + 'Z'

def download_file(token, dest_path, stream_id, start_time, end_time, gain=1, file_ext='wav'):
    """ Prepare `url` and `local_path` and save it using function `__save_file` 
        Args:
            dest_path: Audio save path.
            stream_id: Stream id to get the segment.
            start_time: Minimum timestamp to get the audio.
            end_time: Maximum timestamp to get the audio. (Should not more than 15 min range)
            gain: (optional, default = 1) Input channel tone loudness
            file_ext: (optional, default = 'wav') Extension for saving audio files.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
    """
    start = __iso_to_rfcx_custom_format(__generate_date_in_isoformat(start_time))
    end = __iso_to_rfcx_custom_format(__generate_date_in_isoformat(end_time))
    audio_name = "{stream_id}_t{start_time}.{end_time}_g{gain}_f{file_ext}".format(stream_id=stream_id,
                                                                                    start_time=start,
                                                                                    end_time=end,
                                                                                    gain=gain,
                                                                                    file_ext=file_ext)
    url = "https://media-api.rfcx.org/internal/assets/streams/" + audio_name + "." + file_ext
    local_path = __local_audio_file_path(dest_path, audio_name, file_ext)
    __save_file(url, local_path, token)

def __iso_to_rfcx_custom_format(time):
    """Convert RFCx iso format to RFCx custom format"""
    return time.replace('-', '').replace(':', '').replace('.', '')

def __get_all_segments(token, stream_id, start, end):
    """Get all audio segment in the `start` and `end` time range"""
    all_segments = []
    empty_segment = False
    offset = 0

    while not empty_segment:
        # No data will return empty array from server
        segments = stream_segments(token, stream_id, start, end, limit=1000, offset=offset)
        if segments:
            all_segments.extend(segments)
            offset = offset + 1000
        else:
            empty_segment = True

    return all_segments

def __segment_download(save_path, gain, file_ext, segment, token):
    """Download audio using the core api(v2)"""
    stream_id = segment['stream']['id']
    start = __iso_to_rfcx_custom_format(segment['start'])
    end = __iso_to_rfcx_custom_format(segment['end'])
    custom_time_range = start + '.' + end
    rfcx_audio_format = "{stream_id}_t{time}_rfull_g{gain}_f{file_ext}".format(stream_id=stream_id,
                                                                                                time=custom_time_range,
                                                                                                gain=gain,
                                                                                                file_ext=file_ext)
    audio_name = "{}_{}_{}_gain{}".format(stream_id, start, segment['id'], gain)
    url = "https://media-api.rfcx.org/internal/assets/streams/" + rfcx_audio_format + "." + file_ext
    local_path = __local_audio_file_path(save_path, audio_name, file_ext)
    __save_file(url, local_path, token)

def download_file_segments(token, dest_path, stream, min_date, max_date, gain=1, file_ext='wav', parallel=True):
    """ Download RFCx audio on specific time range using `stream_segments` to get audio segments information
        and save it using function `__save_file`
        Args:
            token: RFCx client token.
            dest_path: Audio save path.
            stream: Identifies a stream/site
            min_date: Minimum timestamp to get the audio.
            max_date: Maximum timestamp to get the audio.
            gain: (optional, default= 1) Input channel tone loudness
            file_ext: (optional, default= 'wav') Extension for saving audio file.
            parallel: (optional, default= True) Enable to parallel download audio from RFCx

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
    """
    save_path = dest_path + '/' + stream
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    start = __generate_date_in_isoformat(min_date)
    end = __generate_date_in_isoformat(max_date)

    segments = __get_all_segments(token, stream, start, end)

    if segments:
        print("Downloading {} audio from {}".format(len(segments), stream))
        if(parallel):
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                futures = []
                for segment in segments:
                    futures.append(executor.submit(__segment_download, save_path, gain, file_ext, segment, token))

                futures, _ = concurrent.futures.wait(futures)
        else:
            for segment in segments:
                __segment_download(save_path, gain, file_ext, segment, token)
        print("Finish download on {}".format(stream))
    else:
        print("No data found on {} - {} at {}".format(start[:-10], end[:-10], stream))
