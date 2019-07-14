import getpass
import rfcx._pkce as pkce
import rfcx._api as api
from rfcx._credentials import Credentials

class Client(object):
    """Authenticate and perform requests against the RFCx platform"""

    def __init__(self):
        self.credentials = None

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
        redirect_uri = 'https://rfcx-app.s3.eu-west-1.amazonaws.com/login/cli.html'
        scope = 'openid%20profile'

        # Prompt the user to open their browser. On completion, paste the auth code.
        print('Go to this URL in a browser: ' + url.format(code_challenge, client_id, redirect_uri, scope))
        code = getpass.getpass('Enter your authorization code: ')

        # Perform the exchange
        access_token, refresh_token, token_expiry, id_token = api.authcode_exchange(code.strip(), code_verifier, client_id, scope)

        # Store the result in credentials
        self.credentials = Credentials(access_token, token_expiry, refresh_token, id_token)
        print('ID TOKEN:')
        print(self.credentials.id_object)
