import threading
import time

import dash
import warnings
import os
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc
from adasher.elements import header, footer
import logging

from eqa import __stats, __util as _u, __app_util as _a, __data, __submarine as _sub


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


warnings.filterwarnings("ignore")
warnings.simplefilter("ignore", UserWarning)

app = _a.get_app()
server = app.server

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True


# layout
layout = list()
layout.append(header('Earthquake analytics', 'left', 1))
layout.append(dcc.Interval(id='interval-progress', interval=1000, max_intervals=30*60))
layout.append(dbc.Progress(id='total_progress'))
layout.append(dcc.Interval(id='interval-component', interval=30*60*1000, n_intervals=0))
# layout.append(dcc.Loading(id="loading-1", type="default",
#                           children=[html.Div(id='all_tabs_content')]))
layout.append(html.Div(id='all_tabs_content', children=[__stats.get_all_tabs_content()]))

__tabs = [
    html.A(html.I(className="fa-brands fa-github"), href='https://github.com/bhanuchander210/earthquake_analytics'),
]
layout.append(footer([html.Div(children=__tabs, style={'text-align': 'center', 'margin': '5px'})],
                     style={'height': '30px'}))
app.layout = html.Div(children=layout, id='overall_page')


def fetch_init():
    threading.Thread(target=__stats.get_all_tabs_content, ).start()
    threading.Thread(target=_sub.get_cables,).start()


def get_fetch_pct():
    _pct_df, _ = __data.get_available_data_pct()
    _pct_cab = _sub.get_cables().get_cab_pct()
    _pct = (_pct_df + _pct_cab) / 2
    return _pct, 'Fetching {:.2f}'.format(_pct)


@app.callback(
    [Output("total_progress", "value"), Output("total_progress", "label"),
     Output("total_progress", "style")],
    [Input("interval-progress", "n_intervals")],
)
def update_progress(n):
    style = dict()
    _val, _lab = get_fetch_pct()
    if _val >= 100:
        style['display'] = 'none'
    return _val, _lab, style


@app.callback(Output('all_tabs_content', 'children'),
              Input('interval-component', 'n_intervals'), prevent_initial_call=True)
def update_pblm_table(n):
    _val, _ = get_fetch_pct()
    if _val < 100:
        return html.Div('Loading..', style={'margin': '50%'})
    _st = time.time()
    _content = __stats.get_all_tabs_content()
    _u.app_logger.info('Total loading time : {:.2f}'.format(time.time()-_st))
    return _content


if __name__ == '__main__':
    _u.init_utils()
    fetch_init()
    app.run_server(debug=False, port=8080, use_reloader=False, host='0.0.0.0')
