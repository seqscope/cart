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
      <li> {marker.id} </li>
      <div>
        {marker.genes.map((gene) => {
          return <button key={gene}>{gene}</button>
        })}
      </div>
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
