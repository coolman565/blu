from database.domain.media import MediaType


class Media(object):
    disc = None
    disc_drive = None
    disc_drive_name = None
    disc_id = None
    disc_title = None
    nice_title = None
    media_type = None
    season = None
    rip_dir = None
    episodes = []
    source = None


class Series(Media):
    season = None

    def __init__(self):
        self.media_type = MediaType.SERIES
        self.episodes = []


class Title(object):
    bytes = None
    chapters = None
    duration = None
    file_name = None
    f_name = None
    lang = None
    lang_code = None
    size = None
    stream_id = None
    title = None
    title_id = None


class Movie(Media):
    title = None

    def __init__(self):
        self.media_type = MediaType.MOVIE
