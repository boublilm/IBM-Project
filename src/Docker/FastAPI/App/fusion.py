import random
import time
import logging as log
from datetime import datetime

import numpy as np
from threading import Thread
from server import ServerInterface
from utils.singleton import singleton

@singleton
class FakeFusion(object):

    def __init__(self, **kwargs):
        self._config = kwargs.get('config')
        self._server:ServerInterface = kwargs.get('server')
        self._fake_flowid = 0
        self._domains = ['L2L','L2R', 'R2L', 'R2R']
        self._models = {}
        self._generate_fake_models()
        self.alert_thread: AlertThread = None

    def generate_alerts(self, domain='L2R',start_thread=False):
        if start_thread:
            self.alert_thread = AlertThread(config=self._config, flow_num_counter=self._fake_flowid,server=self._server)
            self.alert_thread.start()

        self._fake_flowid += 1
        score = np.mean(self._models[domain] * 100)
        self._server.insert_new_alert({'flowid': self._fake_flowid, 'anomaly_score': score,
                                      "timestamp": str(datetime.now())})

    def stop_generation(self):
        self.alert_thread.stop = True

    def update_models(self, domain, model):
        self._models.update({domain: model})

    def get_model(self, domain) -> np.array:
        return self._models.get(domain, None)

    def _generate_fake_models(self):
        for dom in self._domains:
            self._models.setdefault(dom, np.random.rand(1,4))

class AlertThread(Thread):
    def __init__(self, config, flow_num_counter, server: ServerInterface):
        self._server = server
        self._config = config
        self.stop = False
        self._wait_time = 5
        self._fake_flowid = flow_num_counter
        Thread.__init__(self)

    def run(self):
        log.info(f"Alert threading was activated")
        while not self.stop:
            time.sleep(self._wait_time)
            self._fake_flowid += 1
            random_flow = {'flowid': self._fake_flowid, 'anomaly_score': random.randrange(1, 1000),
                           'timestamp': str(datetime.now())}
            log.info(f"Generating new flow. Flowid - {self._fake_flowid}")
            self._server.insert_new_alert(random_flow)