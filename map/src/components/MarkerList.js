import React from 'react';

const Marker = ({ marker, handleToggle }) => {
  const handleClick = (e) => {
    e.preventDefault();
    handleToggle(e.currentTarget.id);
  }
  return (
    <div
      id={marker.id}
      name="marker"
      value={marker.id}
      onClick={handleClick}
      className={marker.display ? "marker" : "strike marker"}
    >
      {marker.id}
    </div>
  )
}

const MarkerList = ({ markerList, handleToggle }) => {
  return (
    <div>
      {markerList.map((marker, idx) => {
        return (
          <Marker key={idx} marker={marker} handleToggle={handleToggle} />
        )
      })}
    </div>
  )
}

export default MarkerList;
