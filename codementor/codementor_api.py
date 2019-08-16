import requests


class CodementorApi:

    def __init__(self):
        self.api_url = 'https://dev.codementor.io/api/'

    def get_headers(self, user):
        return {'x-codementor-api-key': user.userprofile.codementor_api_key}

    def get_completed_sessions(self, user):
        url = '{}sessions'.format(self.api_url)

        response = requests.get(url, headers=self.get_headers(user))

        results = {}
        # If the request was successful
        if response.status_code == requests.codes.ok:
            # Get the response body in JSON format
            results = response.json()
        else:
            print('Failed request {}:\n{}'.format(response.status_code, response.text))

        return results
