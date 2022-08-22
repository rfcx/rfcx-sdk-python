import rfcx
import os

client = rfcx.Client()
client.authentication()

def download(stream_id, start, end, local_path, file_ext):
    if not os.path.isdir(local_path):
        os.makedirs(local_path)
    client.download_file_segments(local_path, stream_id, start, end, file_ext=file_ext)

puerto_rico_ra11 = '4GhAqNg3k9D8'

print('\nAudio for Puerto Rico RA 11 at 11:00 - 13:00 on 01 Jan 2022')
download(puerto_rico_ra11, '2022-01-01T11:00:00.000Z', '2022-01-01T12:59:59.999Z', 'ra11', 'wav')
