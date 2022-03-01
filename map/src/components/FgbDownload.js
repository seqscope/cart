import React, { useEffect, useState } from 'react';
import { geojson } from "flatgeobuf";

const FgbDownload = ({ handleClick, callback }) => {
  const [features, setFeatures] = useState({});

  const onClick = (e) => {
    const fgb_src = "https://seqscope-web-test.s3.amazonaws.com/flatgeobuf/merged.fgb";
    const xy = handleClick();
    const xc = xy.x;
    const yc = xy.y;
    const range = 1500;
    const bounds = {
      maxX: xc + range,
      maxY: yc + range,
      minX: xc - range,
      minY: yc - range
    };
    let features = loadFGB(fgb_src, bounds);
    setFeatures(features);
    console.log(features);
    callback(features);
  };

  const loadFGB = async (fgb_src, bounds) => {
    console.log("loadFGB");
    const iter = geojson.deserialize(
      fgb_src,
      bounds,
      (meta) => { console.log(meta); });
    let features = [];
    for await (let feature of iter) {
      features.push(feature);
    }
    return features;
  };

  // const handleHeaderMeta = (headerMeta) => {
  //   console.log(headerMeta)
  // }

  return (
    <div>
      <label>Full Genes (count {features.length})</label>
      <input
        onClick={onClick}
        type="button"
        value="FGB"
      ></input>
    </div>
  )
}

export default FgbDownload;
