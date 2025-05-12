import requests

class SecretsClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def get_secrets(self):
        response = requests.get(self.api_url,verify=False)
        # response = requests.get(self.api_url)  # Uncomment this line for production
        response.raise_for_status() 
        return response.json()
