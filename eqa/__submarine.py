import os
import time

import pandas as pd
import plotly.graph_objs as go
import requests
import threading
import geopandas as gpd
import numpy as np
import shapely.geometry
from shapely.geometry import Point, LineString, MultiLineString
from pyproj import Geod
from dash import Input, Output, html, dcc, dash_table

from eqa import __data as _d, __util as _u, __app_util as _a
from eqa.__data import Names, Cols
from adasher.cards import container, card
from adasher.elements import CardHeaderStyles


BASE_URL = 'https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/'

__cables = None
__landing_points = None
_gfwg = CardHeaderStyles.GRAY_FONT_WHITE_BG


def create_dir(_dir):
    if not os.path.exists(_dir):
        os.mkdir(_dir)


def distance(_x: Point, _y: Point):
    return Geod(ellps="WGS84").geometry_length(LineString([_x, _y]))


def close_pt(_line: MultiLineString, _y: Point):
    _dist = _y.distance(_line)
    return _line.interpolate(_line.project(_y))


def distance_bw(_line: MultiLineString, _y: Point):
    return distance(close_pt(_line, _y), _y)


class TeleData:

    def __init__(self, dir, gjson_file_name, use_cache=True):
        self.dir = dir
        self.gjson_file_name = gjson_file_name
        self.g_df = None
        self.features = dict()
        self.is_cache = use_cache
        if self.is_cache:
            self._cache_all()
            return
        self.fetch_all_data()

    def fetch_all_data(self):
        self._fetch_df()

    def _cache_all(self):
        if os.path.exists(self.gjson_file_name):
            self.g_df = gpd.read_file(self.__get_gjson_url())
            return

        self._fetch_df()
        with open(self.gjson_file_name, 'w') as f:
            f.write(self.g_df.to_json())

    def _cache_file(self, _id):
        __data = self.get_feature(_id)
        with open(self.__file_path(_id), 'w') as f:
            f.write(__data)

    def _fetch_df(self):
        st = time.time()
        self.g_df = gpd.read_file(self.__get_gjson_url())
        _u.app_logger.info(
            'Fetching data from remote for : {} time {:.2f} sec'.format(self.gjson_file_name, time.time() - st))

    def get_feature(self, _id):
        if _id in self.features.keys():
            return self.features[_id]
        create_dir(self.dir)
        __data = requests.get(self.__get_file_url(_id)).json()
        self.features[_id] = __data
        return __data

    def __file_name(self, _id):
        return _id + '.json'

    def __gson_path(self):
        return os.path.join(self.dir, self.gjson_file_name)

    def __file_path(self, _id):
        return os.path.join(self.dir, self.__file_name(_id))

    def __get_gjson_url(self):
        return BASE_URL + self.dir + '/' + self.gjson_file_name

    def __get_file_url(self, _id):
        return BASE_URL + self.dir + '/' + self.__file_name(_id)


class Cables(TeleData):

    def __init__(self):
        TeleData.__init__(self, 'cable', 'cable-geo.json')
        self.EQ_RADIUS = 2000 * 1000
        self.eq_df = get_lm_eq_df()
        self.for_date = _u.today_str()
        self.cab_eq_map = dict()

        # head only
        # self.g_df = self.g_df.head(100)
        self.__add_eq_count()

    def get_lat_lon_names(self, filter_names: list):
        lats = []
        lons = []
        names = []

        _df = self.g_df[self.g_df['name'].isin(filter_names)]
        for feature, name in zip(_df.geometry, _df.name):
            if isinstance(feature, shapely.geometry.linestring.LineString):
                linestrings = [feature]
            elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
                linestrings = feature.geoms
            else:
                continue
            for linestring in linestrings:
                x, y = linestring.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                names = np.append(names, [name] * len(y))
                lats = np.append(lats, None)
                lons = np.append(lons, None)
                names = np.append(names, None)
        return lats, lons, names

    def __add_eq_count(self):
        __st = time.time()
        self.g_df[Names.COUNT] = self.g_df[Cols.ID].apply(lambda x: len(self.get_lm_eq_df(x)))
        self.g_df = self.g_df.sort_values(by=Names.COUNT, ascending=False)
        _u.app_logger.info("Total time taken to compute eq count in cables df: {:.2f} sec".format(time.time() - __st))

    def get_lm_eq_df(self, _id) -> pd.DataFrame:
        if _id in self.cab_eq_map.keys():
            return self.eq_df[self.eq_df.index.isin(list(self.cab_eq_map[_id]))]

        __cache_file = _d.get_cache_file_path(self.dir, _id)
        if self.is_cache and os.path.exists(__cache_file):
            __cach_kv = _d.get_cache_file(self.dir, _id)
            self.cab_eq_map.update(__cach_kv)
            return self.eq_df[self.eq_df.index.isin(__cach_kv[_id])]

        _st = time.time()
        _ml_str = self.g_df[self.g_df[Cols.ID] == _id]['geometry'].iloc[0]
        self.eq_df['dist'] = self.eq_df[Cols.PT].apply(lambda x: distance_bw(_ml_str, x))
        __eq_df = self.eq_df[self.eq_df['dist'] <= self.EQ_RADIUS]
        self.cab_eq_map[_id] = list(__eq_df.index)
        np.save(__cache_file, {_id: list(__eq_df.index)}, allow_pickle=True)
        _u.app_logger.info("Time taken to fetch eq for id : " + _id + ", " + "{:.2f} sec".format(time.time() - _st))
        return __eq_df


