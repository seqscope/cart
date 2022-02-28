import React from 'react';

const Background = ({ value, handleChange }) => {
  const onChange = (e) => {
    handleChange(Number(e.target.value));
  }
  return (
    <div>
      <label>
        <div>background opacity:{value}</div>
        <input
          onChange={onChange}
          name="bgOpacity"
          min="0"
          max="1"
          value={value}
          step=".1"
          type="range"
        />
      </label>
    </div>
  )
};

export default Background;
