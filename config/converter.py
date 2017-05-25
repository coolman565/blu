class Converter(object):
    def __init__(self):
        self.executable = "HandBrakeCLI.exe"
        self.minLength = 600
        self.compress_directory = "in_progress"
        self.preset = "HQ 1080p30 Surround"
        self.container = "mp4"
        self.encoder = "x264"
        self.encoder_options = '--x264-preset="veryslow" --x264-tune="film" --x264-profile="main"'
        self.quality = 21
        self.series = Series()

    def update(self, config):
        self.series.update(config['series'])
        self.executable = config['executable']
        self.minLength = int(config['minLength'])
        self.preset = config['preset']
        self.container = config['container']
        self.encoder = config['encoder']
        self.encoder_options = config['encoder_options']
        self.quality = float(config['quality'])


class Series(object):
    def __init__(self):
        self.file_name_template = "{series}/Season {season}/{series} S{season:02d}E{episode:02d} - {title} {quality}-{source}"
        self.output_directory = "series"

    def update(self, config):
        self.file_name_template = config['file_name_template']
        self.output_directory = config['output_directory']
