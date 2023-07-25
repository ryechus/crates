import os
import re
import binascii

from functools import cached_property

from dataclasses import dataclass, field

from .parser import loadcrate, encode_struct


PLATFORM_DEFAULT_SERATO_FOLDER = os.path.join(os.environ["HOME"], "Music", "_Serato_")
SUBCRATE_FOLDER = "SubCrates"


def get_subcrates_folder(serato_folder):
    ...


@dataclass
class Crate:
    """
    Serato saves crates in all the drives from which songs
    in the crate come from. When you create a seratojs.Crate
    it assumes we are dealing with a Music-folder-main-drive crate.

    You can "fix" this crate to represent a particular crate in
    one particular Serato folder; in which case saving will use
    that location only. You are responsible for adding songs
    compatible with that drive. This is what we call 'location-aware'
    crates.
    """

    name: str
    serato_folder: str = None
    track_paths: set[str] = field(default_factory=set)

    @property
    def filename(self):
        return f"{self.name}.crate"

    def get_save_locations(self):
        if self.serato_folder:
            return [self.serato_folder]

        # TODO: fill in the rest of this implementation if necessary
        return []
        ...

    def get_song_paths(self):
        try:
            crate = self.load_crate
        except FileNotFoundError:
            crate = []
            open(
                os.path.join(
                    PLATFORM_DEFAULT_SERATO_FOLDER, SUBCRATE_FOLDER, self.filename
                ),
                "wb",
            )

        for row in crate:
            if row[0] != "otrk":
                continue
            self.track_paths.add(row[1][0][1])

    @cached_property
    def load_crate(self):
        try:
            return loadcrate(
                os.path.join(
                    PLATFORM_DEFAULT_SERATO_FOLDER, SUBCRATE_FOLDER, self.filename
                )
            )
        except FileNotFoundError:
            open(
                os.path.join(
                    PLATFORM_DEFAULT_SERATO_FOLDER, SUBCRATE_FOLDER, self.filename
                )
            )

    @cached_property
    def contents(self):
        f = open(
            os.path.join(
                PLATFORM_DEFAULT_SERATO_FOLDER, SUBCRATE_FOLDER, self.filename
            ),
            "r",
            encoding="ascii",
            errors="ignore",
        )
        contents = f.read()
        f.close()

        return contents

    def generate_new(self):
        crate = self.head
        for path in self.track_paths:
            crate += encode_struct(path)

        return crate

    def save_new(self, name):
        crate = open(
            os.path.join(
                PLATFORM_DEFAULT_SERATO_FOLDER, SUBCRATE_FOLDER, self.filename
            ),
            "wb",
        )
        crate.write(self.generate_new())

    def add_track(self, track):
        self.track_paths.append(track)

    def get_crate_header_data(self):
        idx = re.search("otrk", self.contents).end()
        return bytes(self.contents[:idx])

    @property
    def head(self):
        return b"vrsn\x00\x00\x008\x001\x00.\x000\x00/\x00S\x00e\x00r\x00a\x00t\x00o\x00 \x00S\x00c\x00r\x00a\x00t\x00c\x00h\x00L\x00i\x00v\x00e\x00 \x00C\x00r\x00a\x00t\x00eosrt\x00\x00\x00\x13tvcn\x00\x00\x00\x02\x00#brev\x00\x00\x00\x01\x00ovct\x00\x00\x00\x1atvcn\x00\x00\x00\x08\x00s\x00o\x00n\x00gtvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x18tvcn\x00\x00\x00\x06\x00b\x00p\x00mtvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x18tvcn\x00\x00\x00\x06\x00k\x00e\x00ytvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x1etvcn\x00\x00\x00\x0c\x00l\x00e\x00n\x00g\x00t\x00htvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00$tvcn\x00\x00\x00\x12\x00p\x00l\x00a\x00y\x00C\x00o\x00u\x00n\x00ttvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x1etvcn\x00\x00\x00\x0c\x00a\x00r\x00t\x00i\x00s\x00ttvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x1ctvcn\x00\x00\x00\n\x00g\x00e\x00n\x00r\x00etvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x1ctvcn\x00\x00\x00\n\x00a\x00d\x00d\x00e\x00dtvcw\x00\x00\x00\x02\x000"
        # return b"vrsn\x00\x00\x008\x001\x00.\x000\x00/\x00S\x00e\x00r\x00a\x00t\x00o\x00 \x00S\x00c\x00r\x00a\x00t\x00c\x00h\x00L\x00i\x00v\x00e\x00 \x00C\x00r\x00a\x00t\x00eosrt\x00\x00\x00\x13tvcn\x00\x00\x00\x02\x00#brev\x00\x00\x00\x01\x00ovct\x00\x00\x00\x1atvcn\x00\x00\x00\x08\x00s\x00o\x00n\x00gtvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x18tvcn\x00\x00\x00\x06\x00b\x00p\x00mtvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x18tvcn\x00\x00\x00\x06\x00k\x00e\x00ytvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x1etvcn\x00\x00\x00\x0c\x00l\x00e\x00n\x00g\x00t\x00htvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00$tvcn\x00\x00\x00\x12\x00p\x00l\x00a\x00y\x00C\x00o\x00u\x00n\x00ttvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x1etvcn\x00\x00\x00\x0c\x00a\x00r\x00t\x00i\x00s\x00ttvcw\x00\x00\x00\x02\x000ovct\x00\x00\x00\x1ctvcn\x00\x00\x00\n\x00g\x00e\x00n\x00r\x00etvcw\x00\x00\x00\x02\x000"
