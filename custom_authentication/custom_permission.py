"""
    check if authenticated ?
    customer_id = user.customer.id
    LMS_resources = 
    customerresources.filter(customer=cutomer_id, resource=)

"""

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import User
import boto3


# Global Declaration
client = boto3.client('cognito-idp', region_name=base.COGNITO_REGION_NAME)

# Method to get username from access_token
def get_username_from_access_token(access_token):
    try:
        client_response = client.get_user(AccessToken=access_token)
        if 'UserAttributes' in client_response.keys():
            for key in client_response['UserAttributes']:
                if key['Name'] == 'email':
                    username = key['Value']
                    break
            return username

    except client.exceptions.NotAuthorizedException as e:
        return None

def get_authorization_header(request):
    
    auth = request.headers.get('authtoken')
    return auth


class BasicAuthentication(BaseAuthentication):
    def authenticate(self, request):

        # Retrieve JWT Bearer Token and encode it or retrieve data from boto3
        access_token = None
        try:
            auth = get_authorization_header(request).split()
            access_token = auth[1]
        except Exception as e:
            return None

        if not auth or auth[0].lower() != "bearer":
            return None

        # Token should be with Bearer 
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(
                "Invalid basic header. No credentials provided.")

        # To check if Authorization is valid
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed(
                "Invalid basic header. Credential string is not properly formatted")

        # Decode JWT Token or Retrieve data from boto3 
        try:
            # Decode Data From Token
            # decoded_data = jwt.decode(auth[1], algorithms=["RS256"], options={"verify_signature": False})

            # Get Data From Cognito
            username = get_username_from_access_token(access_token)

        except Exception as e:
            username = None


        return self.authenticate_credentials(username, request)


    def authenticate_credentials(self, username, request=None):

        # Authenticate User using credentials [ You can add your custom conditions ]

        user = User.objects.filter(email=username).first()

        if user is None:
            raise exceptions.AuthenticationFailed(
                "Invalid Token")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive")

        return user, None