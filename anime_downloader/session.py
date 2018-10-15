import requests
import urllib3

_session = requests.Session()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_session():
    global _session
    _session = _session or requests.Session()

    return _session
