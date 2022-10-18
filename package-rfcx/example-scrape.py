import rfcx
import os

client = rfcx.Client()
client.authenticate()

def download(stream_id, start, end, local_path, file_ext):
    if not os.path.isdir(local_path):
        os.makedirs(local_path)
    client.download_audio_files(local_path, stream_id, start, end, file_ext=file_ext)

PUERTO_RICO_RA11 = '4GhAqNg3k9D8'

print('\nAudio for Puerto Rico RA 11 at 11:00 - 13:00 on 01 Jan 2022')
download(PUERTO_RICO_RA11, '2022-01-01T11:00:00.000Z', '2022-01-01T12:59:59.999Z', 'ra11', 'wav')
