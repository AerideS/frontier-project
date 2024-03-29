<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Animate a point along a route</title>
<meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
<link href="https://api.mapbox.com/mapbox-gl-js/v3.2.0/mapbox-gl.css" rel="stylesheet">
<script src="https://api.mapbox.com/mapbox-gl-js/v3.2.0/mapbox-gl.js"></script>
<style>
body { margin: 0; padding: 0; }
#map { position: absolute; top: 0; bottom: 0; width: 100%; }
</style>
</head>
<body>
<style>
    .overlay {
        position: absolute;
        top: 10px;
        left: 10px;
    }
</style>
<script src="https://unpkg.com/@turf/turf@6/turf.min.js"></script>

<div id="map"></div>
<div class="overlay">
    <button id="replay">Replay</button>
</div>

<script>
	mapboxgl.accessToken = 'pk.eyJ1IjoibGdoNjk2MyIsImEiOiJjbHRwaWJ5NXAwNjNpMmpwZmo0dzg5MmcyIn0.WRICTXvdHP46wiy2GmLJDw';
    const map = new mapboxgl.Map({
        container: 'map',
        // Choose from Mapbox's core styles, or make your own style with Mapbox Studio,
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [128.0996, 35.1531],
        zoom: 14,
        pitch: 40
    });

    // San Francisco
    const origin = [128.0928, 35.1544];

    // Washington DC
    const destination = [128.1046, 35.1532];

    // A single point that animates along the route.
    // Coordinates are initially set to origin.
    const start = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'Point',
                    'coordinates': origin
                }
            }
        ]
    };

    const end = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'Point',
                    'coordinates': destination
                }
            }
        ]
    };

    map.on('load', () => {
        map.addSource('start', {
            'type': 'geojson',
            'data': start
        });

        map.addSource('end', {
            'type': 'geojson',
            'data': end
        })
    });

    function pointOnCircle(time) {
        return {
            'type': 'Point',
            'coordinates': [origin[0] + time/30*(destination[0]-origin[0]), origin[1] +  time/30*(destination[1]-origin[1])]
        };
    }

    map.on('load', () => {
        // Add a source and layer displaying a point which will be animated in a circle.
        map.addSource('point', {
            'type': 'geojson',
            'data': pointOnCircle(0)
        });

        map.addLayer({
            'id': 'point',
            'source': 'point',
            'type': 'symbol',
            'layout': {
                // This icon is a part of the Mapbox Streets style.
                // To view all images available in a Mapbox style, open
                // the style in Mapbox Studio and click the "Images" tab.
                // To add a new image to the style at runtime see
                // https://docs.mapbox.com/mapbox-gl-js/example/add-image/
                'icon-image': 'airport',
                'icon-size': 1.5,
                'icon-rotate': ['get', 'bearing'],
                'icon-rotation-alignment': 'map',
                'icon-allow-overlap': true,
                'icon-ignore-placement': true
            }
        });

        function animateMarker(timestamp) {
            // Update the data to a new position based on the animation timestamp. The
            // divisor in the expression `timestamp / 1000` controls the animation speed.
            // 시간(초) 단위로 움직임. 5초동안 움직이는 코드임.
            if(timestamp <= 5000) {
              map.getSource('point').setData(pointOnCircle(timestamp / 1000));

              // Request the next frame of the animation.
              requestAnimationFrame(animateMarker);
            }
        }

        // Start the animation.
        animateMarker(0);
      }
    )

</script>

</body>
</html>