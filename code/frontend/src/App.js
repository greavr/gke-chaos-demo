import Header from './components/Header/Header';
import Monitoring from './components/Monitoring/Monitoring';
import LoadGenerator from './components/LoadGenerator/LoadGenerator';
import ChaosMode from './components/ChaosMode/ChaosMode';
import LiveSite from './components/LiveSite/LiveSite';

import './App.scss';

function App() {
  return (
    <div className="App">
      <Header />
      <div className='main'>
        <div className='main-left'>
          <Monitoring />
          <LoadGenerator />
          <ChaosMode />
        </div>
        <div className='main-right'>
          <LiveSite />
        </div>
      </div>
    </div>
  );
}

export default App;
