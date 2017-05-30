import logging
import os
import re
import shutil
import subprocess
import tempfile
from os import linesep
from typing import Iterable

from config import Config
from database import Sqlite
from database.domain import Series, Episode
from database.domain.disc import Disc
from database.domain.media import MediaType
from database.domain.title import Status, Title
from .media import Media


class MakeMKV():
    def __init__(self, config: Config):
        self.executable = config.ripper.executable
        self.minLength = config.ripper.minLength
        self.rip_dir = config.ripper.rip_dir
        self.db = Sqlite(config)
        self.log = logging.getLogger(__name__)

    info_map = {
        "0": "unknown",
        "1": "type",
        "2": "title",
        "5": "codec_id",
        "6": "codec_short",
        "7": "codec_long",
        "8": "chapters",
        "9": "duration",
        "10": "size",
        "11": "bytes",
        "12": "extension",
        "13": "bitrate",
        "14": "audio_channels",
        "15": "angle_info",
        "16": "fname",
        "17": "sample_rate",
        "18": "sample_size",
        "19": "video_size",
        "20": "aspect_ratio",
        "21": "frame_rate",
        "22": "stream_flags",
        "23": "date_time",
        "25": "unknown",
        "26": "stream_id",
        "27": "file_name",
        "28": "lang_code",
        "29": "lang",
    }

    def scan_discs(self):
        self.log.info("Searching for discs")
        command = "{} -r info disc:-1".format(self.executable)
        self.log.debug(command)

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        (result, error) = proc.communicate()

        if proc.returncode or error is not None and len(error) > 0:
            logging.error("MakeMKV disc scan failed")
            logging.debug(error)
        else:
            resultSet = result.decode('unicode_escape').split(linesep)
            details_list = self._extract_disc_info_from_scan(resultSet)
            details_list = self._parse_disc_details(details_list)

            for disc_details in details_list:
                disc_details = self.scan(disc_details)
                if disc_details.media_type is MediaType.SERIES:
                    series = self.db.session.query(Series).filter(Series.title.ilike(disc_details.nice_title),
                                                                     Series.season == disc_details.season,
                                                                     Series.media_type == disc_details.media_type).all()
                    if len(series) == 0:
                        series = Series(title=disc_details.nice_title,
                                        season=disc_details.season,
                                        media_type=disc_details.media_type)
                        self.db.session.add(series)
                    else:
                        series = series[0]

                    disc = list(filter(
                        lambda disc: (disc.title == disc_details.disc_title)
                                     and (disc.name == disc_details.nice_title),
                        series.discs))

                    other_disc_list = list(filter(
                        lambda disc: (disc.title != disc_details.disc_title) and (disc.name == disc_details.nice_title),
                        series.discs))

                    if len(disc) == 0:
                        disc = Disc(
                            name=disc_details.nice_title,
                            drive=disc_details.disc_drive,
                            drive_name=disc_details.disc_drive_name,
                            disc_id=disc_details.disc_id,
                            title=disc_details.disc_title,
                            rip_dir=disc_details.rip_dir,
                            source=disc_details.source.replace("\"", "")
                        )
                        series.discs.append(disc)
                    else:
                        disc = disc[0]

                    current_episode_count = 0
                    for disc in other_disc_list:
                        current_episode_count = current_episode_count + len(disc.title)
                    for index, episode in enumerate(disc_details.episodes):
                        series_episode = Episode(
                            bytes=episode['bytes'],
                            duration=self._to_epoch_time(episode['duration']),
                            file_name=episode['file_name'],
                            f_name=episode['fname'],
                            frame_rate=float(episode['frame_rate'].split()[0]),
                            lang=episode['lang'],
                            lang_code=episode['lang_code'],
                            stream_id=episode['stream_id'],
                            title=episode['title'],
                            title_id=episode['title_id'],
                            video_size=episode['video_size'],
                            number=(current_episode_count + index + 1),
                            status=Status.SCANNED
                        )
                        disc.titles.append(series_episode)
                        series.episodes.append(series_episode)

                    self.db.session.commit()
                elif disc_details.media_type is MediaType.MOVIE:
                    pass
                else:
                    logging.error("Unknown MediaType: %s", disc_details.media_type)

            return details_list

    def _extract_disc_info_from_scan(self, results) -> Iterable[Media]:
        drv = "DRV"
        disc_details_list = []
        for line in results:
            if line[:len(drv)] == drv:
                working = re.sub("{}:".format(drv), "", line)
                details_set = re.sub("\"", "", working).split(",")
                details = Media()
                details.disc_id = details_set[0]
                details.disc_drive_name = details_set[4]
                details.disc_title = details_set[5]
                details.disc_drive = details_set[6]

                if (details.disc_id is not None and len(details.disc_id) > 0) \
                        and (details.disc_drive_name is not None and len(details.disc_drive_name) > 0) \
                        and (details.disc_title is not None and len(details.disc_title) > 0) \
                        and (details.disc_drive is not None and len(details.disc_drive) > 0):
                    disc_details_list.append(details)

        return disc_details_list

    def _parse_disc_details(self, disc_details_list: Iterable[Media]) -> Iterable[Media]:
        for details in disc_details_list:
            details.media_type = self._get_media_type(details.disc_title)
            details.rip_dir = os.path.join(self.rip_dir, details.disc_title)
            if details.media_type is MediaType.SERIES:
                details.season = self._get_season_number(details.disc_title)
                details.disc = self._get_disc_number(details.disc_title)
            elif details.media_type is MediaType.MOVIE:
                pass
            else:
                logging.error("Unknown Media Type: %s", details.media_type)
            details.nice_title = self._get_nice_title(details.disc_title)
        return disc_details_list

    def _get_media_type(self, disc_title) -> MediaType:
        search = re.compile(r'(DISC_(\d))|(DISC(\d))|(D(\d))|(SEASON_(\d))|(SEASON(\d))|(S(\d))')
        if search.search(disc_title):
            return MediaType.SERIES
        else:
            return MediaType.MOVIE

    def _get_disc_number(self, disc_title):
        search = re.compile(r'(DISC_(\d))|(DISC(\d))|(D(\d))')
        s = search.search(disc_title)

        counter = 0
        while s.group(len(s.groups()) - counter) is None:
            counter = counter + 1

        return s.group(len(s.groups()) - counter)

    def _get_season_number(self, disc_title):
        search = re.compile(r'(SEASON_(\d))|(SEASON(\d))|(S(\d))')
        s = search.search(disc_title)

        counter = 0
        while s.group(len(s.groups()) - counter) is None:
            counter = counter + 1

        return s.group(len(s.groups()) - counter)

    def _get_nice_title(self, disc_title):
        regex = re.compile(r'(DISC_(\d))|(DISC(\d))|(D(\d))|(SEASON_(\d))|(SEASON(\d))|(S(\d))')
        working = regex.sub("", disc_title)  # Remove Season and disc
        working = re.sub(r'_', ' ', working)  # Replace '_' with spaces
        return working.strip()  # Remove trailing/leading spaces

    def scan(self, disc: Media) -> Media:
        command = "{} -r info disc:{} --minlength={}".format(self.executable, disc.disc_id, self.minLength)
        self.log.debug(command)

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        )
        (result, error) = proc.communicate()

        if error is not None and len(error) > 0:
            logging.error("MakeMKV scan failed")
            logging.debug(error)

        resultSet = result.decode('unicode_escape').split(linesep)
        disc_details_map, makemkv_map = self._parse_makemkv_dump(resultSet)
        makemkv_sorted_list = self._order_by_stream_id(makemkv_map)
        disc.episodes = self._filter_by_stream_id(makemkv_sorted_list)
        disc.source = disc_details_map[1]
        return disc

    def rip_all(self):
        discs = self.db.session.query(Disc).filter(Disc.titles.any(Title.status == Status.SCANNED)).all()

        for disc in discs:
            temp_rip_dir = tempfile.mkdtemp(dir=self.rip_dir, prefix=disc.title)

            if self.rip(disc.disc_id, temp_rip_dir):
                dst = os.path.join(self.rip_dir, disc.title)
                os.makedirs(dst, exist_ok=True)

                for title in disc.titles:
                    src = os.path.join(temp_rip_dir, title.file_name)
                    self._touch(src)
                    local_dst = os.path.join(dst, title.file_name)
                    title.raw_file = shutil.move(src=src, dst=local_dst)
                    title.status = Status.RIPPED

                shutil.rmtree(temp_rip_dir)

        self.db.session.commit()

    def _touch(self, fname, times=None):
        with open(fname, 'a'):
            os.utime(fname, times)

    def rip(self, disc_id, directory):
        os.makedirs(directory, exist_ok=True)

        command = '{} -r mkv disc:{} all "{}" --noscan --minlength={} --decrypt --directio={}' \
            .format(self.executable, disc_id, directory, self.minLength, "true")
        logging.debug(command)

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        )

        (result, error) = proc.communicate()

        if error is not None and len(error) > 0:
            logging.error("MakeMKV scan failed")
            logging.debug(error)
            return False

        resultSet = result.decode('unicode_escape').split(linesep)
        return True

    def _order_by_stream_id(self, makemkv_map):
        ordered_list = []
        for index, value in makemkv_map.items():
            ordered_list.append(value)

        ordered_list.sort(key=lambda i: i[self.info_map["26"]])

        return ordered_list

    def _filter_by_stream_id(self, list):
        seen = {}
        result = []
        for item in list:
            marker = item['stream_id']
            if marker in seen:
                continue
            seen[marker] = 1
            result.append(item)
        return result

    def _parse_makemkv_dump(self, makemkv_dump):
        """
        :param makemkv_dump: 
        :return: 
        """
        disc = {}
        titles = {}
        for line in makemkv_dump:
            info_type = line[:5]
            csv = line[6:].split(',')

            if info_type == 'CINFO':
                disc[int(csv[0])] = csv[2]
            elif info_type == 'TINFO' or info_type == 'SINFO':
                if titles.get(csv[0]):
                    title = titles.get(csv[0])
                else:
                    title = {}
                    title['title_id'] = re.sub('"', '', csv[0])

                if line[:len('TINFO')] == 'TINFO' and self.info_map.get(csv[1]) is not None:
                    title[self.info_map.get(csv[1])] = re.sub('"', '', csv[3])
                elif line[:len('SINFO')] == 'SINFO' and int(csv[1]) == 0 and self.info_map.get(csv[2]) is not None:
                    title[self.info_map[csv[2]]] = re.sub('"', '', csv[4])

                titles[csv[0]] = title

        return disc, titles

    def _to_epoch_time(self, time) -> int:
        h, m, s = time.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
