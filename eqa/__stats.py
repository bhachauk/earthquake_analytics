import threading

from eqa import __data, __util, __submarine, __app_util as _a
from eqa.__util import Period, Periods, Names
from eqa.__data import Cols

from adasher.advanced import auto_analytics
from adasher.templates import GROWTH_PIE_BAR_TREND, STATS
from adasher.elements import info, CardHeaderStyles, number_with_diff
from adasher.cards import card, container, stats_from_df
import plotly.graph_objs as go
import numpy as np


import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc, dash_table

_hs = CardHeaderStyles.WHITE_FONT_BLACK_BG
_gfwb = CardHeaderStyles.GRAY_FONT_WHITE_BG
init_check = False


def get_all_tabs_content_for_init():
    global init_check
    get_all_tabs_content()
    init_check = True


def get_all_tabs_content():
    __util.app_logger.info("Loading all contents ..!!!")
    content_dict = {
        'Home': [dcc.Loading(id="loading-home", children=[get_home_content()])],
        'Area': [dcc.Loading(id="loading-area", children=[get_area_content()])],
        # 'Insight': get_insight_content(),
        # 'Submarine cable 1': [dcc.Loading(id="loading-smc1", children=[__submarine.get_submarine_1_content()])],
        'Submarine cable': [dcc.Loading(id="loading-smc2", children=[__submarine.get_submarine_2_content()])],
    }

    tabs = list()
    for name, content in content_dict.items():
        tabs.append(dbc.Tab(id=name, children=content, label=name, tab_style={'font-size': '10px'}))

    return html.Div(children=[
        html.Div(info("Generated on : " + __util.now_formatted()), style={'position': 'absolute', 'top': 0, 'right': 0}),
        dbc.Tabs(id=__util.now_formatted(), children=tabs)
        ]
    )


def get_home_content():

    __content = [
        [(get_eq_globe_and_today_bar(), 4), (get_home_col_2(), 8)],
        # [(get_mag_summary(__util.Periods.get(Names.LM), header='Magnitude wise distribution'), 8),
        #  (get_type_summary(__util.Periods.get(Names.LM), header='Type wise distribution'), 4)],
    ]
    return container(__content)


def get_area_content():
    __content = [
        [(get_eq_area_heat(), 8), (get_eq_area_col2(), 4)],
        # [(get_eq_area_col2(), 12)],
    ]
    return container(__content)


def get_insight_content():
    __content = [
        [(get_mag_summary_insight(), 12)],
        [(get_type_summary_insight(), 12)]
    ]
    return container(__content)


def get_eq_globe_and_today_bar():
    _td_df = __data.get_td_df()
    _yd_df = __data.get_yd_df()
    _dbyd_df = __data.get_dbyd_df()

    _lm_avg = get_avg(__util.Periods.get(Names.LM))
    _pm_avg = get_avg(__util.Periods.get(Names.MBL))

    # return html.Div(children=[get_eq_globe_fig()])
    fs = 14
    _info_style = {'font-size': '10px', 'color': 'gray'}
    _hs = {'font-size': '14px'}

    return card('Stats',
                [
                    number_with_diff(len(_td_df), len(_yd_df), 'vs Yesterday', font_size=fs, is_positive_impact=False,
                                     header='Today so far', info_style=_info_style, header_style=_hs),
                    number_with_diff(len(_yd_df), len(_dbyd_df), 'vs Previous day', font_size=fs,
                                     is_positive_impact=False, header='Yesterday', info_style=_info_style, header_style=_hs),
                    number_with_diff(int(_lm_avg), int(_pm_avg), 'vs Previous 30 days', font_size=fs,
                                     is_positive_impact=False, header='30 days Avg/day', info_style=_info_style, header_style=_hs),
                    get_eq_globe_fig()
                 ], _gfwb)


def get_eq_globe_fig():
    _td_df = __data.get_lw_df().sort_values(by=Cols.MAG, ascending=False).head(20)
    scl = [0, 'rgb(100,0,0)'], [1, 'rgb(200,0,0)']
    fig = go.Figure(go.Scattergeo(
        lat=_td_df[Cols.LAT],
        lon=_td_df[Cols.LON],
        customdata=_td_df,
        hovertemplate="<b>%{customdata[4]}</b> <br> %{customdata[13]} <br> %{customdata[0]}<extra></extra>",
        mode='markers',
        marker_color='red',
        marker=dict(size=12)
    ))
    fig.update_layout(height=250, margin=dict(l=50, r=50, b=10, t=0), geo=dict(
            projection_type='orthographic',
            center_lon=-180,
            center_lat=0,
            projection_rotation_lon=-180,
            showland=True,
            showcountries=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        ),
        updatemenus=[dict(type='buttons', showactive=False,
                          y=1,
                          x=0,
                          xanchor='center',
                          yanchor='bottom',
                          pad=dict(t=0, r=0, l=0, b=5),
                          buttons=[dict(label='Play',
                                        method='animate',
                                        args=[None,
                                              dict(frame=dict(duration=100,
                                                              redraw=True),
                                                   transition=dict(duration=0),
                                                   fromcurrent=True,
                                                   mode='immediate')
                                              ])
                                   ])
                     ]
    )
    lon_range = np.arange(-180, 180, 2)
    frames = [go.Frame(layout=dict(geo_center_lon=lon,
                                   geo_projection_rotation_lon=lon
                                   )) for lon in lon_range]

    fig.update(frames=frames)
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def get_home_col_2():
    content = [
        dcc.Interval(id='eq_card_interval', interval=30 * 1000, n_intervals=0),
        dcc.Loading(id='eq_card_loader', children=[
            html.Div(id='eq_card_lm')
        ]),
        get_lm_mag_bar()
    ]
    return card('Strong Earthquake in recent times', content, _gfwb)


