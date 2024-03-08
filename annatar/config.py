import os
from base64 import b64decode
from datetime import datetime

import structlog
from pydantic import BaseModel, root_validator

from annatar.api.filters import Filter, by_category

log = structlog.get_logger()
DEFAULT_INDEXERS = "yts,eztv,kickasstorrents-ws,thepiratebay,therarbg,torrentgalaxy,bitsearch,limetorrents,badasstorrents"


APP_ID = os.getenv("APP_ID", "community.annatar.addon.stremio")
APP_NAME = os.getenv("APP_NAME", "Annatar")
BUILD_VERSION: str = os.getenv("BUILD_VERSION", "UNKNOWN")
ENV = os.getenv("ENV", "dev")
HOST: str = os.getenv("LISTEN_HOST", "0.0.0.0")
JACKETT_INDEXERS_LIST = (os.getenv("JACKETT_INDEXERS") or DEFAULT_INDEXERS).split(",")
PORT: int = int(os.getenv("LISTEN_PORT", "8000"))
PROM_DIR = os.getenv(
    "PROMETHEUS_MULTIPROC_DIR", f"/tmp/annatar.metrics-{datetime.now().timestamp()}"
)
VERSION = os.getenv("BUILD_VERSION") or "0.0.1"


class UserConfig(BaseModel):
    debrid_service: str
    debrid_api_key: str
    filters: list[Filter] = []
    max_results: int = 5

    class Config:
        extra = "allow"

    @root_validator(pre=True)
    @classmethod
    def convert_resolutions(cls, values):
        """
        Convert from previous versions that let you filter by resolution to a
        more generic filter system
        """
        if "resolutions" not in values:
            return values
        resolutions = values["resolutions"]
        filters = values.get("filters", []).copy()
        # the filters are exclusive so we find those that are not in the list
        filters += [f for f in by_category("Resolution") if f.id not in resolutions]
        values["filters"] = filters
        return values

    @staticmethod
    def defaults() -> "UserConfig":
        return UserConfig(
            debrid_service="",
            debrid_api_key="",
            max_results=5,
            filters=[],
        )


def parse_config(b64config: str) -> UserConfig:
    if not b64config:
        return UserConfig.defaults()
    try:
        return UserConfig.model_validate_json(b64decode(b64config))
    except Exception as e:
        log.error("Unrecognized config parsing error", exc_info=e)
        return UserConfig.defaults()
