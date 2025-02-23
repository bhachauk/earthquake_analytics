import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

function PlotlyWidget({ url, title }) {
    const [graphData, setGraphData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await axios.get(url);
                const data = JSON.parse(response.data);
                setGraphData(data);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [url]);

    return (
        <div className="plotly-widget-container">
            {title && <h3 className="plotly-widget-title">{title}</h3>}
            <div className="plotly-widget-content">
                {loading && (
                    <div className="plotly-widget-loading">
                        <div className="loading-spinner"></div>
                    </div>
                )}
                {error && <div className="plotly-widget-error">Error loading graph: {error.message}</div>}
                {!loading && !error && graphData && (
                    <div className="plotly-widget">
                        <Plot data={graphData.data} layout={graphData.layout} config={{ responsive: false }} />
                    </div>
                )}
                {!loading && !error && !graphData && <div className="plotly-widget-error">No graph data received.</div>}
            </div>
        </div>
    );
}

export default PlotlyWidget;