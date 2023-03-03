import requests
import time
import os

upload_endpoint = os.getenv('RFCX_INGEST_URL', 'https://ingest.rfcx.org/uploads')

statuses = {0: 'WAITING', 10: 'UPLOADED', 20: 'INGESTED', 30: 'FAILED', 31: 'DUPLICATE', 32: 'CHECKSUM'}
    
# POST
def _request_upload(token, stream_id, filename, timestamp):
    headers = {'Authorization': 'Bearer ' + token}
    data = {'filename': filename, 'timestamp': timestamp, 'stream': stream_id}
    resp = requests.post(upload_endpoint, headers=headers, data=data, timeout=90)
    return resp.json() if (resp.status_code == 200) else None

# PUT
def _upload(signed_url, filepath):
    file_ext = filepath.split('.')[-1]
    headers = {'Content-Type': 'audio/' + file_ext}
    with open(filepath, 'rb') as data:
        resp = requests.put(signed_url, data=data, headers=headers, timeout=120)
    resp.raise_for_status()

# GET
def _get_status(token, upload_id):
    headers = {'Authorization': 'Bearer ' + token}
    url = upload_endpoint + '/' + upload_id
    resp = requests.get(url, headers=headers, timeout=90)
    resp.raise_for_status()
    return resp.json()

def ingest_file(token, stream_id, filepath, timestamp):
    """ Ingest a single audio file
        Args:
            token: RFCx client token
            stream_id: RFCx stream id
            filepath: Local file path to be ingest
            timestamp: Audio timestamp in iso format

        Returns:
            ingest identifier

        Raises:
            Exception: on failed upload or ingest
    """
    filename = os.path.basename(filepath)

    resp = _request_upload(token, stream_id, filename, timestamp)
    if resp is None:
        raise Exception('Failed to request upload')

    try:
        _upload(resp['url'], filepath)
    except Exception as e:
        e.add_note('Failed to upload file')
        raise

    return resp['uploadId']

def check_ingest(token, ingest_id, wait_for_completion = False):
    """ Check the status of an ingest
        Args:
            token: RFCx client token
            ingest_id: Ingest identifier (returned from `ingest_file`)
            wait_for_completion: should keep waiting and checking until file is processed

        Returns:
            status: 10 is waiting (not yet processed), 20 is success, 3x is failure
            status_name
            failure_message

        Raises:
            Exception: on failed upload or ingest
    """
    while True:
        resp = _get_status(token, ingest_id)
        status = resp['status']
        if not wait_for_completion or status >= 20:
            break
        time.sleep(5)

    status_name = statuses[status] if status in statuses else 'UNKNOWN'
    failure_message = resp['failureMessage'] if 'failureMessage' in resp else None
    return status, status_name, failure_message
