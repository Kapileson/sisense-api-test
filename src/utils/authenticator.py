import os
import requests
import json

from src.utils.utilities import Utilities


class Authenticator:

    def __init__(self):
        self.user_credential = self.get_sisense_credentials()
        self.auth_url = self.get_auth_url()

    @staticmethod
    def get_base_url():
        return "https://{0}/api/".format(Utilities.url)

    def get_auth_url(self):
        auth_url = self.get_base_url() + "v1/authentication/login"
        return auth_url

    @staticmethod
    def get_sisense_credentials():
        sisense_credential = {'user_name': os.getenv('SISENSE_USERNAME'),
                              'password': os.getenv('SISENSE_PASSWORD')}
        return sisense_credential

    def get_token(self):
        # Gets Authorization token to use in other requests.
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = json.dumps({'username': self.user_credential['user_name'], 'password': self.user_credential['password']})
        r = requests.post(self.auth_url, data=body, headers=headers)
        json_data = r.json()
        token = str(json_data['access_token'])
        return token
