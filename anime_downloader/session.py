import requests
import urllib3

session = requests.Session()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
