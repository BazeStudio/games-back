import logging
import os

from strictyaml import Map, Str, Bool, load

logger = logging.getLogger(__name__)

# конфиг которым управляют админы
CONFIG_ENV_NAME = 'games_config'

if CONFIG_ENV_NAME in os.environ:
    src_file = os.environ.get(CONFIG_ENV_NAME)
else:
    src_file = '/etc/games/games.yml'


with open(src_file, 'r') as file_h:
    CFG_CONTENT = file_h.read()


SCHEMA = Map({
    "connections": Map(
        {
            "pgsql": Map({"uri": Str()}),
            "celery": Map({"uri": Str()}),
        }
    ),
    "static_root": Str(),
    "api_docs_enabled": Bool(),
    "debug": Bool(),
    "secret_key": Str(),
    "media_root": Str()
})

config = load(CFG_CONTENT, SCHEMA)
