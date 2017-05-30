import logging
import requests

from config.identifier import Series


class TVDB_API():
    def __init__(self, config: Series):
        self.log = logging.getLogger(__name__)
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
        else:
            self.log.warning("TheTVDB login failed")
            self.log.debug("%d: %s",login_request.status_code, login_request.json())

    def search(self, title):
        end_point = "{}/search/series?name={}".format(self.host, title)
        search_request = requests.get(end_point, headers=self.headers)

        if search_request.status_code == 200:
            return search_request.json()['data'][0]
        else:
            self.log.warning("Series search failed")
            self.log.debug("%d: %s", search_request.status_code, search_request.json())

    def getSeriesEpisodeDetails(self, id, season):
        endpoint = "{}/series/{}/episodes/query?airedSeason={}".format(self.host, id, season)
        response = requests.get(endpoint, headers=self.headers)

        if response.status_code == 200:
            return response.json()['data']
        else:
            self.log.warning("Episode Search failed")
            self.log.debug("%d: %s", response.status_code, response.json())
