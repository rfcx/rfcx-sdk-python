import rfcx
import os

client = rfcx.Client()
client.authenticate()

local_path = 'audio'
if not os.path.isdir(local_path):
    os.makedirs(local_path)

stream_id = '4GhAqNg3k9D8' # Puerto Rico - RA11

any_segment = client.stream_segments(stream=stream_id, start='2022-01-01T11:00:00.000Z', end='2023-01-01T11:00:00.000Z')[0]
expected_file_extension = any_segment['file_extension']

client.download_segments(stream_id, local_path, '2022-04-17T11:00:00.000Z', '2022-04-18T23:59:59.999Z', expected_file_extension)

