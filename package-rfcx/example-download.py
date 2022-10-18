from random import choice
import rfcx
import datetime
import os
from dateutil import parser

client = rfcx.Client()
client.authenticate()

# Find the streams in the Puerto Rico
print('\nStreams for Puerto Rico')
streams = client.streams(projects='n9nrlg45vyf0')
for stream in streams:
    print(stream['id'], stream['name'], stream['project_id'],
          stream['updated_at'])


# Helper for downloading audio between any 2 times
def download(stream_id, dest_path, start_date, end_date, file_ext, parallel=False):
    client.download_audio_files(stream_id,
                                dest_path,
                                min_date=start_date,
                                max_date=end_date,
                                file_ext=file_ext,
                                parallel=parallel)


# Download the last 10 days of the latest stream
stream = streams[-1]
max_date = parser.parse(stream['updated_at']).replace(microsecond=0, tzinfo=None)
min_date = max_date - datetime.timedelta(days=10)
print(stream['updated_at'], max_date, min_date)
print(f'\nDownloading the latest 10 days of audio from {stream["name"]}')
download(stream['id'], 'downloaded', min_date, max_date, 'opus')

# Any detections in the last 10 minutes
print('\nChecking for detections in the same time period')
detections_in_last10days = client.detections(
    min_date=min_date,
    max_date=max_date,
    classifications=['chainsaw', 'vehicle'],
    streams=[streams[0]],
    min_confidence=0.975)
if len(detections_in_last10days) == 0:
    print('No detections in this time')
else:
    for detection in detections_in_last10days:
        print(detection)
