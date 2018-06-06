# -*- coding: utf8 -*-

import functools
import logging
import json
import socket
import time
import requests


class CounterType(object):
    """Open falcon counter type."""

    GAUGE = "GAUGE"
    COUNTER = "COUNTER"


logger = logging.getLogger(__name__)


class Timer(object):
    """Timer."""

    def __init__(self, client, metric, tags=None):
        """Initialize.
        :param object client: An instance of `pyfalcon.client.Client`
        :param str metric: The name of metric
        :param int step: The cycle of report
        :param str tags: Tags
        """
        self.client = client
        self.metric = metric
        self.step = client.step
        self.tags = self.client._format_tags(tags)
        self.payload = self.client._format_content(
            self.metric, -1, self.step, CounterType.GAUGE, self.tags)

    def __call__(self, func):
        """Override `__call__`."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                rst = func(*args, **kwargs)
            finally:
                elapse = (time.time() - start) * 1000  # ms
                self.payload["value"] = elapse
                self.client._send(self.payload)
            return rst

        return wrapper

    def __enter__(self):
        """Enter the context."""
        self.start = time.time()

    def __exit__(self, typ, value, tb):
        """Leave the context."""
        elapse = (time.time() - self.start) * 1000  # ms
        self.payload["value"] = elapse
        self.client._send(self.payload)


class Client(object):
    """HTTP client."""

    def __init__(self,
                 host="localhost",
                 port=1988,
                 timeout=1,
                 step=60):
        """Initialize.
        :param str host: Open falcon agent host, ip or hostname
        :param int port: Open falcon agent port
        :param int timeout: Socket connect or recv timeout
        :param int step: The period of collecting metric
        """
        self.buffer = []
        self.metrics_index = {}
        self.host = host
        self.port = port
        self.step = step
        self.start = int(time.time())
        self.timeout = timeout
        self.endpoint = socket.gethostname()
        self.push_api = "http://{}:{}/v1/push".format(self.host, self.port)

    def _get_buffer(self, payload):
        """Send data to open falcon agent.
        :param dict data: Metric data
        :return: A buffer string.
        """
        if isinstance(payload, dict):
            now = int(time.time())
            if now - self.start < self.step:
                index = len(self.buffer)
                metric = payload["metric"]
                if metric not in self.metrics_index:
                    self.metrics_index[metric] = {
                        "index": index,
                        "count": 1
                    }
                    self.buffer.append(payload)
                else:
                    pos = self.metrics_index[metric]
                    pos["count"] += 1
                    cur_metric = self.buffer[pos["index"]]
                    cur_metric["value"] += payload["value"]
            else:
                self.start = now
                for metric in self.buffer:
                    name = metric["metric"]
                    count = self.metrics_index[name]["count"]
                    metric["value"] = float(metric["value"]) / count
                data = json.dumps(self.buffer)
                self.buffer = [payload]
                return data

    def _send(self, payload):
        """Send data to open falcon agent.
        :param dict data: Metric data
        """
        buffer = self._get_buffer(payload)
        if buffer:
            try:
                requests.post(
                    self.push_api, data=payload, timeout=self.timeout)
            except Exception:
                pass

    def _format_tags(self, tags_dict):
        """Convert the format of tags to open falcon's requirement.
        :param dict tags_dict: Tags dict
        :return: A tag str.
        """
        if not isinstance(tags_dict, dict):
            return ""

        tmp = map(lambda x: "{}={}".format(x[0], x[1]), tags_dict.items())
        return ",".join(tmp)

    def _format_content(self, metric, value, counter_type, tags):
        """Generate data to meet with the requirement of open falcon.
        :param str metric: The name of metric
        :param float/int value: The current time of the value of the metric
        :param int step: The cycle of report
        :param str counter_type: The type of counter
        :param str tags: Tags
        """
        payload = {
            "endpoint": self.endpoint,
            "metric": metric,
            "timestamp": int(time.time()),
            "step": self.step,
            "value": value,
            "counterType": counter_type,
            "tags": tags
        }
        return payload

    def gauge(self, metric, value, tags=None):
        """Collect metric using the type of counter.
        :param str metric: The name of metric, required
        :param float/int value: Metric value
        :param int step: The cycle of report, default is 60s, optional
        :param dict tags: Tags, optional
        """
        tags = self._format_tags(tags)
        payload = self._format_content(
            metric, value, CounterType.GAUGE, tags)

        self._send(payload)

    def timer(self, metric, tags=None):
        """Timer used to record response time.
        :param str metric: The name of metric
        :param int step: The cycle of report, default is 60s, optional
        :param dict tags: Tags, optional
        :return: An instance of `pyfalcon.client.Timer`.
        """
        return Timer(self, metric, tags)


if __name__ == '__main__':
    cli = Client(host="localhost",
                 port=1988,
                 timeout=1)
    cli.gauge("onlineusers", step=60, tags={"loc": "chengdu"})
