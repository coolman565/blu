from config import Config
from database import Sqlite
from database.domain import Series, Episode
from database.domain.title import Status
from .theTVDB_API import TVDB_API


class Identify():
    def __init__(self, config: Config):
        self.tvdb_api = TVDB_API(config.identifier.series)
        self.db = Sqlite(config)

    def get_db_metadata(self):
        self._get_series_details()

    def _get_series_details(self):
        series_list = self.db.session.query(Series) \
            .filter(Series.episodes.any(Episode.status == Status.RIPPED)) \
            .all()

        for series in series_list:
            series_data = self.tvdb_api.search(series.title)
            series.title = series_data['seriesName']
            episode_data = self.tvdb_api.getSeriesEpisodeDetails(series_data['id'], series.season)
            for index, episode in enumerate(series.episodes):
                episode_details = self._get_episode_by_number(episode.number, episode_data)
                if episode_details is not None:
                    episode.title = episode_details['episodeName']

        self.db.session.commit()

    def _get_episode_by_number(self, episode_number, tvdb_data):
        for details in tvdb_data:
            if details['airedEpisodeNumber'] == episode_number:
                return details
        return None
