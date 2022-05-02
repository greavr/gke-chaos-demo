import React, {useState} from 'react';
import './button.scss';

const Button = props => {
  return (
    props.externalLink ?
    <a className='button' href={props.externalLink} target='_blank'>
      <div>
        {props.text}
      </div>
    </a>
    :
    <button
      className={`button ${props.short ? 'button--short' : null} ${props.isPending ? 'button--pending' : null} ${props.type === 'red' ? 'button--red' : null} ${props.type === 'green' ? 'button--green' : null} ${props.type === 'disabled' ? 'button--disabled' : null}`}
      onClick={props.handleClick}
    >
      {props.text}  
    </button>
  )
}

export default Button;