class LandingPoints(TeleData):

    def __init__(self):
        TeleData.__init__(self, 'landing-point', 'landing-point-geo.json')


class EQCablesOut:

    def __init__(self, df: pd.DataFrame, fig):
        self.df = df
        self.size = len(df)
        self.fig = fig
        self.__format_df()

    def __format_df(self):
        self.df = self.df[['distance_km', 'name']]
        _empty_lines = 5 if self.df.empty else 5-(len(self.df) % 5) if len(self.df) % 5 != 0 else 0
        for _ in range(_empty_lines):
            self.df = self.df.append({'distance_km': '', 'name': ''}, ignore_index=True)
        self.df.rename(columns={'distance_km': 'Distance (km)', 'name': 'Cable name'}, inplace=True)


def get_cables() -> Cables:
    global __cables
    if __cables is None or __cables.for_date != _u.today_str():
        __cables = Cables()
        _u.app_logger.info("new cable instance created.")
    return __cables


def get_landing_points() -> LandingPoints:
    global __landing_points
    if __landing_points is None:
        __landing_points = LandingPoints()
    return __landing_points


def init():
    schedule_update()


def load_data(delay=60 * 60 * 24):
    while True:
        st = time.time()
        get_cables()
        get_landing_points()
        print('fetch time : ', time.time() - st)
        time.sleep(delay)


def schedule_update():
    threading.Thread(target=load_data).start()


def get_finalized_cables_out(_pt, _eq_name='Earthquake') -> EQCablesOut:
    _cab_df = get_all_near_cables(_pt)
    fig = go.Figure(data=go.Scattergeo(lat=[_pt.y], lon=[_pt.x], mode='markers',
                                       marker=dict(size=25, color='red'),
                                       showlegend=False, name=_eq_name))
    fig = get_cabs_fig(list(_cab_df['name']), fig)
    for _, _row in _cab_df.iterrows():
        _c_pt = _row['np']
        fig.add_trace(go.Scattergeo(name=_row['distance_km'], lat=[_c_pt.y], lon=[_c_pt.x], mode='markers',
                                    marker=dict(size=10, color='coral'), showlegend=False))

    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0),
                      title=_eq_name,
                      geo=dict(
                          projection_scale=5,  # this is kind of like zoom
                          center=dict(lat=_pt.y, lon=_pt.x),
                      ), height=300)
    return EQCablesOut(_cab_df, fig)


def get_cabs_fig(cab_names: list, fig=go.Figure()):
    if not cab_names:
        return fig
    cables = get_cables()
    lats, lons, names = cables.get_lat_lon_names(cab_names)
    fig.add_trace(go.Scattergeo(lat=lats, lon=lons, hovertext=names, mode='lines', showlegend=False))
    return fig


def get_all_near_cables(_pt: Point, proximity=2000 * 1000) -> gpd.GeoDataFrame:
    __df = get_cables().g_df
    __df['dist'] = __df['geometry'].apply(lambda x: distance_bw(x, _pt))
    __df['np'] = __df['geometry'].apply(lambda x: close_pt(x, _pt))
    __df = __df[__df['dist'] <= proximity]
    __df = __df.sort_values(by=['dist'], ascending=True)
    __df['distance_km'] = __df['dist'].apply(lambda x: '{:.2f} km'.format(x / 1000))
    return __df


# dev methods

def get_random_cable_names() -> list:
    __df = get_cables().g_df
    return list(__df['name'].sample(5))


def get_random_point() -> Point:
    return Point(np.random.randint(-180, 180), np.random.randint(-90, 90))


def get_lm_eq_df():
    _df = _d.get_lm_df()
    _df[Cols.PT] = _df.apply(lambda x: Point(x[Cols.LON], x[Cols.LAT]), axis=1)
    return _df


