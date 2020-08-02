from abc import ABCMeta, abstractmethod, abstractproperty

import os
import subprocess
import logging

logger = logging.getLogger(__name__)


class BasePlayer(metaclass=ABCMeta):
    name = ''

    STOP = 50
    NEXT = 51
    PREV = 52

    @abstractmethod
    def _get_executable_windows():
        return

    @abstractmethod
    def _get_executable_posix():
        return

    @abstractproperty
    def args():
        '''
        Args return a list of arguments to be passed to player.
        One of the arguments should be `{stream_url}` which will be replaced
        while calling the script.
        '''
        return

    def __init__(self, episode):
        # TODO: Stream urls is a list of urls for now
        # It should be a list of seperate class with title and other metadata
        self.episode = episode

    def _get_executable(self):
        if os.name == 'nt':
            # Windows
            return self._get_executable_windows()
        else:
            return self._get_executable_posix()

    def play(self):
        cmd = [self._get_executable()] + self.args
        logger.debug('Command: {}'.format(cmd))
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        returncode = self.process.wait()

        return returncode
