"""RFCx authentication"""
import os
import logging
import webbrowser
from time import sleep
from datetime import datetime, timedelta

import rfcx._api_auth as api_auth
from rfcx._credentials import Credentials
from rfcx._util import date_after

DEFAULT_CLIENT_ID = "LS4dJlP8J2iOBr2snzm6N8I5u7FLSUGd"
PERSISTED_CREDENTIALS_PATH = '.rfcx_credentials'
ALLOW_ROLES = ['rfcxUser', 'systemUser']

DEVICE_ERROR_STATUS = {
    'pending': 'authorization_pending',
    'slow': 'slow_down',
    'expired': 'expired_token',
    'denied': 'access_denied'
}

logger = logging.getLogger(__name__)


class Authentication(object):
    """Authenticate the RFCx SDK platform"""
    def __init__(self,
                 persist=True,
                 persisted_credentials_path='.rfcx_credentials'):
        self.credentials = None
        self.persist = persist
        self.persisted_credentials_path = persisted_credentials_path
        self.client_id = os.getenv('AUTH0_CLIENT_ID', DEFAULT_CLIENT_ID)

    def authenticate(self):
        """Authenticate an RFCx user to obtain a token

        If you want to persist/load the credentials to/from a custom path then set `persisted_credentials_path`
        Args:
            persist: Should save the user token to the filesystem (in file specified by
            persisted_credentials_path, defaults to .rfcx_credentials in the current directory).

        Returns:
            None.
        """
        if os.getenv('AUTH0_CLIENT_SECRET'):
            self.__generate_new_machine_token()
            return

        if os.path.exists(self.persisted_credentials_path):
            is_token_loaded = self.__load_token_from_credentials_file()
            if is_token_loaded:
                return

        self.__generate_new_user_token()

    def __load_token_from_credentials_file(self):
        with open(self.persisted_credentials_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        if len(lines) == 5 and lines[0] == 'version 1':
            access_token = lines[1]
            token_expiry = datetime.strptime(lines[3], "%Y-%m-%dT%H:%M:%S.%fZ")
            refresh_token = lines[2] if lines[2] != '' else None
            id_token = lines[4]
            if token_expiry > datetime.now() + timedelta(hours=1):
                self.__setup_credentials(access_token, token_expiry,
                                         refresh_token, id_token)
                print('Using persisted authenticatation')
                return True

            if refresh_token is not None:
                try:
                    access_token, refresh_token, token_expiry, id_token = api_auth.refresh(
                        refresh_token, self.client_id)
                    self.__setup_credentials(access_token, token_expiry,
                                             refresh_token, id_token)
                    self.__persist_credentials()
                    print(
                        'Using persisted authenticatation (with token refresh)'
                    )
                except api_auth.TokenError:
                    pass
                return True

        return False

    def __setup_credentials(self,
                            access_token,
                            token_expiry,
                            refresh_token=None,
                            id_token=None):
        self.credentials = Credentials(access_token, token_expiry,
                                       refresh_token, id_token)

    def __persist_credentials(self):
        credentials = self.credentials
        with open(self.persisted_credentials_path, 'w', encoding='utf-8') as f:
            f.write('version 1\n')
            f.write(credentials.access_token + '\n')
            f.write((credentials.refresh_token if credentials.
                     refresh_token is not None else '') + '\n')
            f.write(credentials.token_expiry.isoformat() + 'Z\n')
            f.write(credentials.id_token + '\n')

    def __generate_new_machine_token(self):
        response = api_auth.machine_auth()
        access_token = response['access_token']
        token_expiry = date_after(response['expires_in'])
        self.__setup_credentials(access_token, token_expiry)

    def __generate_new_user_token(self):
        response = api_auth.device_auth(self.client_id)
        if response is None:
            raise Exception(
                'Obtain device code failed. Please retry again later or contact support.'
            )

        device_code = response['device_code']
        user_code = response['user_code']
        interval = response['interval']
        verification_uri = response['verification_uri_complete']

        print(
            f'Go to this URL in a browser: {verification_uri} \nYour code is: {user_code}'
        )

        try:
            webbrowser.get()
            webbrowser.open(verification_uri, new=2)
        except webbrowser.Error:
            pass

        token_response, error = self.__get_device_request_token(
            device_code=device_code, interval=interval)
        if error:
            logger.error('Obtain token failed: %s', token_response)
            raise Exception(
                'Obtain token failed. Please retry again later or contact support.'
            )
        access_token = token_response['access_token']
        token_expiry = date_after(token_response['expires_in'])
        refresh_token = token_response[
            'refresh_token'] if 'refresh_token' in token_response else None
        id_token = token_response[
            'id_token'] if 'id_token' in token_response else None
        self.__setup_credentials(access_token, token_expiry, refresh_token,
                                 id_token)

        # Write token to disk
        if self.persist:
            self.__persist_credentials()

    def __get_device_request_token(self, device_code: str, interval: int = 5):
        error = 'authorization_pending'
        resp = None
        while error == DEVICE_ERROR_STATUS[
                'pending'] or error == DEVICE_ERROR_STATUS['slow']:
            sleep(interval)
            resp = api_auth.device_request_token(device_code, self.client_id)
            error = resp['error'] if 'error' in resp else None
        return resp, error
