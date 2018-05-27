import logging
import sys
import time

def setup_logger(log_level):
    if log_level == 'DEBUG':
        format = '%(levelname)s %(name)s: %(message)s'
    else:
        format = '%(levelname)s:%(message)s'

    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format=format
    )


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
