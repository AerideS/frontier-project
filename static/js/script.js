// The value for 'accessToken' begins with 'pk...'
mapboxgl.accessToken = 'pk.eyJ1IjoibGdoNjk2MyIsImEiOiJjbHRwaWJ5NXAwNjNpMmpwZmo0dzg5MmcyIn0.WRICTXvdHP46wiy2GmLJDw'; 
const map = new mapboxgl.Map({
  container: 'map', // container id
  style: 'mapbox://styles/lgh6963/clu8bnid5006m01r67dxy19gh', // stylesheet location
  center: [128.09902549138565,35.15402490372111], // starting position
  zoom: 15 // starting zoom
});

// Code from the next step will go here.

// 점 추가 함수
function addPointLayer(coordinate) {
  map.addLayer({
    id: 'points',
    type: 'circle',
    source: {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: [{
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: coordinate
          },
          properties: {
            title: 'Point',
            description: 'This is a point.'
          }
        }]
      }
    },
    paint: {
      'circle-radius': 20,
      'circle-color': '#007cbf'
    }
  });
}

// 맵 로드 시 호출
map.on('load', function () {
  var coordinate = [128.0997, 35.1532]; // 좌표 설정
  addPointLayer(coordinate); // 점 추가 함수 호출
});

map.on('load', function () {
  var coordinate = [128.0997, 35.1532]; // 텍스트를 표시할 좌표

// 텍스트 레이어 추가
map.addLayer({
  id: 'text-layer',
  type: 'symbol',
  source: {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: coordinate // 좌표 설정
        },
        properties: {
          text: '텍스트 예제', // 표시할 텍스트
          iconSize: 10
        }
      }]
    }
  },
  layout: {
    'text-field': ['get', 'text'], // 텍스트 필드 설정
    'text-font': ['Open Sans Regular'],
    'text-size': 12
  },
  paint: {
    'text-color': '#000000' // 텍스트 색상 설정
  }
});
});
