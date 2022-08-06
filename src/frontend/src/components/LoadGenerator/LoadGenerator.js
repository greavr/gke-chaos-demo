import React, { useState, useEffect } from 'react';
import './load-generator.scss';
import Chart from './Chart/Chart';
import Button from '../Button/Button';
import axios from 'axios';

const today = new Date();

const LoadGenerator = () => {
  // Variables
  const [buttonPending, setButtonPending] = useState(false);
  const [currentLoad, setCurrentLoad] = useState(100);
  const [chartData, setChartData] = useState([100]);
  const [chartTime, setChartTime] = useState([today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds()]);

  // Function that runs once when conponent is loaded
  useEffect(() => {
    setInterval(() => {
      handleGetLoad();
    }, 5000);
  }, [])

  // Handle generate load
  const handleGenerateLoad = () => {
    // Disable button click while processing
    setButtonPending(true);
    axios.get('/increase-load')
    .then(() => {
      // Handle success
      // Get button back to active
      setButtonPending(false);
      // Get and display current load
      handleGetLoad();
    })
  }

  // Get current load data every 5 seconds
  const handleGetLoad = () => {
    axios.get('/get-load')
    .then(response => {
      // handle success
      // Update load data
      setCurrentLoad(response.data.current_load);
      setChartData(chartData => [...chartData, response.data.current_load]);
      // Update time
      setChartTime(chartTime => [...chartTime, today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds()]);
    })
  }

  return (
    <div className='load-generator'>
      <div className='load-generator__title'>Load Generator</div>
      <div className='load-generator__inner'>
        <div className='load-generator__load-info'>
          <Button
            className='button'
            text={buttonPending ? 'Generating load...' : 'Generate Load'}
            isPending={buttonPending}
            handleClick={handleGenerateLoad}
          />
          <div className='info'><span>Current Load:</span><span className='load'>{currentLoad}</span></div>
        </div>
        <Chart
          chartData={chartData}
          labels={chartTime}
        />
      </div>
    </div>
  )
}

export default LoadGenerator;