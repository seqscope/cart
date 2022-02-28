import React from 'react';

const DotControl = ({ value, handleChange }) => {
  const onChange = (e) => {
    handleChange(Number(e.target.value));
  }
  return (
    <div>
      <label>
        <div>Dot Size:{value}</div>
        <input
          onChange={onChange}
          min="0"
          max="300"
          value={value}
          step="20"
          type="range"
        />
      </label>
    </div>
  )
};

export default DotControl;
