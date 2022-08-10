import os
import json
import datetime
import httplib2
import logging
from six.moves import http_client
from six.moves import urllib


class Error(Exception):
    """Base error for this module."""


class TokenError(Error):
    """Error trying to exchange an authorization grant for an access token or refreshing a token."""


logger = logging.getLogger(__name__)

AUTH_DOMAIN = 'https://auth.rfcx.org'
AUTH_AUDIENCE = 'https://rfcx.org'

def machine_auth():
    """Get Auth0 request machine to machine token response
    Args:
        None.

    Returns:
        Auth0 request token object contains access_token, expires_in, and token_type.
    """
    auth0_client_id = os.getenv('AUTH0_CLIENT_ID')
    auth0_client_secret = os.getenv('AUTH0_CLIENT_SECRET')

    if auth0_client_id is None or auth0_client_secret is None:
        raise TokenError('Not giving `AUTH0_CLIENT_ID` or `AUTH0_CLIENT_SECRET`')

    post_data = {
        'grant_type': 'client_credentials',
        'client_id': auth0_client_id,
        'client_secret': auth0_client_secret,
        'audience': AUTH_AUDIENCE
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    body = urllib.parse.urlencode(post_data)

    http = httplib2.Http()
    _, content = http.request(f'{AUTH_DOMAIN}/oauth/token',
                              method='POST',
                              body=body,
                              headers=headers)

    return __parse_exchange_token_response(content)


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
        'audience': AUTH_AUDIENCE
    }

    headers = {'content-type': "application/x-www-form-urlencoded"}
    body = urllib.parse.urlencode(post_data)

    http = httplib2.Http()
    resp, content = http.request(f'{AUTH_DOMAIN}/oauth/device/code',
                                 method='POST',
                                 body=body,
                                 headers=headers)
    if resp.status == http_client.OK:
        return __parse_exchange_token_response(content)

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

    _, content = http.request(f'{AUTH_DOMAIN}/oauth/token',
                              method='POST',
                              body=body,
                              headers=headers)

    return __parse_exchange_token_response(content)


def refresh(refresh_token, client_id):
    post_data = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'refresh_token': refresh_token
    }
    access_token, _, token_expiry, id_token = __request_token(post_data)
    return access_token, refresh_token, token_expiry, id_token


def __request_token(post_data):
    body = urllib.parse.urlencode(post_data)
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }

    http = httplib2.Http()

    resp, content = http.request(f'{AUTH_DOMAIN}/oauth/token',
                                 method='POST',
                                 body=body,
                                 headers=headers)
    d = __parse_exchange_token_response(content)
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


def __parse_exchange_token_response(content):
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
