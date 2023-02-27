"""RFCx audio segment information and download"""
import datetime
import shutil
import os
import concurrent.futures
import requests
import rfcx._api_rfcx as api_rfcx


def __save_file(url, local_path, token):
    """ Download the file from `url` and save it locally under `local_path` """
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        with open(local_path, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
            print(f'Saved {local_path}')
    else:
        print('Cannot download', url)
        reason = response.json()
        print('Reason:', response.status_code, reason['message'])


def __local_audio_file_path(path, audio_name, audio_extension):
    """ Create string for the name and the path """
    return path + '/' + audio_name + '.' + audio_extension.lstrip('.')


def __generate_date_in_isoformat(date):
    """ Generate date in iso format ending with `Z` """
    return date.replace(microsecond=0).isoformat() + 'Z'


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
        segments = api_rfcx.stream_segments(token,
                                   stream_id,
                                   start,
                                   end,
                                   limit=1000,
                                   offset=offset)
        if segments:
            all_segments.extend(segments)
            offset = offset + 1000
        else:
            empty_segment = True

    return all_segments


def __download_segment(token, save_path, stream_id, start_str, file_ext):
    audio_name = stream_id + '_' + start_str.replace('.000Z', '').replace('Z', '').replace(':', '-').replace('.', '-').replace('T', '_')
    url = f'{api_rfcx.base_url}/streams/{stream_id}/segments/{start_str}/file'
    local_path = __local_audio_file_path(save_path, audio_name, file_ext)
    __save_file(url, local_path, token)
    return local_path


def download_segment(token,
                        dest_path,
                        stream_id,
                        start,
                        file_ext):
    """ Download a single audio file (segment)
        Args:
            dest_path: Audio save path.
            stream_id: Stream id to get the segment.
            start: Exact start timestamp (string or datetime).
            file_ext: Extension for saving audio files.

        Returns:
            Path to downloaded file.

        Raises:
            TypeError: if missing required arguments.
    """
    if isinstance(start, datetime.datetime):
        start = __generate_date_in_isoformat(start)
    return __download_segment(token, dest_path, stream_id, start, file_ext)


def download_segments(token,
                         dest_path,
                         stream_id,
                         min_date,
                         max_date,
                         file_ext='wav',
                         parallel=True):
    """ Download a set of audio files (segments) falling within a date range
        Args:
            token: RFCx client token.
            dest_path: Audio save path.
            stream_id: Identifies a stream/site
            min_date: Minimum timestamp to get the audio.
            max_date: Maximum timestamp to get the audio.
            file_ext: (optional, default= 'wav') Extension for saving audio file.
            parallel: (optional, default= True) Enable to parallel download audio from RFCx.

        Returns:
            None.

        Raises:
            TypeError: if missing required arguments
    """
    stream_resp = api_rfcx.stream(token, stream_id)
    if stream_resp is None:
        return

    stream_name = stream_resp['name']
    if isinstance(min_date, datetime.datetime):
        min_date = __generate_date_in_isoformat(min_date)
    if isinstance(max_date, datetime.datetime):
        max_date = __generate_date_in_isoformat(max_date)

    segments = __get_all_segments(token, stream_id, min_date, max_date)

    if segments:
        print(f'Downloading {len(segments)} audio from {stream_name}')
        save_path = dest_path + '/' + stream_name
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        if parallel:
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=100) as executor:
                futures = []
                for segment in segments:
                    futures.append(
                        executor.submit(__download_segment, token, save_path, stream_id,
                                        segment['start'], file_ext))

                futures, _ = concurrent.futures.wait(futures)
        else:
            for segment in segments:
                __download_segment(token, save_path, stream_id, segment['start'], file_ext)
        print(f'Finish download on {stream_name}')
    else:
        print(f'No data found on {min_date[:10]} - {max_date[:10]} at {stream_name}')
