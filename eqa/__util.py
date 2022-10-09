import os
import logging
from logging.handlers import RotatingFileHandler
import time
import psutil
import numpy as np

from dateutil import rrule
from datetime import datetime, timedelta
from adasher.data_utils import Period

conf = None
data_dir = 'data'
app_logger = logging.getLogger('init')
mem_caches = dict()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
UTC_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def create_dir_if_not_exists(in_dir):
    if not os.path.exists(in_dir):
        os.makedirs(in_dir)


def init_logging(logger, file_name, size_in_mb, back_up_count):
    """
    :param logger:
    :param file_name
    :param size_in_mb:
    :param back_up_count:
    :return:
    """
    logging_fmt = '%(asctime)-15s : %(filename)s:%(lineno)s : %(funcName)s() : %(message)s'
    logging_dt_fmt = '%m/%d/%Y %I:%M:%S %p'
    create_dir_if_not_exists(data_dir)
    log_file = os.path.join(data_dir, file_name)
    log_formatter = logging.Formatter(logging_fmt, datefmt=logging_dt_fmt)
    log_handler = RotatingFileHandler(log_file, mode='a', maxBytes=size_in_mb * 1024 * 1024, backupCount=back_up_count,
                                      encoding=None, delay=0)
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    logger.info("Logs inited with size_in_mb : {}, back_up_count: {}".format(size_in_mb, back_up_count))


class Logger:
    def __init__(self, name, file_name, size_in_mb=1, back_up_count=2):
        self.logger = logging.getLogger(name)
        init_logging(self.logger, file_name, size_in_mb, back_up_count)
        self.logger.info("Inited logger : {}".format(name))


def init_utils():
    global app_logger
    app_logger = Logger('common', 'log.out').logger


def today_start():
    today = datetime.today()
    return today.replace(hour=0, minute=0, second=0, microsecond=0)


def elap(f):
    def wrap(*args, **kwargs):
        global app_logger
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        app_logger.info('{:s} function took {:.4f} sec'.format(f.__name__, time2 - time1))
        return ret

    return wrap


def curr_mem(msg=None):
    global app_logger
    process = psutil.Process(os.getpid())
    current = process.memory_info().rss
    app_logger.info("CPUMemLog pid : {}, mem: {}, cpu : {}, mem_readable: {}, msg : {}".format(str(os.getpid()),
                                                                                               str(current),
                                                                                               str(process.cpu_percent(
                                                                                                   interval=0.1)),
                                                                                               str(psutil._common.bytes2human(
                                                                                                   current)),
                                                                                               str(msg)))


def now_formatted():
    return formatted(datetime.now(), UTC_TIME_FORMAT)


def today_str():
    return formatted(today_start())


def formatted(_time, __format=DATE_FORMAT):
    return _time.strftime(__format)


class Names:
    YD = 'Yesterday'
    TD = 'Today'
    DBYD = 'Day before Yesterday'
    LW = 'Last week'
    WBL = 'Week before last'
    LM = 'Last 30 Days'
    MBL = '30 Days before last'

    TIME = 'time'
    TYPE = 'type'
    COUNT = 'count'


class Periods:

    @staticmethod
    def get(tp):
        tps = dict()
        tps[Names.TD] = Period(today_start(), datetime.now(), Names.TD)
        tps[Names.YD] = Period(today_start() - timedelta(days=1), today_start(), Names.YD)
        tps[Names.DBYD] = Period(today_start() - timedelta(days=2), today_start() - timedelta(days=1), Names.DBYD)
        tps[Names.LW] = Period(today_start() - timedelta(days=7), today_start(), Names.LW)
        tps[Names.LM] = Period(today_start() - timedelta(days=30), today_start(), Names.LM)
        tps[Names.LM] = Period(today_start() - timedelta(days=30), today_start(), Names.LM)
        tps[Names.WBL] = Period(today_start() - timedelta(days=14), today_start() - timedelta(days=7), Names.WBL)
        tps[Names.MBL] = Period(today_start() - timedelta(days=60), today_start() - timedelta(days=30), Names.MBL)
        return tps.get(tp, None)


class LatLongSeparator:
    lat_min_max = (-90, 90)
    long_min_max = (-180, 180)

    def __init__(self, lat_step, lon_step):
        if lat_step > 90 or lon_step > 180:
            raise Exception("Min values of box ranges (<= 90, <=180)")
        self.lats = np.arange(*self.lat_min_max, lat_step)
        self.lons = np.arange(*self.long_min_max, lon_step)
        self.lat_step = self.lats[1] - self.lats[0]
        self.lon_step = self.lons[1] - self.lons[0]
        if not isinstance(self.total(), int):
            raise Exception("Invalid box shape as total separation : %d" % self.total())

    def get_box_label(self, _lat, _long):
        return "Area:({},{})".format(*self.get_box_val(_lat, _long))

    def get_box_val(self, _lat, _long):
        return max([x for x in self.lats if x <= _lat]), max([x for x in self.lons if x <= _long])

    def total(self):
        return len(self.lats) * len(self.lons)

    @staticmethod
    def parse(_val):
        return [float(x) for x in _val[:-1].replace("Area:(", "").split(',')]


def get_mem_cache(_id):
    global mem_caches
    if _id not in mem_caches.keys():
        return None
    _expired = [k for k in mem_caches[_id].keys() if k != today_str()]
    for _k in _expired:
        del mem_caches[_id][_k]
    return mem_caches[_id][today_str()] if today_str() in mem_caches[_id].keys() else None


def put_mem_cache(_id, _obj):
    global mem_caches
    mem_caches[_id] = dict()
    mem_caches[_id][today_str()] = _obj
