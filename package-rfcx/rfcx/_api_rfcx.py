import httplib2
import json
import logging
from six.moves import http_client
from six.moves import urllib

logger = logging.getLogger(__name__)

host = 'https://api.rfcx.org'  # TODO move to configuration

def guardians(token, sites):
    data = {'sites[]': sites, 'limit': 1000}
    path = '/v1/guardians'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)

def guardianAudio(token, guardianId, start, end, limit, descending):
    data = {'starting_after': start, 'ending_before': end, 'limit': limit, 'order': 'descending' if descending else 'ascending'}
    path = f'/v1/guardians/{guardianId}/audio'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)

def tags(token, type, labels, start, end, sites, limit):
    data = {'type': type, 'values[]': labels, 'starting_after_local': start, 'starting_before_local': end, 'sites[]': sites, 'limit': limit}
    path = '/v2/tags'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)
    
    
def _request(url, method='GET', token=None):
    logger.debug('get url: ' + url)

    if token != None:
        headers = {'Authorization': 'Bearer ' + token}
    else:
        headers = {}

    http = httplib2.Http()
    resp, content = http.request(url, method=method, headers=headers)

    if resp.status == http_client.OK:
        return json.loads(content)
    
    logger.error(f'HTTP status: {resp.status}')

    return None