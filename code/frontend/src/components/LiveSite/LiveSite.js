import React, { useState, useEffect } from 'react';
import './live-site.scss';
import { _VARIABLES } from '../../config.js';
import loadingGif from '../../assets/loading.gif';

const LiveSite = () => {
  const [isIframeLoaded, setIsIframeLoaded] = useState(false);
  const [iframeURL, setIframeURL] = useState('');
  let i = 0;

  useEffect(() => {
    setInterval(() => {
      rotateIframeURL();
    }, 2000);
  }, []);

  useEffect(() => {
    // console.log(iframeURL)
  }, [iframeURL]);

  const rotateIframeURL = () => {
    setIframeURL(_VARIABLES.site_urls[i]);
    i = i > _VARIABLES.site_urls.length - 2 ? 0 : i + 1;
  }

  const handleIframeOnLoad = () => {
    setIsIframeLoaded(true);
  }

  return (
    <div className='live-site'>
      <div className='title'>Live Site:</div>
      <div className='live-site__inner'>
        <div className={`loading ${isIframeLoaded ? 'loading--hidden' : null}`}>
          <img src={loadingGif} />
          <div className='text'>Loading Boutique Site...</div>
        </div>

        <iframe className={`iframe ${isIframeLoaded ? 'iframe--visible' : null}`} src={iframeURL} title="Site Preview" id="preview_iframe" onLoad={handleIframeOnLoad}></iframe>
      </div>
    </div>
  )
}

export default LiveSite;