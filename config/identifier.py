class Identifier(object):
    def __init__(self):
        self.series = Series()

    def update(self, config):
        self.series.update(config['series'])

class Series(object):
    def __init__(self):
        self.api_key = None
        self.user_key = None
        self.user_name = None
        self.host = "https://api.thetvdb.com"

    def update(self, config):
        self.api_key = config['api_key']
        self.user_key = config['user_key']
        self.user_name = config['user_name']
        self.host = config['host']
