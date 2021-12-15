from datetime import datetime
from typing import Dict
from utils.log import log
from Mongo import MongoHandler
import utils.definition as consts
from utils.config import Configuration
from utils.tools import diff_in_hours
from utils.singleton import singleton


@singleton
class ServerInterface(object):

    def __init__(self, **kwargs):
        self._config: Configuration = kwargs.get('config')
        self._db_handler: MongoHandler = MongoHandler(
            self._config.get(consts.MONGO_SECTION_TOKEN, consts.MONGO_IP_TOKEN),
            self._config.get(consts.MONGO_SECTION_TOKEN, consts.MONGO_PORT_TOKEN),
            self._config.get(consts.MONGO_SECTION_TOKEN, consts.MONGO_DB_TOKEN),
        )
        self._time_window = self._config.get(consts.SERVER_SECTION_TOKEN, consts.TIME_WINDOW_TOKEN)
        self._timer = datetime.now()
        log.debug(f"timer on the server is set to {str(self._timer)} and will be reset every 24 hours")

    def insert_new_feedback(self, feedback: Dict):
        try:

            self._db_handler.insert_document(
                collection_name=self._config.get(consts.MONGO_SECTION_TOKEN, consts.MONGO_DB_FEEDBACK_TABLE_TOKEN),
                document=feedback
            )

        except Exception as e:
            log.exception("Couldn't insert feedback", e)
            raise e

    def insert_new_alert(self, alert: Dict):
        try:
            self._restart_timer()
            alert_time = datetime.strptime(alert.get(consts.TIME_TOKEN), consts.TIME_FORMAT)
            if (self._is_exists(alert.get(consts.FLOW_ID_TOKEN))
                    and
                    diff_in_hours(alert_time, self._timer) < 24
                    and
                    self._is_malicious_flow(alert.get(consts.FLOW_ID_TOKEN))
            ):
                # The new flow already exists in the Feedback table, meaning it was recently labeled by the user as
                # malicious.
                # Furthermore it is a new label, as it has been less than 24 hours since it was inserted.
                # In that case we don't want to update the user with the same flow twice.
                return

            self._db_handler.insert_document(
                collection_name=self._config.get(consts.MONGO_SECTION_TOKEN, consts.MONGO_DB_FUSION_TABLE_TOKEN),
                document=alert
            )

        except Exception as e:
            log.exception("Couldn't insert alert", e)
            raise e

    def _is_exists(self, flowid: str) -> bool:
        return True if self._db_handler.get_document(
            collection_name=self._config.get(consts.MONGO_SECTION_TOKEN, consts.MONGO_DB_FEEDBACK_TABLE_TOKEN),
            document_id=flowid,
            filter=consts.FLOW_ID_TOKEN
        ) else False

    def _is_malicious_flow(self, flowid: str) -> bool:
        return True if self._db_handler.get_document(
            collection_name=self._config.get(consts.MONGO_SECTION_TOKEN, consts.MONGO_DB_FEEDBACK_TABLE_TOKEN),
            document_id=flowid,
            filter=consts.FLOW_ID_TOKEN
        )[consts.FLOW_ID_TOKEN] == consts.MALICIOUS_TOKEN else False

    def _restart_timer(self):
        if diff_in_hours(datetime.now(), self._timer) > 24:
            self._timer = datetime.now()
