import numpy as np
import pandas as pd
import os
import urllib.parse
from eqa import __util
from eqa.__util import Names
import datetime
import glob
from urllib.request import urlopen
import json

from adasher.data_utils import Period, Periods

TOTAL_DATES = 90
EQ_DATA_DIR = os.path.join(__util.data_dir, 'EQ_DATA')
CACHE_DIR = os.path.join(__util.data_dir, 'cache')

# EQ_COLOR = {
#     2: '#FA8072',
#     3: '#E9967A',
#     4: '#CD5C5C',
#     5: '#DC143C',
#     6: '#B22222',
#     7: '#8B0000',
# }
EQ_COLOR = {
    2: '#ccc',
    3: '#bbb',
    4: '#aaa',
    5: '#999',
    6: '#888',
    7: '#777',
}


def get_eq_color(_val):
    _val = int(np.floor(float(_val)))
    return EQ_COLOR[min(2, max(_val, 7))]


class Cols:
    LAT = 'latitude'
    LON = 'longitude'
    MAG = 'mag'
    PLACE = 'place'
    AREA = 'area'
    DEPTH = 'depth'
    PT = 'point'
    ID = 'id'
    UID = 'uid'


def get_url(**kwargs):
    usgs_url = 'https://earthquake.usgs.gov/fdsnws/event/1/query?'
    kwargs.update({'format': 'csv', 'minmagnitude': 2})
    return usgs_url + urllib.parse.urlencode(kwargs)


def get_all_dates():
    return [__util.today_start() - datetime.timedelta(days=t + 1) for t in range(TOTAL_DATES)]


def get_all_files_dates():
    __all_dates = get_all_dates()
    __all_dates.append(__util.today_start())
    return [__util.formatted(_t) for _t in __all_dates]


def get_file_path(_date_str):
    return os.path.join(EQ_DATA_DIR, _date_str + '.csv')


def clear_old_data():
    __valid_files = get_all_files_dates()
    for f in os.listdir(EQ_DATA_DIR):
        try:
            __file_path = os.path.join(EQ_DATA_DIR, f)
            if f[:10] not in __valid_files and os.path.exists(__file_path):
                os.remove(__file_path)
        except e:
            pass


def get_available_data_pct():
    _val = (len(os.listdir(EQ_DATA_DIR)) / (TOTAL_DATES + 1)) * 100
    return _val, "Fetching {:.2f} %".format(_val)


def collect_data():
    __util.create_dir_if_not_exists(EQ_DATA_DIR)

    for d in get_all_dates():
        _start, _end = __util.formatted(d), __util.formatted(d + datetime.timedelta(days=1))
        _file_path = get_file_path(_start[:10])
        if os.path.exists(_file_path):
            continue
        _url = get_url(starttime=_start, endtime=_end)
        pd.read_csv(_url).to_csv(_file_path, index=False)

    _start = __util.formatted(__util.today_start())
    _file_path = get_file_path(_start[:10])
    _url = get_url(starttime=_start)
    pd.read_csv(_url).to_csv(_file_path, index=False)


def get_df():
    collect_data()
    clear_old_data()
    # __dtype = dict()
    __dtype = {
        Cols.LAT: 'float16',
        Cols.LON: 'float16',
        Cols.DEPTH: 'float16',
        Cols.MAG: 'float16',
        'magType': 'str',
        'horizontalError': 'float16',
        'depthError': 'float16',
        'magError': 'float16',
        'magNst': 'float16',
    }

    __dfs = list()
    for _f in glob.glob(os.path.join(EQ_DATA_DIR, '*.csv')):
        try:
            __dfs.append(pd.read_csv(_f, dtype=__dtype))
        except Exception as e:
            print(e)
            print(_f)
            print(e.__traceback__)
            pass
    return pd.concat(__dfs)


def __mag_fmt(val):
    return "{:.1f}".format(val)


def get_prep_df(period: __util.Period):
    _df = get_df()
    _prev_period = Periods.get_prev_period(period)
    _df[Names.TIME] = _df[Names.TIME].apply(lambda x: x[:19])
    _df[Names.TIME] = pd.to_datetime(_df[Names.TIME], format=__util.UTC_TIME_FORMAT)
    _t_df = _df[(_df[Names.TIME] >= _prev_period.start) & (_df[Names.TIME] < period.end)].copy()
    _t_df[Cols.UID] = _t_df[Cols.MAG].map(__mag_fmt) + " - " + _t_df[Names.TIME].dt.strftime('%d %B %y') \
                      + " - " + _t_df[Cols.PLACE].map(str)
    del _df
    return _t_df


def get_lm_df():
    return __get_period_df(Names.LM)


def get_lw_df():
    return __get_period_df(Names.LW)


def get_pm_df():
    return __get_period_df(Names.MBL)


def get_td_df():
    return __get_period_df(Names.TD)


def get_yd_df():
    return __get_period_df(Names.YD)


def get_dbyd_df():
    return __get_period_df(Names.DBYD)


def __get_period_df(_p: str):
    return get_prep_df(__util.Periods.get(_p))


def get_prep_df_with_area(period: __util.Period, lat_step=10, lon_step=20):
    _df = get_prep_df(period)
    _lat_lon_sep = __util.LatLongSeparator(lat_step, lon_step)
    _df[Cols.AREA] = _df.apply(lambda x: _lat_lon_sep.get_box_label(x[1], x[2]), axis=1)
    return _df


def getplace(lat, lon):
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false" % (lat, lon)
    v = urlopen(url).read()
    j = json.loads(v)
    components = j['results'][0]['address_components']
    country = town = None
    for c in components:
        if "country" in c['types']:
            country = c['long_name']
        if "postal_town" in c['types']:
            town = c['long_name']
    return town, country


def get_cache_file_path(_dir, _id, _ext='.npy'):
    __cache_dir = os.path.join(CACHE_DIR, _dir)
    __util.create_dir_if_not_exists(__cache_dir)
    __file_name = _id + __util.today_str() + _ext
    return os.path.join(__cache_dir, __file_name)


def get_cache_file(_dir, _id):
    __cache_dir = os.path.join(CACHE_DIR, _dir)
    __file_path = get_cache_file_path(_dir, _id)

    # flush old files
    [os.remove(os.path.join(__cache_dir, _f))
     for _f in os.listdir(__cache_dir)
     if __util.today_str() not in _f]

    try:
        return np.load(__file_path, allow_pickle=True).item() if os.path.exists(__file_path) else None
    except Exception as e:
        return None


if __name__ == '__main__':
    __util.init_utils()
    collect_data()
    clear_old_data()
    _df = get_df()
    _df['country'] = _df.apply(lambda x: getplace(x[1], x[2]), axis=1)
    _df.head().to_csv('sample.csv', index=False)
