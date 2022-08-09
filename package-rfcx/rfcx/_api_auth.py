import datetime
import httplib2
import json
import logging
from six.moves import http_client
from six.moves import urllib
import rfcx._helper as helper


class Error(Exception):
    """Base error for this module."""


class TokenError(Error):
    """Error trying to exchange an authorization grant for an access token or refreshing a token."""


logger = logging.getLogger(__name__)


def device_auth(client_id):
    """Get Auth0 device code response
    Args:
        None.

    Returns:
        Auth0 device code json object contains device_code, user_code, expires_in, interval, verification_uri, and verification_uri_complete.
    """
    post_data = {
        'client_id': client_id,
        'scope': 'openid email profile offline_access',
        'audience': 'https://rfcx.org'
    }

    headers = {'content-type': "application/x-www-form-urlencoded"}
    body = urllib.parse.urlencode(post_data)

    http = httplib2.Http()
    resp, content = http.request('https://rfcx.eu.auth0.com/oauth/device/code',
                                 method='POST',
                                 body=body,
                                 headers=headers)
    if resp.status == http_client.OK:
        return _parse_exchange_token_response(content)

    return None

def device_request_token(device_code, client_id):
    """Get Auth0 request device token response
    Args:
        device_code: (required) Auth0 device code
        interval: (optional, default=5) Number of sleep time while waiting api

    Returns:
        Auth0 request token object contains access_token, refresh_token, id_token, scope, expires_in, and token_type.
    """
    post_data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code,
        'client_id': client_id
    }

    headers = {'content-type': "application/x-www-form-urlencoded"}
    body = urllib.parse.urlencode(post_data)

    http = httplib2.Http()

    _, content = http.request('https://rfcx.eu.auth0.com/oauth/token',
                                 method='POST',
                                 body=body,
                                 headers=headers)

    return _parse_exchange_token_response(content)


def authcode_exchange(code, code_verifier, client_id, scope):
    """Exchanges a code for OAuth2Credentials.
    Args:
        code: string, a dict-like object, or None. For a non-device
                flow, this is either the response code as a string, or a
                dictionary of query parameters to the redirect_uri. For a
                device flow, this should be None.
        http: httplib2.Http, optional http instance to use when fetching
                credentials.
    Returns:
        An OAuth2Credentials object that can be used to authorize requests.
    Raises:
        TokenError: if a problem occurred obtaining a token.
        ValueError: if code and device_flow_info are both provided or both
                    missing.
    """
    if code is None:
        raise ValueError('No code provided.')

    post_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'code': code,
        'code_verifier': code_verifier,
        'redirect_uri':
        'https://rfcx-app.s3.eu-west-1.amazonaws.com/login/cli.html',
        'scope': scope
    }
    return _request_token(post_data)


def refresh(refresh_token, client_id):
    post_data = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'refresh_token': refresh_token
    }
    access_token, _, token_expiry, id_token = _request_token(post_data)
    return access_token, refresh_token, token_expiry, id_token


def _request_token(post_data):
    body = urllib.parse.urlencode(post_data)
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }

    http = httplib2.Http()

    resp, content = http.request('https://auth.rfcx.org/oauth/token',
                                 method='POST',
                                 body=body,
                                 headers=headers)
    d = _parse_exchange_token_response(content)
    if resp.status == http_client.OK and 'access_token' in d:
        access_token = d['access_token']
        refresh_token = d.get('refresh_token', None)
        token_expiry = None
        if 'expires_in' in d:
            delta = datetime.timedelta(seconds=int(d['expires_in']))
            token_expiry = delta + datetime.datetime.utcnow()

        id_token_jwt = None
        if 'id_token' in d:
            id_token_jwt = d['id_token']

        logger.info('Successfully retrieved access token')
        return access_token, refresh_token, token_expiry, id_token_jwt
    else:
        logger.info('Failed to retrieve access token: %s', content)
        if 'error' in d:
            # you never know what those providers got to say
            error_msg = (str(d['error']) + str(d.get('error_description', '')))
        else:
            error_msg = 'Invalid response: {0}.'.format(str(resp.status))
        raise TokenError(error_msg)


def _parse_exchange_token_response(content):
    """Parses response of an exchange token request.
    Most providers return JSON but some (e.g. Facebook) return a
    url-encoded string.
    Args:
        content: The body of a response
    Returns:
        Content as a dictionary object. Note that the dict could be empty,
        i.e. {}. That basically indicates a failure.
    """
    resp = json.loads(content)
    return resp
