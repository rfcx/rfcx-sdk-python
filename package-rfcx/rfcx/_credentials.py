import json
import rfcx._helper as helper

class VerifyJwtTokenError(Exception):
    """Exception raised when the id token is invalid."""
    def __init__(self, id_token: str, message: str = 'Wrong number of segments in token') -> None:
        self.id_token = id_token
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f'{self.message}: {self.id_token}'

class Credentials(object):

    def __init__(self, access_token, token_expiry, refresh_token=None, id_token=None):
        self.token = id_token if id_token else access_token
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
            raise VerifyJwtTokenError(id_token)

        return json.loads(helper._urlsafe_b64decode(segments[1]))
