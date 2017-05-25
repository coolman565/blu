from cement.core.foundation import CementApp

from config import Config
from database import Sqlite
from handbrakeCLI.HandBrakeCLI import HandBrakeCLI
from makeMKV import MakeMKV
from metaData import Identify

with CementApp('BlueTheRipper') as app:
    app.run()

    config = Config()
    config.load_config("config.yml")

    database = Sqlite(config)

    makemkv_cli = MakeMKV(config)
    identify = Identify(config)
    hanbrake_cli = HandBrakeCLI(config)

    disc_details_list = makemkv_cli.scan_discs()

    makemkv_cli.rip_all()

    identify.get_db_metadata()

    hanbrake_cli.compress_all()
