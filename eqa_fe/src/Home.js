import React from 'react';
import PlotlyWidget from "./PlotlyWidget";
import {GetMetricURL} from "./Config";

function Home() {
    return (
        <div className="plotly-grid">
            <PlotlyWidget url={GetMetricURL("top_n_today")} title="Today: Top 10"/>
            <PlotlyWidget url={GetMetricURL("last_n_days_dist")}
                          title="Magniture Distribution: Last 30 Days vs Previous"/>
            {/* Add more PlotlyWidgets as needed */}
        </div>
    );
}

export default Home;