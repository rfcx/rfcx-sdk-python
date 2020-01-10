import getpass
import datetime
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

    def authenticate(self):
        """Authenticate an RFCx user to obtain a token

        Returns:
            Success if an access_token was obtained
        """

        if self.credentials != None:
            print('Already authenticated')
            return

        # Create a Code Verifier & Challenge
        code_verifier = pkce.code_verifier()
        code_challenge = pkce.code_challenge(code_verifier)

        # See: https://auth0.com/docs/integrations/using-auth0-to-secure-a-cli
        url = 'https://auth.rfcx.org/authorize?response_type=code&code_challenge={0}&code_challenge_method=S256&client_id={1}&redirect_uri={2}&audience=https://rfcx.org&scope={3}'
        client_id = 'LS4dJlP8J2iOBr2snzm6N8I5u7FLSUGd'
        redirect_uri = 'https://rfcx-app.s3.eu-west-1.amazonaws.com/login/cli.html' # TODO move to configuration
        scope = 'openid%20profile'

        # Prompt the user to open their browser. On completion, paste the auth code.
        print('Go to this URL in a browser: ' + url.format(code_challenge, client_id, redirect_uri, scope))
        code = getpass.getpass('Enter your authorization code: ')

        # Perform the exchange
        access_token, refresh_token, token_expiry, id_token = api_auth.authcode_exchange(code.strip(), code_verifier, client_id, scope)

        # Store the result in credentials
        self.credentials = Credentials(access_token, token_expiry, refresh_token, id_token)
        print('Successfully authenticated')
        app_meta = self.credentials.id_object['https://rfcx.org/app_metadata']
        if app_meta:
            self.accessible_sites = app_meta['accessibleSites']
            self.default_site = app_meta['defaultSite']
            print('Default site:', self.default_site)
            print('Accessible sites:', self.accessible_sites)


    def tags(self, type, labels=None, start=None, end=None, sites=None, limit=1000, include_windows='true'):
        """Retrieve tags (annotations or confirmed/rejected reviews) from the RFCx API
        
        Args:
            type: (Required) Type of tag. Must be either: annotation, inference, inference:confirmed, or inference:rejected
            labels: List of labels. If None then returns tags of any label.
            start: Minimum timestamp of the annotations to be returned. If None then defaults to exactly 30 days ago.
            end: Maximum timestamp of the annotations. If None then defaults to now.
            sites: List of sites by shortname. If None then returns tags from any site.
            limit: Maximum results to return. Defaults to 1000. (TODO check if there is an upper limit on the API)

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
            start = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).replace(microsecond=0).isoformat() + 'Z'
        if end == None:
            end = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
        
        return api_rfcx.tags(self.credentials.id_token, type, labels, start, end, sites, limit, include_windows)