# submarine 1 contents
def get_submarine_1_content():
    return container([
        [(get_affected_cables_count_stats(), 6), (get_cable_eq_card(), 6)],
        [(get_top_affected_cables_bar(), 6)]
    ])


def get_affected_cables_count_stats():
    __content = list()
    __cab = get_cables().g_df
    __f_cab = __cab[__cab[Names.COUNT] > 0]
    val = (len(__f_cab) / len(__cab)) * 100
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=['', ''], values=[val, 100-val], hole=0.85, textinfo='none', hoverinfo='none',
                         marker_colors=['rgb(113,209,145)', 'rgb(240,240,240)']))
    fig.update_layout(showlegend=False, height=300, width=300, margin=dict(l=0, r=0, b=0, t=0), autosize=False,
                      annotations=[dict(text=str(val)+"%", x=0.5, y=0.5, font_size=20, showarrow=False)])
    __content.append(html.Div(dcc.Graph(figure=fig, config={'displayModeBar': False, 'scrollZoom': True}),
                              style={'width': '300px'}))
    __content.append(html.H5("{} / {}".format(str(len(__f_cab)), str(len(__cab)))))
    return card('Last 30 days affected cables stats', __content, _gfwg)


def get_top_affected_cables_bar():
    __content = list()
    return card('Last 30 days top affected cables', __content, _gfwg)


def get_cable_eq_card():
    __content = list()
    return card('Affected cable', __content, _gfwg)


# submarine 2 contents
def get_submarine_2_content():
    __uids = list(get_lm_eq_df()[Cols.UID])
    __container = container([
        [(dcc.Dropdown(__uids, __uids[0], id='eq-dropdown', style={'margin': '15px'}), 6),
         (html.Div(), 6)
         ]
    ])
    return html.Div(children=[
        __container,
        card('Nearby submarine cables', [dcc.Loading(children=[html.Div(id='submarine-eq-cab-output-content')])],
             CardHeaderStyles.GRAY_FONT_WHITE_BG)
        ])


def get_cables_to_eq_stats():
    __cab_df = get_cables().g_df
    __cab_names = list(__cab_df['name'])
    return html.Div(children=[
        dcc.Dropdown(__cab_names, __cab_names[0], id='cab-dropdown'),
        html.Div(id='submarine-cab-eq-output-content')
    ])


@_a.app.callback(
    Output('submarine-eq-cab-output-content', 'children'),
    Input('eq-dropdown', 'value')
)
def __get_submarine_content(_eq_uname):
    __eq_df = get_lm_eq_df()
    _pt = __eq_df[__eq_df[Cols.UID] == _eq_uname][Cols.PT].iloc[0]
    eq_out = get_finalized_cables_out(_pt, _eq_uname)

    __eq_cabs_fig = dcc.Graph(figure=eq_out.fig, config={'displayModeBar': False, 'scrollZoom': True})
    __cab_tab = html.Div(children=[
        html.Span(eq_out.size, style={'color': 'blue', 'float': 'left', 'margin-right': '15px', 'font-size': '50px'}),
        html.P("near by submarine cables found within 2000 km radius around the earthquake.".format(str(eq_out.size)),
               style={'padding': '20px 10px 0px'}),
        dash_table.DataTable(data=eq_out.df.to_dict('records'),
                             columns=[{"name": i, "id": i} for i in eq_out.df.columns],
                             style_cell={'textAlign': 'left'}, page_size=5,
                             style_table={'minWidth': '100%', 'overflowX': 'scroll'}
                             )
    ])
    __tabs = html.Div(children=[__cab_tab, html.Br()])
    __content = [
        [(__eq_cabs_fig, 6),
         (__tabs, 6)
         ]
    ]
    return container(__content)


@_a.app.callback(
    Output('submarine-cab-eq-output-content', 'children'),
    Input('cab-dropdown', 'value')
)
def __get_submarine_cab_eq_content(_cab_name):
    __cabs = get_cables()
    __cab_df = __cabs.g_df[__cabs.g_df['name'] == _cab_name]
    __id = __cab_df[Cols.ID].iloc[0]
    __df = __cabs.get_lm_eq_df(__id)[[Cols.UID]]
    return html.Div(children=[
        # dcc.Graph(figure=eq_out.fig),
        dash_table.DataTable(data=__df.to_dict('records'),
                             columns=[{"name": i, "id": i} for i in __df.columns],
                             style_cell={'textAlign': 'left'})
    ])


if __name__ == '__main__':
    _u.init_utils()
    # lps = get_landing_points()
    # print(lps.g_df.head())
    cabs = get_cables()
    print(cabs.g_df.head())
    pass
