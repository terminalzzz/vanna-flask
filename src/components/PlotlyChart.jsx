import React, { useEffect, useRef } from 'react';

const PlotlyChart = ({ figJson }) => {
  const plotRef = useRef(null);

  useEffect(() => {
    if (figJson && plotRef.current) {
      // Dynamically import Plotly to avoid SSR issues
      import('plotly.js/dist/plotly.js').then((Plotly) => {
        const fig = JSON.parse(figJson);
        Plotly.newPlot(plotRef.current, fig.data, fig.layout, { responsive: true });
      }).catch((error) => {
        console.error('Error loading Plotly:', error);
      });
    }
  }, [figJson]);

  return (
    <div className="max-w-full bg-white rounded-lg p-4" style={{ width: '600px', height: '400px' }}>
      <div ref={plotRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
};

export default PlotlyChart;