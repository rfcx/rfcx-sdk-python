import httplib2
import json
import logging
from six.moves import http_client
from six.moves import urllib

logger = logging.getLogger(__name__)

def tags(token, type, labels, start, end, sites, limit):
    data = {'type': type, 'values[]': labels, 'starting_after_local': start, 'starting_before_local': end, 'sites[]': sites, 'limit': limit}
    
    host = 'https://api.rfcx.org'  # TODO move to configuration
    path = '/v2/tags'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))

    logger.debug('url: ' + url)
    print(url)
    
    headers = {'Authorization': 'Bearer ' + token}

    http = httplib2.Http()
    resp, content = http.request(url, method='GET', headers=headers)

    if resp.status == http_client.OK:
        return json.loads(content)
    
    logger.error('HTTP status: ' + resp.status)

    return None
