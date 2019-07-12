import base64
import hashlib
import secrets
import getpass
import rfcx._pkce as pkce
import rfcx._api as api

def login():

    # https://auth0.com/docs/integrations/using-auth0-to-secure-a-cli

    # Create a Code Verifier & Challenge
    random = secrets.token_bytes(64)
    code_verifier = base64.b64encode(random, b'-_').decode().replace('=', '')
    # code_verifier = pkce.code_verifier()
    # code_challenge = pkce.code_challenge(code_verifier)

    m = hashlib.sha256()
    m.update(code_verifier.encode())
    d = m.digest()
    code_challenge = base64.b64encode(d, b'-_').decode().replace('=', '')

    url = 'https://auth.rfcx.org/authorize?response_type=code&code_challenge={0}&code_challenge_method=S256&client_id={1}&redirect_uri={2}&audience=https://rfcx.org&scope={3}'
    client_id = 'LS4dJlP8J2iOBr2snzm6N8I5u7FLSUGd'
    redirect_uri = 'https://rfcx-app.s3.eu-west-1.amazonaws.com/login/cli.html'
    scope = 'openid%20profile'

    print('Go to this URL in a browser: ' + url.format(code_challenge, client_id, redirect_uri, scope))
    
    code = getpass.getpass('Enter your authorization code: ')
    # gcloud_process.communicate(code.strip())

    access_token, refresh_token, token_expiry, id_token = api.authcode_exchange(code, code_verifier, client_id, scope)

    print('ACCESS TOKEN:')
    print(access_token)
    print('ID TOKEN:')
    print(id_token)
