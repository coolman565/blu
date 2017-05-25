import requests

from config.identifier import Series


class TVDB_API():
    def __init__(self, config: Series):
        self.api_key = config.api_key
        self.user_key = config.user_key
        self.user_name = config.user_name
        self.host = config.host

        end_point = "{}/login".format(self.host)
        body = {"apikey": self.api_key, "userkey": self.user_key, "username": self.user_name}
        login_request = requests.post(end_point, json=body)
        if login_request.status_code == 200:
            self.token = login_request.json()['token']
            self.headers = {
                "Authorization": "Bearer {}".format(self.token),
                "Accept-Language": "en"
            }

    def search(self, title):
        end_point = "{}/search/series?name={}".format(self.host, title)
        search_request = requests.get(end_point, headers=self.headers)

        if search_request.status_code == 200:
            return search_request.json()['data'][0]

    def getSeriesEpisodeDetails(self, id, season):
        endpoint = "{}/series/{}/episodes/query?airedSeason={}".format(self.host, id, season)
        response = requests.get(endpoint, headers=self.headers)

        if response.status_code == 200:
            return response.json()['data']
