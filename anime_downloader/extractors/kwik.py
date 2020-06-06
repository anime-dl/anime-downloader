import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader import util
from anime_downloader.config import Config
from uuid import uuid4
from time import time
from secrets import choice
import requests

logger = logging.getLogger(__name__)


class Kwik(BaseExtractor):
    '''Extracts video url from kwik pages, Kwik has some `security`
       which allows to access kwik pages when only refered by something
       and the kwik video stream when refered through the corresponding
       kwik video page.
    '''
    headers = {
            'User-Agent': choice((
                'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko)',
                'Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
                ))
            }
    session = requests.session()


    #Captcha bypass stuff is mostly thanks to https://github.com/Futei/SineCaptcha
    def _generate_mouse_movements(self, timestamp):
        mouse_movements = []
        last_movement = timestamp

        for index in range(choice(range(1000, 10000))):
            last_movement += choice(range(10))
            mouse_movements.append([choice(range(500)), choice(range(500)), last_movement])

        return mouse_movements

    def bypass_captcha(self):
        bypassed = False
        
        #Retry until success
        while not bypassed:
            site_key = str(uuid4())
            response = self.session.post('https://hcaptcha.com/getcaptcha', data = {
                'sitekey': site_key,
                'host': 'kwik.cx'
                }).json()
            
            key = response.get('key')
            tasks = [row['task_key'] for row in response.get('tasklist')]
            job = response.get('request_type')
            timestamp = round(time()) + choice(range(30, 120))
            answers = dict(zip(tasks, [choice(['true', 'false']) for index in range(len(tasks))]))

            #Mouse movements
            mm = self._generate_mouse_movements(timestamp)
            ts = self._generate_mouse_movements(timestamp)
            te = self._generate_mouse_movements(timestamp)
            md = self._generate_mouse_movements(timestamp)
            mu = self._generate_mouse_movements(timestamp)

            json = {
                'job_mode': job,
                'answers': answers,
                'serverdomain': 'kwik.cx',
                'sitekey': site_key,
                'motionData': {
                    'st': timestamp,
                    'dct': timestamp,
                    'ts': ts,
                    'te': te,
                    'mm': mm,
                    'md': md,
                    'mu': mu
                    },
                'n': None,
                'c': None
                }

            response = self.session.post(f'https://hcaptcha.com/checkcaptcha/{key}', json = json).json()
            bypassed = response.get("pass")
            logger.info(f"Bypassed: {bypassed}")

            if bypassed:
                Config._CONFIG["siteconfig"]["kwik"]["token"] = response.get("generated_pass_UUID")
                Config.write()
                logger.info(f"Token: {response.get('generated_pass_UUID')}")


    def _get_data(self):
        # Kwik servers don't have direct link access you need to be referred
        # from somewhere, I will just use the url itself. We then
        # have to rebuild the url. Hopefully kwik doesn't block this too

        #Necessary
        token = Config._CONFIG["siteconfig"]["kwik"]["token"]

        if token == "":
            self.bypass_captcha()
            token = Config._CONFIG["siteconfig"]["kwik"]["token"]

        self.url = self.url.replace(".cx/e/", ".cx/f/")

        resp = helpers.soupify(self.session.get(self.url, headers = self.headers))
        bypass_url = 'https://kwik.cx' + resp.form.get('action')

        data = {}
        [data.update({x.get("name"): x.get("value")}) for x in resp.select("form > input")]
        data.update({"id": resp.strong.text, "g-recaptcha-response": token, "h-captcha-response": token})

        #Returning 403, and challenge page.
        #Should return 200 and actual page.
        self.headers.update({"referer": self.url})
        resp = self.session.post(bypass_url, data = data, headers = self.headers)

        title_re = re.compile(r'title>(.*)<')

        #resp = self.session.post(self.url, headers={"referer": self.url})
        kwik_text = resp.text
        logger.debug(resp)

        title = title_re.search(kwik_text).group(1)

        deobfuscated = helpers.soupify(util.deobfuscate_packed_js(re.search(r'<(script).*(var\s+_.*escape.*?)</\1>(?s)', kwik_text).group(2)))

        post_url = deobfuscated.form["action"]
        token = deobfuscated.input["value"]

        resp = self.session.post(post_url, headers = self.headers, params={"_token": token}, allow_redirects = False)
        stream_url = resp.headers["Location"]

        logger.debug('Stream URL: %s' % stream_url)
        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': ''
            },
            'referer': None
        }
