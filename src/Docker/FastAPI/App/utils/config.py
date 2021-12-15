import configparser
import os
from .singleton import singleton
from .log import log
from . import definition as consts


@singleton
class Configuration(object):

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read(consts.CONFIG_PATH_TOKEN)
        self._dev_mode = False if (consts.CONFIG_DEV_MODE_TOKEN in os.environ and os.environ[
            consts.CONFIG_DEV_MODE_TOKEN].upper() == 'FALSE') else True
        self._set_dev_mode_configuration()

    def get(self, section, option=None):
        if not option:
            return self._config[section]

        else:
            if self._config[section][option].isnumeric():
                return int(self._config[section][option])

            return self._config[section][option]

    def get_app_run_config(self) -> dict:
        res = dict(self._config[consts.SERVER_SECTION_TOKEN])
        res.pop(consts.TIME_WINDOW_TOKEN.lower())
        if self._dev_mode:
            res.pop(consts.SSL_KEY_FILE_TOKEN.lower())
            res.pop(consts.SSL_CERT_FILE_TOKEN.lower())
        res[consts.SERVER_PORT_TOKEN.lower()] = self.get(consts.SERVER_SECTION_TOKEN, consts.SERVER_PORT_TOKEN)
        res['host'] = res['ip']
        res.pop('ip')
        return dict(res)

    def _set_dev_mode_configuration(self):
        if self._dev_mode:
            log.info("Running in development mode")
            self._config[consts.MONGO_SECTION_TOKEN][consts.MONGO_IP_TOKEN] = "localhost"
            self._config[consts.MONGO_SECTION_TOKEN][consts.MONGO_PORT_TOKEN] = "27017"
            self._config[consts.SERVER_SECTION_TOKEN][consts.SERVER_IP_TOKEN] = "localhost"
            self._config[consts.SERVER_SECTION_TOKEN][consts.SERVER_PORT_TOKEN] = "5000"
        else:
            log.info("Running in production mode")
