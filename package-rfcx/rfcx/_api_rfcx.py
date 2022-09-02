import httplib2
import json
import logging
from six.moves import http_client
from six.moves import urllib

logger = logging.getLogger(__name__)

host = 'https://api.rfcx.org'  # TODO move to configuration


def stream_segments(token, stream_id, start, end, limit, offset):
    data = {
        'id': stream_id,
        'start': start,
        'end': end,
        'limit': limit,
        'offset': offset
    }
    path = f'/streams/{stream_id}/stream-segments'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)


def annotations(token,
                start,
                end,
                classifications=None,
                stream=None,
                limit=50,
                offset=0):
    data = {'start': start, 'end': end, 'limit': limit, 'offset': offset}
    if classifications:
        data['classifications[]'] = classifications
    if stream:
        data['stream_id'] = stream
    path = '/annotations'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)


def detections(token,
               start,
               end,
               classifications=None,
               classifiers=None,
               streams=None,
               min_confidence=None,
               limit=50,
               offset=0):
    data = {'start': start, 'end': end, 'limit': limit, 'offset': offset}
    if classifications:
        data['classifications[]'] = classifications
    if classifiers:
        data['classifiers[]'] = classifiers
    if streams:
        data['streams[]'] = streams
    if min_confidence:
        data['min_confidence'] = min_confidence
    path = '/detections'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)


def streams(token,
            organizations=None,
            projects=None,
            created_by=None,
            keyword=None,
            is_public=True,
            is_deleted=False,
            limit=1000,
            offset=0):
    data = {
        'is_public': is_public,
        'is_deleted': is_deleted,
        'limit': limit,
        'offset': offset
    }
    if organizations:
        data['organizations[]'] = organizations
    if projects:
        data['projects[]'] = projects
    if created_by:
        data['created_by'] = created_by
    if keyword:
        data['keyword'] = keyword
    path = '/streams'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
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
