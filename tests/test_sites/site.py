from abc import ABCMeta, abstractmethod, abstractproperty
import httpretty
import json
from pathlib import Path


def configure_httpretty(sitedir):
    httpretty.enable()
    dir = Path(f"tests/test_sites/data/test_{sitedir}/")
    data_file = dir / 'data.json'

    data = None
    with open(data_file) as f:
        data = json.load(f)

    for obj in data:
        method = httpretty.POST
        if obj['method'] == 'GET':
            method = httpretty.GET
        with open(dir / obj['file']) as f:
            httpretty.register_uri(
                method,
                obj['url'],
                f.read(),
            )
