import getpass
import datetime
import os
import re
import rfcx.audio as audio
import rfcx._pkce as pkce
import rfcx._api_rfcx as api_rfcx
import rfcx._api_auth as api_auth
from rfcx._credentials import Credentials


class Client(object):
    """Authenticate and perform requests against the RFCx platform"""

    def __init__(self):
        self.credentials = None
        self.default_site = None
        self.accessible_sites = None
        self.persisted_credentials_path = '.rfcx_credentials'

    def authenticate(self, persist=True):
        """Authenticate an RFCx user to obtain a token

        If you want to persist/load the credentials to/from a custom path then set `persisted_credentials_path`
        before calling `client.authenticate()`. E.g. `client.persisted_credentials_path = '/my/path/.rfcx_credentials'`

        Args:
            persist: Should save the user token to the filesystem (in file specified by
            persisted_credentials_path, defaults to .rfcx_credentials in the current directory).

        Returns:
            Success if an access_token was obtained
        """

        if self.credentials != None:
            print('Already authenticated')
            return

        client_id = 'LS4dJlP8J2iOBr2snzm6N8I5u7FLSUGd'
        access_token = None

        # Attempt to load the credentials from disk
        if os.path.exists(self.persisted_credentials_path):
            with open(self.persisted_credentials_path, 'r') as f:
                lines = f.read().splitlines()
            if len(lines) == 5 and lines[0] == 'version 1':
                access_token = lines[1]
                refresh_token = lines[2] if lines[2] != '' else None
                token_expiry = datetime.datetime.strptime(
                    lines[3], "%Y-%m-%dT%H:%M:%S.%fZ")
                id_token = lines[4]
                if token_expiry > datetime.datetime.now() + datetime.timedelta(hours=1):
                    self._setup_credentials(
                        access_token, token_expiry, refresh_token, id_token)
                    print('Using persisted authenticatation')
                    return
                elif refresh_token != None:
                    has_error = False
                    try:
                        access_token, refresh_token, token_expiry, id_token = api_auth.refresh(
                            refresh_token, client_id)
                    except api_auth.TokenError:
                        has_error = True
                    if not has_error:
                        self._setup_credentials(
                            access_token, token_expiry, refresh_token, id_token)
                        self._persist_credentials()
                        print('Using persisted authenticatation (with token refresh)')
                        return

        # Create a Code Verifier & Challenge
        code_verifier = pkce.code_verifier()
        code_challenge = pkce.code_challenge(code_verifier)

        # See: https://auth0.com/docs/integrations/using-auth0-to-secure-a-cli
        url = 'https://auth.rfcx.org/authorize?response_type=code&code_challenge={0}&code_challenge_method=S256&client_id={1}&redirect_uri={2}&audience=https://rfcx.org&scope={3}'
        # TODO move to configuration
        redirect_uri = 'https://rfcx-app.s3.eu-west-1.amazonaws.com/login/cli.html'
        scope = 'openid%20email%20profile%20offline_access'

        # Prompt the user to open their browser. On completion, paste the auth code.
        print('Go to this URL in a browser: ' +
              url.format(code_challenge, client_id, redirect_uri, scope))
        code = getpass.getpass('Enter your authorization code: ')

        # Perform the exchange
        access_token, refresh_token, token_expiry, id_token = api_auth.authcode_exchange(
            code.strip(), code_verifier, client_id, scope)
        self._setup_credentials(
            access_token, token_expiry, refresh_token, id_token)

        print('Successfully authenticated')
        print('Default site:', self.default_site)
        if len(self.accessible_sites) > 0:
            print('Accessible sites:', ", ".join(self.accessible_sites))

        # Write token to disk
        if persist:
            self._persist_credentials()

    def _setup_credentials(self, access_token, token_expiry, refresh_token, id_token):
        self.credentials = Credentials(
            access_token, token_expiry, refresh_token, id_token)
        app_meta = self.credentials.id_object['https://rfcx.org/app_metadata']
        if app_meta:
            self.accessible_sites = app_meta.get('accessibleSites', [])
            self.default_site = app_meta.get('defaultSite', 'derc')
            # Check we have sufficient credentials
            roles = app_meta.get('authorization', {}).get('roles', [])
            if not "rfcxUser" in roles:
                raise Exception(
                    "User does not have sufficient privileges. Please check you have access to https://dashboard.rfcx.org or contact support.")

    def _persist_credentials(self):
        c = self.credentials
        with open(self.persisted_credentials_path, 'w') as f:
            f.write('version 1\n')
            f.write(c.access_token + '\n')
            f.write((c.refresh_token if c.refresh_token != None else '') + '\n')
            f.write(c.token_expiry.isoformat() + 'Z\n')
            f.write(c.id_token + '\n')

    # v1
    def guardians(self, sites=None):
        """Retrieve a list of guardians from a site (TO BE DEPRECATED - use streams in future)

        Args:
            sites: List of site shortnames (e.g. cerroblanco). Default (None) gets all your accessible sites.

        Returns:
            List of guardians"""

        if sites == None:
            sites = self.accessible_sites

        return api_rfcx.guardians(self.credentials.id_token, sites)

    def guardianAudio(self, guardianId=None, start=None, end=None, limit=50, offset=0, descending=True):
        """Retrieve audio information about a specific guardian (TO BE DEPRECATED - use streams in future)

        Args:
            guardianId: (Required) The guid of a guardian
            start: Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            end: Maximum timestamp of the audio. If None then defaults to now.
            limit: Maximum results to return. Defaults to 50. (TODO check if there is an upper limit on the API)
            descending: Order by newest results first. Defaults to True.

        Returns:
            List of audio files (meta data showing audio id and recorded timestamp)
        """
        if self.credentials == None:
            print('Not authenticated')
            return

        if start == None:
            start = (datetime.datetime.utcnow() - datetime.timedelta(days=30)
                     ).replace(microsecond=0).isoformat() + 'Z'
        if end == None:
            end = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

        return api_rfcx.guardianAudio(self.credentials.id_token, guardianId, start, end, limit, offset, descending)

    def tags(self, type, labels, start=None, end=None, sites=None, limit=1000):
        """Retrieve tags (annotations or confirmed/rejected reviews) from the RFCx API

        Args:
            type: (Required) Type of tag. Must be either: annotation, inference, inference:confirmed, or inference:rejected
            labels: (Required) List of labels. If None then returns tags of any label.
            start: Minimum timestamp of the annotations to be returned. If None then defaults to exactly 30 days ago.
            end: Maximum timestamp of the annotations. If None then defaults to now.
            sites: List of sites by shortname. If None then returns tags from any site.
            limit: Maximum number of audio files to return (not the number of tags!). Defaults to 1000.

        Returns:
            List of tags
        """
        if self.credentials == None:
            print('Not authenticated')
            return

        if type not in ['annotation', 'inference', 'inference:confirmed', 'inference:rejected']:
            print('Unrecognized type')
            return

        if start == None:
            start = (datetime.datetime.utcnow() - datetime.timedelta(days=30)
                     ).replace(microsecond=0).isoformat() + 'Z'
        if end == None:
            end = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

        return api_rfcx.tags(self.credentials.id_token, type, labels, start, end, sites, limit)

    def downloadGuardianAudio(self, dest_path=None, guardian_id=None, min_date=None, max_date=None, file_ext='opus', parallel=True):
        """Download audio using audio information from `guardianAudio`

        Args:
            dest_path: (Required) Path to save audio.
            guardianId: (Required) The guid of a guardian
            min_date: Minimum timestamp of the audio. If None then defaults to exactly 30 days ago.
            max_date: Maximum timestamp of the audio. If None then defaults to now.
            file_ext: Audio file extension. Default to `.opus`
            parallel: Parallel download audio. Defaults to True.

        Returns:
            None.
        """
        if self.credentials == None:
            print('Not authenticated')
            return

        if dest_path == None:
            if not os.path.exists('./audios'):
                os.makedirs('./audios')
        if guardian_id == None:
            print("Please specific the guardian id.")
            return

        if min_date == None:
            min_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        if not isinstance(min_date, datetime.datetime):
            print("min_date is not type datetime")
            return

        if max_date == None:
            max_date = datetime.datetime.utcnow()
        if not isinstance(max_date, datetime.datetime):
            print("max_date is not type datetime")
            return

        return audio.downloadGuardianAudio(self.credentials.id_token, dest_path, guardian_id, min_date, max_date, file_ext, parallel)

    def streams(self, keyword='', limit=1000, offset=0):
        """Retrieve a list of streams

        Args:
            keyword:(optional, default= '') Match streams with name
            limit: (optional, default= 1000) Maximum number of  results to return
            offset: (optional, default= 0) Number of results to skip

        Returns:
            List of streams"""

        return api_rfcx.streams(self.credentials.id_token, keyword, limit, offset)
