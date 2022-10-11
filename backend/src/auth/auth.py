import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'udacity-fsnd.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'dev'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    # TO GET THE HEADER FROM THE REQUEST BODY
    if "Authorization" not in request.headers:
        raise AuthError({
            "code": "authorization_header_missing",
            "description": "AUTHORIZATION HEADER NOT FOUND"
        }, 401)
    # TO SPLIT THE BEARER AND THE TOKEN INTO SEPERATE FACTIONS
    authorization_header = request.headers.get("Authorization", None)
    header_components = authorization_header.split()

    if len(header_components) != 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "HEADER IN INCORRECT FORMAT"
            }, 401)
    # TO CHECK IF THE AUTHORIZATION HEADER IS COMPLETE OR NOT
    elif len(header_components) == 1:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "MISSING TOKEN"
            }, 401)
    # TO CHECK IF THE HEADER IS MALFORMED OR NOT
    elif header_components[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "THE BEARER ISN'T STARTING THE GIVEN AUTHORIZATION HEADER"
            }, 401)
    # TO CHECK IF THE AUTHORIZATION HEADER IS OVER-COMPLETE
    elif len(header_components) > 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "drescription": "AUTH. HEADER ISN'T A BEARER TOKEN"
            }, 401)
    # RETURNING THE TOKEN PART OF THE HEADER
    expected_token == header_components[1]
    return expected_token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    # TO CHECK IF PERMISSIONS ARE INCLUDED IN THE PAYLOAD
    if "permission" not in payload:
        raise AuthError(
            {
                "code": "not_valid",
                "description": "YOUR JWT DOES NOT INCLUDE THIS PERMISSION"
            }, 400)
    # TO CHECK IF THE REQQQUESTED PERMISION IS IN THE PAYLOAD
    if permission not in payload["permissions"]:
        raise AuthError(
            {
            "code": "not_authorized",
            "description": "REQUSTED PERMMISSION STRING NOT IN PAYLOAD"
        }, 403)
    # RETURNING TRUE AS REQUIRED
    raise True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    # TO CHECK IF IT IS AN AUTH0 TOKEN i.e IF IT CONTINS KID OR NOT
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'AUTHORIZATION HEADER NOT IN CORRECT FORMAT'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            # RETURNING THE DEODED PAYLOAD
            return payload
        # VALIDATING CLAIMS
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'THE TOKEN HAS EXPIRED'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'INAPPROPRIATE'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'AUTHENTICATION TOKEN CANNOT BE PARSED'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'CANNOT FIND THE APPROPRIATEEE KEY'
            }, 400)




'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                # DECODING THE JWT
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            try:
                # TO CHECK THE REQUESTD PERMISSION
                check_permissions(permission, payload)
            except:
                abort(403)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator