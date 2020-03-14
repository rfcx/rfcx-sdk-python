import json
import rfcx._helper as helper

class Credentials(object):

    def __init__(self, access_token, token_expiry, refresh_token=None, id_token=None):
        self.access_token = access_token
        self.token_expiry = token_expiry
        self.refresh_token = refresh_token
        self.id_token = id_token
        self.id_object = None
        if id_token:
            self.id_object = self._extract_id_token(id_token)

    def _extract_id_token(self, id_token):
        """Extract the JSON payload from a JWT.
        Does the extraction w/o checking the signature.
        Args:
            id_token: string or bytestring, OAuth 2.0 id_token.
        Returns:
            object, The deserialized JSON payload.
        """
        if type(id_token) == bytes:
            segments = id_token.split(b'.')
        else:
            segments = id_token.split(u'.')

        if len(segments) != 3:
            raise VerifyJwtTokenError(
                'Wrong number of segments in token: {0}'.format(id_token))

        return json.loads(helper._urlsafe_b64decode(segments[1]))
