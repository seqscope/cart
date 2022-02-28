import React, { useRef, useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './map.css'

import markers from "./markers.json";
import MarkerList from "./MarkerList";
import Background from './Background';
import DotControl from './DotControl';
import Tooltip from './Tooltip';

mapboxgl.accessToken = 'pk.eyJ1IjoiYWhnbm95IiwiYSI6ImZIcGRiZjgifQ.pL1SaB8gHyl-L2yolSl5Qw';

export default function Map() {

  const mapContainer = useRef(null);
  const map = useRef(null);
  const tooltipRef = useRef(new mapboxgl.Popup({ offset: 15 }));

  const [lng, setLng] = useState(24.8600);
  const [lat, setLat] = useState(0.2006);
  const [zoom, setZoom] = useState(12.00);
  const [markerList, setMarkerList] = useState(markers);
  const [bgOpacity, setBgOpacity] = useState(0.5);
  const [circleSize, setCircleSize] = useState(150);

  useEffect(() => {
    if (map.current) return;
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: { version: 8, sources: {}, layers: [] },
      center: [lng, lat],
      zoom: zoom
    });
  });

  useEffect(() => {
    if (!map.current) return;
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

  useEffect(() => {
    if (!map.current) return;
    map.current.on('move', () => {
      setLng(map.current.getCenter().lng.toFixed(4));
      setLat(map.current.getCenter().lat.toFixed(4));
      setZoom(map.current.getZoom().toFixed(2));
    });
  });

  //tooltip
  useEffect(() => {
    if (!map.current) return;
    // map.current.on('mouseenter', e => {
    //   if (e.features.length) {
    //     console.log(e);
    //     map.current.getCanvas().style.cursor = 'pointer';
    //   }
    // });
    // // reset cursor to default when user is no longer hovering over a clickable feature
    // map.current.on('mouseleave', () => {
    //   map.current.getCanvas().style.cursor = '';
    // });

    // add tooltip when users mouse move over a point
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
      addLayer(map.current, x.id, x.color);
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


  return (
    <div className="map-wrap">
      <div className="sidebar">
        <h1 className="heading">SeqScope</h1>
        <div>X:{lng}|Y:{lat}|Zoom:{zoom}</div>
        <hr />
        <MarkerList markerList={markerList} handleToggle={handleMarkerToggle} />
        <hr />
        <Background value={bgOpacity} handleChange={handleBgChange} />
        <hr />
        <DotControl value={circleSize} handleChange={handleCircleSize} />

      </div>
      <div ref={mapContainer} className="map" />
    </div>
  );
}

