import requests
import time
import os

# POST
def _generate_signed_url(token, upload_url, stream_id, filename, timestamp):
    headers = {'Authorization': 'Bearer ' + token}
    data = {'filename': filename, 'timestamp': timestamp, 'stream': stream_id}
    resp = requests.post(upload_url, headers=headers, data=data, timeout=90)
    return resp.json() if (resp.status_code == 200) else None

# PUT
def _ingest_to_rfcx(token, upload_url, signed_url, filepath):
    file_ext = filepath.split('.')[-1]
    headers = {'Content-Type': 'audio/' + file_ext}
    resp = {}
    with open(filepath, 'rb') as data:
        resp = requests.put(signed_url, data=data, headers=headers, timeout=120)

    return resp.json() if (resp.status_code == 200) else None

# GET
def _get_file_status(token, upload_url, upload_id):
    headers = {'Authorization': 'Bearer ' + token}
    url = upload_url + '/' + upload_id
    resp = requests.get(url, headers=headers, timeout=90)
    return resp.json()

def ingest_file(token, stream_id, filepath, timestamp):
    """ Ingest an audio to RFCx
        Args:
            token: RFCx client token.
            stream_id: RFCx stream id
            filepath: Local file path to be ingest
            timestamp: Audio timestamp in iso format

        Returns:
            None.

        Raises:
            TypeError: if missing required arguements.
    """
    upload_endpoint = 'https://ingest.rfcx.org/uploads'
    filename = os.path.basename(filepath)

    post_resp = _generate_signed_url(token, upload_endpoint, stream_id, filename, timestamp)
    if post_resp is not None:
        print('Fail to generate url for ingest an audio')
        return

    put_resp = _ingest_to_rfcx(token, upload_endpoint, post_resp['url'], filepath)
    if put_resp is not None:
        print('Fail to ingest an audio')
        return

    while True:
        get_resp = _get_file_status(token, upload_endpoint, post_resp['uploadId'])

        if (get_resp['status'] >= 30):
            print('Failed ({}): {}'.format(get_resp['status'], get_resp['failureMessage']))
            break

        elif (get_resp['status'] == 0 or get_resp['status'] == 10):
            time.sleep(3)

        else:
            print('Success ingested file:', filepath)
            break
