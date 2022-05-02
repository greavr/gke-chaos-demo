import React from 'react';
import './header.scss';
import gcp_logo from '../../assets/gcp-logo.png';

const Header = () => {
  return (
    <div className='header'>
      <div className='title'>
        <div className='title_logo'>
          <img src={gcp_logo} />
        </div>
        <div className='title_title'>
          Online Boutique Black Friday Demo
        </div>
      </div>
      <div className='info'>
        <div className='info-detail'>Google Cloud Solutions Studio</div>
        <div className='info-detail'>contact : rgreaves@google.com</div>
      </div>
    </div>
  )
}

export default Header;