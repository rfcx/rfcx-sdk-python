import rfcx
import datetime
import os

client = rfcx.Client()
client.authentication()

# Find the streams in the warsi site
print('\nStreams for Hulu Batang')
streams = client.streams(projects='hul95hb198is')
for stream in streams:
    print(stream['id'], stream['name'], stream['project_id'],
          stream['updated_at'])


# Helper for downloading audio between any 2 times, renames them to their timestamp
def download(stream_id, start, end, local_path, file_ext):
    if not os.path.isdir(local_path):
        os.makedirs(local_path)
    client.download_file_segments(local_path, stream_id, start, end, file_ext=file_ext)

# Download the last 10 minutes of the latest stream
selected_guardian_id = streams[0]['id']
end_time = streams[0]['updated_at']
start_time = (datetime.datetime.fromisoformat(end_time.replace("Z", "")) -
              datetime.timedelta(minutes=10)).isoformat().replace("000", "Z")
print('\nDownloading the latest 10 minutes of audio from ' +
      streams[0]['name'])
download(selected_guardian_id, start_time, end_time, 'downloaded', 'opus')

# Any detections in the last 10 minutes
print('\nChecking for detections in the same time period')
detections_in_last5mins = client.detections(
    start=start_time,
    end=end_time,
    classifications=['chainsaw', 'vehicle'],
    streams=[streams[0]],
    min_confidence=0.975)
if len(detections_in_last5mins) == 0:
    print('No detections in this time')
else:
    for detection in detections_in_last5mins:
        print(detection)
