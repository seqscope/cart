import React, { useEffect, useState } from 'react';
import { geojson } from "flatgeobuf";
import proj4 from 'proj4';

const FgbDownload = ({ x: x_parent, y: y_parent, map: map_parent }) => {
  const [features, setFeatures] = useState([]);
  const [map, setMap] = useState(map_parent);
  const [xc, setXc] = useState(x_parent);
  const [yc, setYc] = useState(y_parent);
  const [range, setRange] = useState(2500);

  const fgb_src = "https://seqscope-web-test.s3.amazonaws.com/flatgeobuf/merged.fgb";

  useEffect(() => {
    setXc(x_parent);
    setYc(y_parent);
    setMap(map_parent);
  }, [x_parent, y_parent, map_parent]);

  const onClick = () => {
    const bounds = {
      maxX: xc + range,
      maxY: yc + range,
      minX: xc - range,
      minY: yc - range
    };
    console.log("click!!!");
    loadFGB(fgb_src, bounds).then((res) => {
      console.log("res!!", res);
      setFeatures(res);
    }).catch(e => console.log("error!", e));
  };

  const createLayer = (map, geojson) => {
    const source = {
      'type': 'geojson',
      'data': {
        'type': 'FeatureCollection',
        'features': geojson
      }
    };
    const lname = 'deep-genes'

    map.addSource(lname, source);
    map.addLayer({
      'id': 'l-' + lname,
      'type': 'circle',
      'source': 'deep-genes',
      'paint': {
        'circle-radius': {
          stops: [
            [0, 0],
            [17, 150]
          ],
          base: 2
        },
        'circle-color': "#F33",
        'circle-opacity': 0.4
      }
    });
  };

  const loadFGB = async (fgb_src, bounds) => {
    const iter = geojson.deserialize(
      fgb_src,
      bounds,
      (meta) => { console.log(meta); });
    const results = [];
    for await (let f of iter) {
      const xy = proj4("EPSG:3857", "EPSG:4326").forward({
        x: f['geometry']['coordinates'][0],
        y: f['geometry']['coordinates'][1]
      });
      f['geometry']['coordinates'] = [xy.x, xy.y];
      results.push(f);
    }
    return results;
  };

  const draw = () => {
    createLayer(map, features);
  };

  const remove = () => {
    const lname = 'deep-genes'
    map.removeLayer('l-' + lname);
    map.removeSource(lname);
    setFeatures([]);
  };

  return (
    <div>
      <p>Full data download (at the center of the screen)</p>
      <input
        onClick={onClick}
        type="button"
        value="Donwload Dataset"
      ></input>
      <p>identified data points: {features.length}</p>
      <input
        onClick={draw}
        type="button"
        value="Draw"
      ></input>
      <input
        onClick={remove}
        type="button"
        value="Remove"
      ></input>

    </div>
  )
}

export default FgbDownload;
