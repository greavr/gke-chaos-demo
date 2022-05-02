import React, { useState, useEffect, useRef } from 'react';
import './chart.scss';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top',
      align: 'end',
      padding: 20
    },
  },
};

const Chart = props => {
  const {labels, chartData} = props
  const [data, setData] = useState({
    labels,
    datasets: [
      {
        label: 'Load',
        data: chartData,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
    ],
  })

  // Update chart data when labels OR chartData has changed
  // from theparent LoadGenerator.js component, then update chart
  useEffect(() => {
    setData({
      labels,
      datasets: [
        {
          label: 'Load',
          data: chartData,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
        },
      ],
    })
  }, [labels, chartData])

  return (
    <div className='chart'>
      <Line className='chart__canvas' options={options} data={data} />
    </div>
  )
}

export default Chart;