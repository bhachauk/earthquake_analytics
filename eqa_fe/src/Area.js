import React from 'react';
import PlotlyWidget from "./PlotlyWidget";
import {GetMetricURL} from "./Config";

function Area() {
    return (
        <div className="plotly-grid">
            <PlotlyWidget url={GetMetricURL("top_areas")}
                          title="Top Impacted Areas in last 90 days"/>
        </div>
    );
}

export default Area;