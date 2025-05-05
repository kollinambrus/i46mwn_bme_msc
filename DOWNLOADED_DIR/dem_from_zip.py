import json
import os
from pathlib import Path
import tempfile
import zipfile
import pandas as pd
import logging


class DemoFromZip():
    def __init__(self, zip_path: Path, parse_rounds = True, verbose = False) -> None:
        self.logger = logging.getLogger()
        
        self.parse_rounds = parse_rounds
        self.verbose = verbose
        self.path = zip_path[:-4]
        # print(f"self.path: {self.path}")
        self.decompress(zip_path)
        

    def decompress(self, inpath: Path) -> None:
        """Loads demo data from a zip file and restores class properties.

        Args:
            inpath (Path): Path to the zip file to read.
        """
        with (
            tempfile.TemporaryDirectory() as tmpdirname,
            zipfile.ZipFile(inpath, "r") as zipf,
        ):
            zipf.extractall(tmpdirname)

            # Load main dataframes
            if self.parse_rounds:
                self.kills = pd.read_parquet(os.path.join(tmpdirname, "kills.data"))
                self.damages = pd.read_parquet(os.path.join(tmpdirname, "damages.data"))
                self.bomb = pd.read_parquet(os.path.join(tmpdirname, "bomb.data"))
                self.smokes = pd.read_parquet(os.path.join(tmpdirname, "smokes.data"))
                self.infernos = pd.read_parquet(os.path.join(tmpdirname, "infernos.data"))
                self.weapon_fires = pd.read_parquet(os.path.join(tmpdirname, "weapon_fires.data"))
                self.rounds = pd.read_parquet(os.path.join(tmpdirname, "rounds.data"))
                self.grenades = pd.read_parquet(os.path.join(tmpdirname, "grenades.data"))

            # Load events
            self.events = {}
            events_dir = os.path.join(tmpdirname, "events")
            if os.path.isdir(events_dir):
                for event_filename in os.listdir(events_dir):
                    event_name = event_filename.split(".")[0]
                    event_path = os.path.join(events_dir, event_filename)
                    self.events[event_name] = pd.read_parquet(event_path)

            # Load ticks
            ticks_filename = os.path.join(tmpdirname, "ticks.data")
            if os.path.exists(ticks_filename):
                self.ticks = pd.read_parquet(ticks_filename)

            # Load header
            header_filename = os.path.join(tmpdirname, "header.json")
            if os.path.exists(header_filename):
                with open(header_filename, "r", encoding="utf-8") as f:
                    self.header = json.load(f)

        self._success(f"Loaded demo data from {inpath}")

    def _success(self, msg: str) -> None:
        """Log a success message.

        Args:
            msg (str): The success message to log.
        """
        if self.verbose:
            self.logger.success(msg)

    def _warn(self, msg: str) -> None:
        """Log a warning message.

        Args:
            msg (str): The warning message to log.
        """
        if self.verbose:
            self.logger.warning(msg)

    def _debug(self, msg: str) -> None:
        """Log a debug message.

        Args:
            msg (str): The debug message to log.
        """
        if self.verbose:
            self.logger.debug(msg)