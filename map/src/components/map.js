import React, { useRef, useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import mapboxgl from 'mapbox-gl';
import proj4 from 'proj4';
import 'mapbox-gl/dist/mapbox-gl.css';
import './map.css'

import markers from "./markers.json";
import MarkerList from "./MarkerList";
import Background from './Background';
import DotControl from './DotControl';
import Tooltip from './Tooltip';
import FgbDownload from './FgbDownload';

mapboxgl.accessToken = 'pk.eyJ1IjoiYWhnbm95IiwiYSI6ImZIcGRiZjgifQ.pL1SaB8gHyl-L2yolSl5Qw';

export default function Map() {

  const mapContainer = useRef(null);
  const map = useRef(null);
  const tooltipRef = useRef(new mapboxgl.Popup({ offset: 15 }));
  const x0 = 24.8600;
  const y0 = 0.2006;
  const [lng, setLng] = useState(x0);
  const [lat, setLat] = useState(y0);
  const xy0 = proj4("EPSG:4326", "EPSG:3857").forward({
    x: x0,
    y: y0
  });

  const [x, setX] = useState(xy0.x.toFixed(1));
  const [y, setY] = useState(xy0.y.toFixed(1));
  const [zoom, setZoom] = useState(12.00);
  const [markerList, setMarkerList] = useState(markers);
  const [bgOpacity, setBgOpacity] = useState(0.5);
  const [circleSize, setCircleSize] = useState(150);
  const [deepFeatures, setDeepFeatures] = useState([]);
  const deepFeaturesRef = useRef(deepFeatures);

  useEffect(() => {
    // initial load
    if (map.current) return;
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: { version: 8, sources: {}, layers: [] },
      center: [lng, lat],
      zoom: zoom
    });

    // add sources and layers
    map.current.on('load', () => {
      // add base map
      map.current.addSource('basemap', {
        type: 'raster',
        tiles: [
          'https://seqscope-web-test.s3.amazonaws.com/basetiles/{z}/{x}/{y}.png'
        ],
        tileSize: 256,
        scheme: 'tms'
      });
      map.current.addLayer({
        'id': 'basetiles',
        'type': 'raster',
        'source': 'basemap',
        'minzoom': 6,
        'maxzoom': 15,
        'paint': {
          'raster-opacity': bgOpacity
        }
      });
      //add marker sources and layers
      markers.map(x => addSource(map.current, x.id));
      markers.map(x => addLayer(map.current, x.id, x.color));

    });

    // coordinate display
    map.current.on('move', () => {
      setLng(map.current.getCenter().lng.toFixed(6));
      setLat(map.current.getCenter().lat.toFixed(6));
      setZoom(map.current.getZoom().toFixed(2));
      const xy = proj4("EPSG:4326", "EPSG:3857").forward({
        x: map.current.getCenter().lng,
        y: map.current.getCenter().lat
      });
      setX(xy.x.toFixed(1));
      setY(xy.y.toFixed(1));
    });

    // tooltip
    map.current.on('click', e => {
      const features = map.current.queryRenderedFeatures(e.point);
      if (features.length) {
        const feature = features[0];
        // Create tooltip node
        const tooltipNode = document.createElement('div');
        ReactDOM.render(<Tooltip feature={feature} />, tooltipNode);
        // Set tooltip on map
        tooltipRef.current
          .setLngLat(e.lngLat)
          .setDOMContent(tooltipNode)
          .addTo(map.current);
      }
    });
  });

  useEffect(() => {
    markerList.map(mk => {
      try {
        map.current.setLayoutProperty(
          `l-mark-${mk.id}`,
          'visibility',
          mk.display ? 'visible' : 'none'
        );
      } catch (err) { }
    });
  });


  const handleMarkerToggle = (id) => {
    let mapped = markerList.map(loc => {
      return loc.id === id ? { ...loc, display: !loc.display } : { ...loc };
    });
    setMarkerList(mapped);
  }
  const handleBgChange = (value) => {
    map.current.setPaintProperty('basetiles', 'raster-opacity', value);
    setBgOpacity(value);
  }
  const handleCircleSize = (value) => {
    markers.map(x => {
      // addLayer(map.current, x.id, x.color);
      map.current.setPaintProperty(
        `l-mark-${x.id}`,
        'circle-radius',
        { stops: [[0, 0], [17, value]], base: 2 }
      );
    });
    setCircleSize(value);
  }
  const addSource = (m, gene) => {
    m.addSource('mark-' + gene, {
      'type': 'vector',
      'tiles': [
        'https://seqscope-web-test.s3.amazonaws.com/tile/' + gene + '/{z}/{x}/{y}.pbf'
      ],
      'minzoom': 4,
      'maxzoom': 15
    });
  };
  const addLayer = (m, gene, color) => {
    m.addLayer({
      'id': 'l-mark-' + gene,
      'type': 'circle',
      'source': 'mark-' + gene,
      'source-layer': gene,
      'paint': {
        'circle-radius': {
          stops: [
            [0, 0],
            [17, circleSize]
          ],
          base: 2
        },
        'circle-color': color,
        'circle-opacity': 0.6
      }
    });
  };

  const handleFgbClick = () => {
    return { x: x, y: y, map: map.current }
  }
  // const fgbCallback = (features) => {
  //   deepFeaturesRef.current = features;
  //   console.log("parent", features);
  // }

  return (
    <div className="map-wrap">
      <div className="sidebar">
        <h1 className="heading">SeqScope</h1>
        {/* <div>X:{lng}|Y:{lat}|Zoom:{zoom}</div> */}
        <div>X:{x}|Y:{y}|Zoom:{zoom}</div>
        <hr />
        <MarkerList markerList={markerList} handleToggle={handleMarkerToggle} />
        <hr />
        <Background value={bgOpacity} handleChange={handleBgChange} />
        <hr />
        <DotControl value={circleSize} handleChange={handleCircleSize} />
        <hr />
        <FgbDownload
          handleClick={handleFgbClick}
        // callback={fgbCallback}
        />
      </div>
      <div ref={mapContainer} className="map" />
    </div>
  );
}

