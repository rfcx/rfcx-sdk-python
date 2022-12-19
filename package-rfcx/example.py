import rfcx
import datetime

client = rfcx.Client()
client.authenticate()

dest_path = './audio'

# 1. Find some sites (streams)
project_id = 'n9nrlg45vyf0' # Puerto Rico Island-Wide
streams = client.streams(projects=[project_id], include_public=True, fields=['id','name','start'])
if len(streams) == 0:
    print('No streams found')
    exit(1)

for stream in streams[:5]:
    print('**', stream['id'], stream['name'], '**')

    # 2. Get the recordings (stream segments)
    start = datetime.datetime.strptime(stream['start'][0:10], "%Y-%m-%d")
    segments = client.stream_segments(stream=stream['id'], start=start,
                                    end=start.replace(hour=23, minute=59, second=59, microsecond=999999))
    
    print(f'Found {len(segments)} segments:')
    for segment in segments[:5]:
        print(segment['start'])
    if len(segments) > 5:
        print(f'...and {len(segments)-5} more.')

    # 3. Download the recordings
    for segment in segments:
        client.download_segment(stream['id'], dest_path, segment['start'], segment['file_extension'])

