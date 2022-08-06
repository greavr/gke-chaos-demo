import React from 'react';
import './monitoring.scss';
import Button from '../Button/Button';

const Monitoring = () => {
  return (
    <div className='monitoring'>
      <div className='title'>GCP Monitoring Dashboard:</div>
      <div className='monitoring__inner'>
        <div className='text'>
          <div className='text__text'>Click the button on the right to</div>
          <div className='text__text'>open GCP Monitoring Dashboard</div>
        </div>
        <Button
          text='Open GCP Monitoring Dashboard'
          externalLink='https://console.cloud.google.com/monitoring/dashboards/builder/fede45bd-5d75-43ac-994c-dcefa25396ad?dashboardBuilderState=%257B%2522editModeEnabled%2522:false%257D&organizationId=599669849801&project=rgreaves-gke-chaos&timeDomain=1h'
        />
      </div>
    </div>
  )
}

export default Monitoring;