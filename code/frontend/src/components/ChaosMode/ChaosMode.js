import React, { useState, useEffect } from 'react';
import axios from 'axios';
import $ from "jquery";
import './chaos-mode.scss';
import Button from '../Button/Button';
import Skeleton from 'react-loading-skeleton';
import ProgressBar from '../ProgressBar/ProgressBar';
import 'react-loading-skeleton/dist/skeleton.css';

const ChaosMode = () => {
  const [servicesData, setServicesData] = useState([]);
  const [nodesData, setNodesData] = useState([]);

  //Comparer Function    
  const getSortOrder = prop => {    
    return function(a, b) {    
        if (a[prop] > b[prop]) {    
          return 1;    
        } else if (a[prop] < b[prop]) {    
          return -1;    
        }    
      return 0;    
    }    
  }

  // fetch services and nodes data at load
  useEffect(() => {
    getAllData();

    //  Update data every 3 seconds
    setInterval(() => {
      getAllData();
    }, 3000);
  }, [])

  // Get all services and nodes data
  const getAllData = () => {
    getPods();
    getInstances();
  }

  // Get Services
  const getPods = () => {
    axios.get('/list-pods')
    .then(function (response) {
      // handle success
      setServicesData(response.data.pods);
    })
  }

  // Get Instances
  const getInstances = () => {
    axios.get('/list-instances')
    .then(function (response) {
      // handle success
      const rawDataArr = response.data.instances
      // Convert zones to regions
      const sortedData = [...new Map(rawDataArr.map(item => [item.zone, item])).values()].sort(getSortOrder("zone"));
      setNodesData(sortedData);
    })
  }

  return (
    <div className='chaos-mode'>
      <div className='chaos-mode__title'>Chaos Mode</div>
      <div className='chaos-mode__inner'>
        {/* Service columns */}
        <div className='services'>
          <div className='services__title'>Services:<span>Active: ({servicesData.filter(x => x.status === ('ready')).length}/{servicesData.length})</span></div>
          <div className='services__content'>
            {/* Render all service rows here */}
            {
              servicesData.length ?
                servicesData.map(service => (
                  <ServiceRow service={service} />
              )) : <SkeletonPlaceHolder count={20} />
            }
          </div>
        </div>
        
        {/* Node columns */}
        <div className='nodes'>
          <div className='nodes__title'>Nodes:<span>Active: ({nodesData.filter(x => x.status === 'RUNNING').length}/{nodesData.length})</span></div>
          <div className='services__content'>
            {/* Render all Node rows here */}
            {
              nodesData.length ? nodesData.map(node => (
                <NodeRow node={node} />
              )) : <SkeletonPlaceHolder count={20} />
            }
          </div>
        </div>
      </div>
    </div>
  )
}

///////////////////////////////////////////////////////////
const ServiceRow = ({service}) => {
  const [isPending, setIsPending] = useState(false);

  // Kill Service life
  const handleServiceLife = serviceData => {
    setIsPending(true);

    const {name, zone, cluster} = serviceData;
    let fd = new FormData();
    fd.append('gke_pod', name);
    fd.append('gke_zone', zone);
    fd.append('gke_cluster', cluster)

    $.ajax({
      url: '/remove-pod',
      data: fd,
      type: 'POST',
      dataType: "json",
      processData: false,
      contentType: false,
      cache: false,
      enctype: 'multipart/form-data',
      success: function(data) {
        // console.log(data);
      }
    })
  }

  return (
    service ? (
      <div className={`service ${service.status === 'ready' ? 'service--running' : 'service--down'}`} key={service.name}>
        <div className='service__name'>{service.name.replace(/\-.*/,'').charAt(0).toUpperCase() + service.name.replace(/\-.*/,'').slice(1)}</div>
        <div className='service__status'>Status: <span className='dot'></span></div>
        <Button
          text='Terminate'
          short='true'
          type={service.status === 'ready' ? 'red' : 'green'}
          handleClick={() => handleServiceLife(service)}
          isPending={isPending}
        />
      </div>
    ) : <Skeleton count={3} />
  )
}

const NodeRow = ({node}) => {
  const [isPending, setIsPending] = useState(false);

  useEffect(() => {
    setIsPending(false);
  }, [])

  // Kill Node life
  const handleNodeLife = nodeData => {
    setIsPending(true);

    const {name, zone} = nodeData;
    let fd = new FormData();
    fd.append('instance_name', name);
    fd.append('instance_zone', zone);

    $.ajax({
      url: '/remove-instance',
      data: fd,
      type: 'POST',
      dataType: "json",
      processData: false,
      contentType: false,
      cache: false,
      enctype: 'multipart/form-data',
      success: function(data) {
        // console.log(data);
        setIsPending(false);
      }
    })
  }

  return (
    <div className={`node ${node.status === 'RUNNING' ? '' : 'node--disabled'}`} key={node.name}>
      <div className='node__name'>{node.zone}</div>
      <div className='node__status'>Status: <span className={`dot ${node.status === 'RUNNING' ? '' : 'dot--is-terminated'}`}></span></div>
      <Button
        text={node.status === 'RUNNING' ? 'Terminate' : 'Terminated'}
        short='true'
        type={node.status === 'RUNNING' ? 'red' : 'disabled'}
        handleClick={() => handleNodeLife(node)}
        isPending={isPending}
      />
    </div>
  )
}

const SkeletonPlaceHolder = ({count}) => <Skeleton className='skeleton' count={count} />

export default ChaosMode;