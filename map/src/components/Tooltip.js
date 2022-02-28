import React from "react";

const Tooltip = ({ feature }) => {
  const { id } = feature.properties;

  return (
    <div id={`tooltip-${id}`} className='tooltip'>
      <strong>{feature.properties.gene_name} </strong> @ {feature.layer["source-layer"]}
      <li> cnt_spliced:{feature.properties.cnt_spliced} </li>
      <li> cnt_unspliced:{feature.properties.cnt_unspliced} </li>
      <li> cnt_ambiguous:{feature.properties.cnt_ambiguous} </li>
    </div>
  );
};

export default Tooltip;