@_a.app.callback(
    Output('eq_card_lm', 'children'),
    Input('eq_card_interval', 'n_intervals')
)
def get_eq_card(_idx):
    _row = get_lm_eq_df_fmt().iloc[_idx]
    _pad_style = {'padding': '10px', 'color': 'white'}
    return html.Div(children=[

        html.Tr(children=[
            html.Td(html.Span(html.H3('{:.1f}'.format(float(_row['mag'])), style=_pad_style))),
            html.Td(children=[
                html.Span(_row['place'], style=_pad_style),
                html.Span(_row['time'], style=_pad_style),
            ]),
            html.Td(children=[
                html.Span("Depth: " + str(_row["depth"]), style=_pad_style)
            ])
        ])
    ], style={'align': 'left', 'background-color': __data.EQ_COLOR[int(np.floor(float(_row['mag'])))]})


def get_lm_eq_df_fmt():

    _key = 'get_lm_eq_df_fm'
    _df = __util.get_mem_cache(_key)
    if _df is not None:
        return _df
    _df = __data.get_lm_df().sort_values(by=Cols.MAG, ascending=False)
    for _col in [Cols.DEPTH, Cols.MAG]:
        _df[_col] = _df[_col].apply(lambda x: '{:.2f}'.format(x))
    _df[Names.TIME] = _df[Names.TIME].dt.strftime('%d %b, %H:%S')
    _df = _df[['time', 'mag', 'place', 'depth']]
    __util.put_mem_cache(_key, _df)
    return _df


def get_eq_table():
    df = __data.get_lm_df().sort_values(by=Cols.MAG, ascending=False)
    df['Location'] = '(' + df['latitude'].map(str) + df['longitude'].map(str) + ')'
    for _col in [Cols.DEPTH, Cols.MAG]:
        df[_col] = df[_col].apply(lambda x: '{:.2f}'.format(x))
    df[Names.TIME] = df[Names.TIME].dt.strftime('%d %b, %H:%S')
    df = df[['time', 'mag', 'place', 'Location', 'depth']]
    df.rename(columns={'place': 'Place', 'mag': 'Magnitude', 'depth': 'Depth', Names.TIME: 'Time'}, inplace=True)

    return dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={'textAlign': 'left', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        style_cell_conditional=[
            {'if': {'column_id': 'Place'},
             'width': '30%'},
        ]
    )


def get_eq_area_heat():
    content = [
        html.Div(children=[
            get_eq_area_heat_fig(),
            dbc.Alert("Divided into 324 Areas (18x18) for analytics with step sizes latitude: 10, longitude: 20",
                      color="secondary", style={'text-align': 'center', 'font-size': '10px'})
        ])
    ]
    return card("Last 30 Days Earthquakes with Area", content, _gfwb)


def get_eq_area_heat_fig(_td_df=None):
    _td_df = __data.get_lm_df()
    _td_df['mag_int'] = _td_df[Cols.MAG].astype(int)
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=_td_df[Cols.LAT],
        lon=_td_df[Cols.LON],
        customdata=_td_df,
        hovertemplate="<b>%{customdata[4]}</b> <br> %{customdata[13]} <br> %{customdata[0]}<extra></extra>",
        mode='markers',
        marker=dict(color=_td_df['mag_int'], colorscale='Reds')
    ))
    __area_list = get_eq_area_count_df(Names.LM).head(10)
    for _, _row in __area_list.iterrows():
        _x, _y = __util.LatLongSeparator.parse(_row[Cols.AREA])
        fig.add_trace(go.Scattergeo(lat=[_x, _x, _x+10, _x+10, _x], lon=[_y, _y+20, _y+20, _y, _y], mode='lines',
                                    line=dict(color='blue'), name=_row[Names.COUNT]))

    fig.update_geos(lataxis_dtick=10, lonaxis_dtick=20, lataxis_showgrid=True, lonaxis_showgrid=True)
    fig.update_layout(width=700, autosize=False, height=400, margin=dict(l=10, r=10, t=10, b=2), showlegend=False)
    fig.update_xaxes(automargin=False)
    fig.update_yaxes(automargin=False)
    return dcc.Graph(figure=fig, config={'displayModeBar': False, 'scrollZoom': True})


