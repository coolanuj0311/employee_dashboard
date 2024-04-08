import requests
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import User


MICROSERVICE1_API_URL1 = "http://microservice1/api/extract_access_token/"
MICROSERVICE1_API_URL2 = "http://microservice1/api/get_user/"


def extract_access_token(authorization_header):
    try:
        response = requests.post(MICROSERVICE1_API_URL1, json={"authorization_header": authorization_header})
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            return access_token
        else:
            return None
    except requests.RequestException as e:
        # Handle request exceptions
        return None
    
def get_username_from_access_token(access_token):
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(MICROSERVICE1_API_URL2, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get("username")
            return username
        else:
            return None
    except requests.RequestException as e:
        # Handle request exceptions
        return None

def get_authorization_header(request):
    auth = request.headers.get('Authorization')
    return auth

class BasicAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = None
        try:
            authorization_header = get_authorization_header(request)
            access_token = extract_access_token(authorization_header)
        except Exception as e:
            return None

        if not access_token:
            return None

        try:
            username = get_username_from_access_token(access_token)
        except Exception as e:
            username = None

        return self.authenticate_credentials(username, request)

    def authenticate_credentials(self, username, request=None):
        user = User.objects.filter(email=username).first()
        if user is None:
            raise exceptions.AuthenticationFailed(
                "Invalid Token")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive")

        return user, None
