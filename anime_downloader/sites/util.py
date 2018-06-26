import logging
import requests
import re
import os
import errno
from bs4 import BeautifulSoup

from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.const import desktop_headers


def get_json(url, params=None):
    logging.debug('API call URL: {} with params {!r}'.format(url, params))
    res = requests.get(url, headers=desktop_headers, params=params)
    logging.debug('URL: {}'.format(res.url))
    data = res.json()
    logging.debug('Returned data: {}'.format(data))

    return data


def get_stream_url_rapidvideo(url, quality, headers):
    # TODO: Refractor this into a EmbedUrlProcessor
    url = url+'&q='+quality
    logging.debug('Calling Rapid url: {}'.format(url))
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    title_re = re.compile(r'"og:title" content="(.*)"')
    image_re = re.compile(r'"og:image" content="(.*)"')

    ret_dict = dict()
    try:
        ret_dict['stream_url'] = soup.find_all('source')[0].get('src')
    except IndexError:
        raise NotFoundError("Episode not found")
    try:
        ret_dict['title'] = str(title_re.findall(r.text)[0])
        ret_dict['image'] = str(image_re.findall(r.text)[0])
    except Exception as e:
        ret_dict['title'] = ''
        ret_dict['image'] = ''
        logging.debug(e)
        pass

    return ret_dict


def slugify(file_name):
    file_name = str(file_name).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', file_name)


def format_filename(filename, epiosde):
    rep_dict = {
        'anime_title': slugify(epiosde._parent.title),
        'ep_no': epiosde.ep_no,
    }

    filename = filename.format(**rep_dict)

    return filename


def make_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
