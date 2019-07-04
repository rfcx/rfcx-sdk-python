import pandas as pd
import json
import urllib.request
import shutil
import os     

def csv_download(path, csv_file_name, audio_extension):
    csv_input = pd.read_csv('audio_urls.csv').values
    for i in csv_input:
        raw_name = ''.join(i)                           # include https: link
        audio_id = (os.path.splitext(os.path.basename(raw_name))[0])   
        __save_audio_file(path, audio_id, audio_extension)

def __save_file(url, local_path):
    # Download the file from `url` and save it locally under `local_path`:
    with urllib.request.urlopen(url) as response, open(local_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def __local_audio_file_path(path, audio_id, audio_extension):
    return path + '/' + audio_id + "." + audio_extension

def __save_audio_file(path, audio_id, source_audio_extension):
    url = "https://assets.rfcx.org/audio/" + audio_id + "." + source_audio_extension
    local_path = __local_audio_file_path(path, audio_id, source_audio_extension)
    __save_file(url, local_path)
    print('File saved to ' + local_path)

# [[audio_name, class], [audio_name, class], ...]

# def json_read(json_file_name):
#     reader = json.loads(json_file_name)
#     json_list = list()
#     for key in reader:
#         json_list.append([key, reader[key]])
#     return json_list

# input: {{audio_name: class}, {audio_name: class}, ...}
# output: [[audio_name, class], [audio_name, class], ...]
# json_here = '{"x": 1, "x": 2, "x": 3}'
# print(json_read(json_here))