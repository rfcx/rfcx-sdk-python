import logging
import os
import re
import requests
from requests_toolbelt import MultipartEncoder

logger = logging.getLogger(__name__)

base_url = os.getenv('RFCX_API_URL', 'https://api.rfcx.org')

def upload(token: str, filepath: str, name: str, version: int, classification_values: list) -> int:
    headers = {'Authorization': 'Bearer ' + token}
    with open(filepath, 'rb') as data:
        multipart_data = MultipartEncoder([
                ('file', ('model.tar.gz', data, 'text/plain')),
                ('name', name),
                ('version', str(version))] +
                [('classification_values', cv) for cv in classification_values])
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': multipart_data.content_type}
        resp = requests.post(f'{base_url}/classifiers', headers=headers, data=multipart_data, timeout=120)
    resp.raise_for_status()

    if resp.status_code != 201 or resp.headers['Location'] is None:
        return None
    
    logger.debug('Location', resp.headers['Location'])
    id = re.search('\/([0-9]+)$', resp.headers['Location'])
    return int(id.group(1)) if id is not None else None
