class Database(object):
    def __init__(self):
        self.dialect = 'sqlite'
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.database = 'blue_the_ripper.db'

    def update(self, config):
        self.dialect = config['dialect']
        self.username = config['username']
        self.password = config['password']
        self.host = config['host']
        self.port = config['port']
        self.database = config['database']

    def get_connection_string(self):
        # dialect+driver://username:password@host:port/database
        if self.dialect == 'sqlite':
            return "{dialect}:///{database}".format(dialect=self.dialect, database=self.database)
        else:
            return "{dialect}://{username}:{password}@{host}:{port}/{database}" \
                .format(dialect=self.dialect,
                        username=self.username,
                        password=self.password,
                        host=self.host,
                        port=self.port,
                        database=self.database)
