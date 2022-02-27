mapboxgl.accessToken = 'pk.eyJ1IjoiYWhnbm95IiwiYSI6ImZIcGRiZjgifQ.pL1SaB8gHyl-L2yolSl5Qw';
const map = new mapboxgl.Map({
  container: 'map',
  // style: 'mapbox://styles/mapbox/dark-v10',
  style: {version: 8,sources: {},layers: []},
  zoom: 12,
  center: [18.3, 0.12]
});
const markers = ['B_cell', 'Colonocyte', 'EEC', 'Fibro', 'Goblet', 'Injury', 'Macro', 'Neuronal', 'SM'];
map.on('load', () => {
	markers.map(x => addSource(map, x));
  // addSource(map, "Colonocyte");
	// addSource(map, "Goblet");
	addLayer(map, "Colonocyte", '#A2F');
});

function addSource(m, gene){
	m.addSource('mark-'+ gene, {
    'type': 'vector',
    'tiles': [
    	'https://seqscope-web-test.s3.amazonaws.com/tile/' + gene + '/{z}/{x}/{y}.pbf'
    ],
    'minzoom': 4,
    'maxzoom': 15
  });
}

function addLayer(m, gene, color) {
	m.addLayer({
		'id': 'l-mark-' + gene,
		'type': 'circle',
		'source': 'mark-' + gene,
		'source-layer': gene,
		'paint': {
			'circle-radius': 2,
			'circle-color': color,
			'circle-opacity': 0.3
		}
	});
}

map.on('click', 'l-mark-Colonocyte', function (e) {
	var feature = e.features[0];
	var coordinates = feature.geometry.coordinates.slice();
	var properties = Object.keys(feature.properties).map(function (propertyName) {
		return renderProperty(propertyName, feature.properties[propertyName]);
	});
	console.log(coordinates);
	new mapboxgl.Popup()
		.setLngLat(coordinates)
		.setHTML(properties.join(' '))
		.addTo(map);
});
   
function renderProperty(propertyName, property) {
  return '<div class="mbview_property">' +
    '<div class="mbview_property-name">' + propertyName + '</div>' +
    '<div class="mbview_property-value">' + displayValue(property) + '</div>' +
    '</div>';
}
function displayValue(value) {
  if (typeof value === 'undefined' || value === null) return value;
  if (typeof value === 'number') return Math.round(value).toString();
  if (typeof value === 'object' ||
    typeof value === 'string') return value.toString();
  return value;
}

