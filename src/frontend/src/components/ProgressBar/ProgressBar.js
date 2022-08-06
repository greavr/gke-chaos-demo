import React, {useState} from 'react';
import './progress-bar.scss';

const ProgressBar = props => {
  return (
    <div className='progress-bar' style={{width: `${props.progress}%`}}>

    </div>
  )
}

export default ProgressBar;