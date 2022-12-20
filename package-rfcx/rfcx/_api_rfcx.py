import httplib2
import json
import logging
import os
from six.moves import http_client
from six.moves import urllib

logger = logging.getLogger(__name__)

base_url = os.getenv('RFCX_API_URL', 'https://api.rfcx.org')

def stream_segments(token, stream_id, start, end, limit, offset):
    data = {'start': start, 'end': end, 'limit': limit, 'offset': offset}
    path = f'/streams/{stream_id}/segments'
    url = f'{base_url}{path}?{urllib.parse.urlencode(data, True)}'
    return _request(url, token=token)


def annotations(token,
                start,
                end,
                classifications=None,
                stream_id=None,
                limit=50,
                offset=0):
    data = {'start': start, 'end': end, 'limit': limit, 'offset': offset}
    if classifications:
        data['classifications[]'] = classifications
    if stream_id:
        data['stream_id'] = stream_id

    path = '/annotations'
    url = f'{base_url}{path}?{urllib.parse.urlencode(data, True)}'
    return _request(url, token=token)


def detections(token,
               start,
               end,
               classifications=None,
               classifiers=None,
               stream_ids=None,
               min_confidence=None,
               limit=50,
               offset=0):
    data = {'start': start, 'end': end, 'limit': limit, 'offset': offset}
    if classifications:
        data['classifications[]'] = classifications
    if classifiers:
        data['classifiers[]'] = classifiers
    if stream_ids:
        data['streams[]'] = stream_ids
    if min_confidence:
        data['min_confidence'] = min_confidence

    path = '/detections'
    url = f'{base_url}{path}?{urllib.parse.urlencode(data, True)}'
    return _request(url, token=token)


def stream(token, stream_id=None, fields=None):
    data = {}
    if fields is not None:
        data['fields[]'] = fields
    path = f'/streams/{stream_id}'
    url = f'{base_url}{path}?{urllib.parse.urlencode(data, True)}'
    return _request(url, token=token)


def streams(token,
            organizations=None,
            projects=None,
            created_by=None,
            name=None,
            keyword=None,
            only_public=None,
            only_deleted=None,
            fields=None,
            limit=1000,
            offset=0):
    data = {'limit': limit, 'offset': offset}
    if organizations:
        data['organizations[]'] = organizations
    if projects:
        data['projects[]'] = projects
    if created_by:
        data['created_by'] = created_by
    if keyword:
        data['keyword'] = keyword
    if name:
        data['name'] = name
    if isinstance(only_public, bool):
        data['only_public'] = 'true' if only_public else 'false'
    if isinstance(only_deleted, bool):
        data['only_deleted'] = 'true' if only_deleted else 'false'
    if fields is not None:
        data['fields[]'] = fields

    path = '/streams'
    url = f'{base_url}{path}?{urllib.parse.urlencode(data, True)}'
    return _request(url, token=token)


def projects(token,
             keyword=None,
             created_by=None,
             only_public=None,
             only_deleted=None,
             fields=None,
             limit=1000,
             offset=0):
    data = {'limit': limit, 'offset': offset}
    if keyword:
        data['keyword'] = keyword
    if created_by:
        data['created_by'] = created_by
    if isinstance(only_public, bool):
        data['only_public'] = 'true' if only_public else 'false'
    if isinstance(only_deleted, bool):
        data['only_deleted'] = 'true' if only_deleted else 'false'
    if fields is not None:
        data['fields[]'] = fields

    path = '/projects'
    url = f'{base_url}{path}?{urllib.parse.urlencode(data, True)}'
    return _request(url, token=token)


def _request(url, method='GET', token=None):
    logger.debug('get url: %s', url)

    if token is not None:
        headers = {'Authorization': 'Bearer ' + token}
    else:
        headers = {}

    http = httplib2.Http()
    resp, content = http.request(url, method=method, headers=headers)

    if resp.status == http_client.OK:
        return json.loads(content)

    logger.error('HTTP status: %s', resp.status)

    if resp.status == 403:
        logger.error('No permission on given parameter(s)')

    return None