def get_eq_area_col2():
    return card('Top affected Areas', [get_eq_area_pie(), get_eq_area_bar()], _gfwb)


def get_eq_area_pie():
    __df = get_eq_area_count_df(Names.LM)
    _t_df = __df.head(4)
    _b_df = __df.tail(len(__df)-4)
    _t_df = _t_df.append({Cols.AREA: 'Others', Names.COUNT: _b_df[Names.COUNT].sum()}, ignore_index=True)
    fig = go.Figure(data=[go.Pie(labels=_t_df[Cols.AREA], values=_t_df[Names.COUNT])])
    fig.update_layout(margin=dict(l=5, r=5, t=5, b=5), height=200, showlegend=False)
    return dcc.Graph(figure=fig, config={'displayModeBar': False, 'scrollZoom': True})


def get_eq_area_bar():
    __df = get_eq_area_count_df(Names.LM).head(10)
    __p_df = get_eq_area_count_df(Names.MBL)
    __p_df = __p_df[__p_df[Cols.AREA].isin(list(__df[Cols.AREA].unique()))]

    fig = go.Figure()
    for _n, _df in [(Names.LM, __df), (Names.MBL, __p_df)]:
        fig.add_trace(go.Bar(x=_df[Cols.AREA], y=_df[Names.COUNT], name=_n))

    fig.update_layout(width=350, height=250, margin=dict(l=5, r=5, t=5, b=5),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis={'categoryorder': 'total descending'},
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                      )
    fig.update_yaxes(type="log")

    return dcc.Graph(figure=fig, config={'displayModeBar': False, 'scrollZoom': True})


def get_eq_area_count_df(_period):
    _td_df = __data.get_prep_df_with_area(__util.Periods.get(_period))
    __df = _td_df[[Cols.AREA]].groupby(Cols.AREA)\
        .size()\
        .reset_index(name=Names.COUNT)\
        .sort_values(by=Names.COUNT, ascending=False)
    return __df


def get_avg(tp: Period):
    _m_df = __data.get_prep_df(tp)[[Names.TIME]]
    _m_df[Names.TIME] = _m_df[Names.TIME].dt.date
    _m_df = _m_df.groupby(Names.TIME).size().reset_index(name=Names.COUNT)
    return _m_df[Names.COUNT].mean()


def get_mag_summary(tp: Period, template=STATS, header=None):
    _df = __data.get_prep_df(tp)
    _df[Cols.MAG] = _df[Cols.MAG].astype(int)
    return auto_analytics(_df, by=Cols.MAG, date_column=('time', __util.UTC_TIME_FORMAT), target_period=tp,
                          header=header, template=template,
                          header_style=CardHeaderStyles.WHITE_FONT_BLACK_BG, template_args=dict(header=" "))


def get_lm_mag_bar():
    fig = go.Figure()
    for tp_name in [Names.LM, Names.MBL]:
        tp = Periods.get(tp_name)
        _df = __data.get_prep_df(tp)[[Cols.MAG]]
        _df[Cols.MAG] = _df[Cols.MAG].astype(int)
        _df = _df.groupby([Cols.MAG]).size().reset_index(name=Names.COUNT)
        _df['HOVER'] = "Mag: " + _df[Cols.MAG].map(str) + " : " + _df[Names.COUNT].map(str)
        fig.add_trace(go.Bar(x=_df[Cols.MAG].map(str), y=_df[Names.COUNT], hovertext=_df['HOVER'], name=tp_name))
    fig.update_yaxes(type="log", title="No of Earthquakes")
    fig.update_layout(margin=dict(l=5, b=50, r=5, t=5), xaxis=dict(title='Magnitude'),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      height=300
                      )
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def get_mag_summary_insight():
    return get_mag_summary(__util.Periods.get(Names.LM), GROWTH_PIE_BAR_TREND, 'Magnitude stats for %s ' % Names.LM)


def get_type_summary(tp: Period, template=STATS, header=None):
    _df = __data.get_prep_df(tp)
    return auto_analytics(_df, by=Names.TYPE, date_column=('time', __util.UTC_TIME_FORMAT), target_period=tp,
                          header=header, template=template, header_style=CardHeaderStyles.WHITE_FONT_BLACK_BG,
                          template_args=dict(header=" "))


def get_type_summary_insight():
    return get_type_summary(__util.Periods.get(Names.LM), GROWTH_PIE_BAR_TREND, 'Type stats for %s ' % Names.LM)


if __name__ == '__main__':
    __lm_df = get_eq_area_count_df(Names.LM).head(10)
    for x in __lm_df[Cols.AREA]:
        print(x)
        print(__util.LatLongSeparator.parse(x))
    pass
