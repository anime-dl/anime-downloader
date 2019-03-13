from abc import ABCMeta, abstractmethod, abstractproperty
import httpretty
import json


class MockSite(metaclass=ABCMeta):
    def __init__(self):
        self.setup_httpretty()

    def setup_httpretty(self):
        data_file = 'webpages/data.json'
        data = None
        with open(data_file) as f:
            data = json.load(f)

        for obj in data:
            method = httpretty.POST
            if obj['method'] == 'GET':
                method = httpretty.GET
            with open('webpages' + obj['file']) as f:
                httpretty.register_uri(
                    method,
                    obj['url'],
                    f.read(),
                )

    @abstractproperty
    def url(self):
        raise NotImplementedError
