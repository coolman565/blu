import logging
import os
import re
import subprocess

from config import Config
from database import Sqlite
from database.domain import Title
from database.domain.title import Status


class HandBrakeCLI:
    def __init__(self, config: Config):
        self.log = logging.getLogger(__name__)
        self.executable = config.converter.executable
        self.minLength = config.converter.minLength
        self.series_directory = config.converter.series.output_directory
        self.tv_file_name_template = config.converter.series.file_name_template
        self.preset = config.converter.preset
        self.container = config.converter.container
        self.encoder = config.converter.encoder
        self.encoder_options = config.converter.encoder_options
        self.quality = config.converter.quality
        self.db = Sqlite(config)

    def compress_files(self, input_list, output_directory, output_filename_template):
        for index, input in enumerate(input_list):
            filename = output_filename_template.format(index + 1)
            output = os.path.join(output_directory, filename)
            self.compress_file(input, output)

    def _generate_file_path(self, file):
        file_name = self.tv_file_name_template \
            .format(series=file.series.title,
                    season=file.series.season,
                    episode=file.number,
                    title=file.title,
                    quality=file.video_size.split('x')[1],
                    source=file.discs.source)
        formatted_file_name = ""
        for file_name_part in file_name.split('/'):
            formatted_file_name = os.path.join(formatted_file_name, file_name_part)
        return formatted_file_name

    def _convert_folder_path(self, folder_path):
        formatted_folder_path = ""
        for sub_folder in folder_path.split('/'):
            formatted_folder_path = os.path.join(formatted_folder_path, sub_folder)
        return formatted_folder_path

    def compress_all(self):
        compress_list = self.db.session.query(Title).filter_by(status=Status.RIPPED).all()
        for file in compress_list:
            if file.type == 'episodes':
                file_name = self._generate_file_path(file)
                output = os.path.join(self._convert_folder_path(self.series_directory), file_name)
                if self.compress_file(input=file.raw_file, output=output):
                    file.status = Status.COMPRESSED
                    file.compressed_file = output
                    self.db.session.commit()
                else:
                    self.log.warning("Failed to compress file: %s", file.raw_file)
            elif file.type == 'movies':
                pass
            else:
                self.log.error("Unknown Media Type: %s", file.type)
        self.db.session.commit()

    def compress_file(self, input, output):
        if not os.path.exists(input):
            self.log.error("Input does not exist: '" + input + "'")
            return False

        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output))

        command = '{} --verbose --input="{}" --output="{}" --preset="{}" --encoder="{}" {} --quality={} --optimize --two-pass --turbo --markers' \
            .format(self.executable,
                    input,
                    "{}.{}".format(output, self.container),
                    self.preset,
                    self.encoder,
                    self.encoder_options,
                    self.quality)
        self.log.debug(command)

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        )

        (result, error) = proc.communicate()

        if proc.returncode is not 0:
            self.log.error("Subprocess returned: %d", proc.returncode)
            return False

        return True
