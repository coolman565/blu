class Ripper(object):
    def __init__(self):
        self.executable = "makemkvcon.exe"
        self.minLength = 900
        self.rip_dir = "raw"

    def update(self, config):
        self.executable = config['executable']
        self.minLength = config['minLength']
        self.rip_dir = config['rip_dir']
