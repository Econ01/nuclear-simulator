// Initialize the map
const map = new ol.Map({
    target: 'map',
    layers: [
        new ol.layer.Tile({
            source: new ol.source.OSM()
        })
    ],
    view: new ol.View({
        center: ol.proj.fromLonLat([0, 0]),
        zoom: 2
    })
});

// Create a vector layer for visualization
const vectorSource = new ol.source.Vector();
const vectorLayer = new ol.layer.Vector({
    source: vectorSource,
    style: new ol.style.Style({
        image: new ol.style.Circle({
            radius: 5,
            fill: new ol.style.Fill({ color: 'rgba(255, 0, 0, 0.8)' }),
            stroke: new ol.style.Stroke({
                color: 'rgba(255, 255, 255, 0.8)', width: 1
            })
        })
    })
});
map.addLayer(vectorLayer);

// Ground zero marker
const groundZero = new ol.Feature();
groundZero.setStyle(new ol.style.Style({
    image: new ol.style.Circle({
        radius: 8,
        fill: new ol.style.Fill({ color: 'rgba(255, 0, 0, 0.8)' }),
        stroke: new ol.style.Stroke({
            color: 'rgba(255, 255, 255, 0.8)', width: 2
        })
    })
}));
vectorSource.addFeature(groundZero);

// Set initial location to browser location
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(position => {
        const coords = ol.proj.fromLonLat([
            position.coords.longitude, 
            position.coords.latitude
        ]);
        map.getView().setCenter(coords);
        map.getView().setZoom(10);
        groundZero.setGeometry(new ol.geom.Point(coords));
        updateLocationInfo(position.coords.longitude, position.coords.latitude);
    });
}

// Update location on map click
map.on('click', event => {
    const coords = ol.proj.toLonLat(event.coordinate);
    groundZero.setGeometry(new ol.geom.Point(event.coordinate));
    updateLocationInfo(coords[0], coords[1]);
});

function updateLocationInfo(lon, lat) {
    const latStr = lat >= 0 ? `${lat.toFixed(4)}°N` : `${Math.abs(lat).toFixed(4)}°S`;
    const lonStr = lon >= 0 ? `${lon.toFixed(4)}°E` : `${Math.abs(lon).toFixed(4)}°W`;
    document.getElementById('location-coords').textContent = `${latStr}, ${lonStr}`;
}

// Get DOM elements
const yieldSlider = document.getElementById('yield');
const yieldValue = document.getElementById('yield-value');
const burstHeightSlider = document.getElementById('burst-height');
const burstHeightValue = document.getElementById('burst-height-value');
const windSpeedSlider = document.getElementById('wind-speed');
const windSpeedValue = document.getElementById('wind-speed-value');
const windDirectionSlider = document.getElementById('wind-direction');
const windDirectionValue = document.getElementById('wind-direction-value');
const atmosphereSlider = document.getElementById('atmosphere');
const atmosphereValue = document.getElementById('atmosphere-value');
const distanceInput = document.getElementById('distance');
const calculateBtn = document.getElementById('calculate-btn');
const resultsContainer = document.getElementById('results-container');

// Event listeners
yieldSlider.addEventListener('input', () => {
    yieldValue.textContent = `${parseFloat(yieldSlider.value).toLocaleString()} kt`;
});

burstHeightSlider.addEventListener('input', () => {
    burstHeightValue.textContent = `${burstHeightSlider.value} m`;
});

windSpeedSlider.addEventListener('input', () => {
    windSpeedValue.textContent = `${windSpeedSlider.value} m/s`;
});

windDirectionSlider.addEventListener('input', () => {
    const dir = parseInt(windDirectionSlider.value);
    windDirectionValue.textContent = `${dir}°`;
    
    // Update wind arrow
    const arrow = document.querySelector('.wind-arrow');
    arrow.style.transform = `rotate(${dir}deg)`;
    
    // Update wind info
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(dir / 45) % 8;
    document.getElementById('wind-info').textContent = 
        `${windSpeedSlider.value} m/s ${directions[index]}`;
});

atmosphereSlider.addEventListener('input', () => {
    const value = parseFloat(atmosphereSlider.value);
    atmosphereValue.textContent = `${Math.round(value * 100)}%`;
});

calculateBtn.addEventListener('click', async () => {
    // Get ground zero coordinates
    const coords = ol.proj.toLonLat(groundZero.getGeometry().getCoordinates());
    
    // Prepare payload
    const payload = {
        yield: yieldSlider.value,
        distance: distanceInput.value,
        burst_height: burstHeightSlider.value,
        wind_speed: windSpeedSlider.value,
        wind_direction: windDirectionSlider.value,
        atmosphere: atmosphereSlider.value,
        latitude: coords[1],
        longitude: coords[0]
    };
    
    try {
        // Update button state
        calculateBtn.disabled = true;
        calculateBtn.innerHTML = '<span class="icon">⏳</span> Calculating...';
        
        // Calculate blast effects
        const blastResponse = await fetch('/calculate-blast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const blastData = await blastResponse.json();
        
        // Calculate fallout
        const falloutResponse = await fetch('/calculate-fallout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const falloutData = await falloutResponse.json();
        
        // Update UI with results
        displayResults(blastData);
        visualizeFallout(falloutData);
        
        // Show results container
        resultsContainer.style.display = 'block';
        
    } catch (error) {
        console.error('Calculation error:', error);
        alert('Simulation failed. See console for details.');
    } finally {
        // Reset button state
        calculateBtn.disabled = false;
        calculateBtn.innerHTML = '<span class="icon">☢️</span> Simulate Detonation';
    }
});

function displayResults(data) {
    // Update blast effects
    document.getElementById('overpressure').textContent = `${data.overpressure_kpa.toFixed(1)} kPa`;
    document.getElementById('dynamic-pressure').textContent = `${data.dynamic_pressure_kpa.toFixed(1)} kPa`;
    document.getElementById('arrival-time').textContent = `${data.arrival_time_sec.toFixed(2)} s`;
    document.getElementById('duration').textContent = `${data.positive_phase_duration_sec.toFixed(2)} s`;
    
    // Update thermal effects
    document.getElementById('thermal').textContent = `${data.thermal_cal_per_cm2.toFixed(1)} cal/cm²`;
    document.getElementById('ignition-prob').textContent = `${(data.ignition_probability * 100).toFixed(1)}%`;
    
    // Update radiation effects
    document.getElementById('prompt-rad').textContent = `${data.prompt_radiation_sv.toFixed(2)} Sv`;
    document.getElementById('fallout-dose').textContent = `${data.residual_radiation_sv_per_h.toFixed(4)} Sv/h`;
    
    // Update effect descriptions
    document.getElementById('blast-effect-desc').textContent = getBlastEffectDesc(data.overpressure_kpa);
    document.getElementById('thermal-effect-desc').textContent = getThermalEffectDesc(data.thermal_cal_per_cm2);
    document.getElementById('radiation-effect-desc').textContent = getRadiationEffectDesc(data.prompt_radiation_sv);
    
    // Estimate casualties
    estimateCasualties(data);
}

function getBlastEffectDesc(pressure) {
    if (pressure > 500) return "Total destruction of all structures";
    if (pressure > 200) return "Reinforced concrete buildings destroyed";
    if (pressure > 50) return "Residential buildings collapse";
    if (pressure > 20) return "Glass windows shatter, moderate structural damage";
    if (pressure > 5) return "Minor structural damage, broken windows";
    return "Minimal structural damage";
}

function getThermalEffectDesc(energy) {
    if (energy > 100) return "Third-degree burns, spontaneous ignition of materials";
    if (energy > 25) return "Second-degree burns, clothing ignites";
    if (energy > 10) return "First-degree burns, flammable materials ignite";
    if (energy > 5) return "Painful burns, possible ignition of thin materials";
    return "Sunburn-like effects";
}

function getRadiationEffectDesc(dose) {
    if (dose > 10) return "100% fatal within 48 hours";
    if (dose > 5) return "50% fatal within 30 days (LD50)";
    if (dose > 1) return "Radiation sickness, increased cancer risk";
    if (dose > 0.5) return "Temporary radiation sickness";
    return "Minimal acute effects";
}

function estimateCasualties(data) {
    const distance = parseFloat(distanceInput.value);
    const populationDensity = {
        'rural': 10,
        'suburban': 1000,
        'urban': 10000,
        'dense': 50000
    };
    
    const density = populationDensity[document.getElementById('population').value];
    const area = Math.PI * distance * distance;
    const population = Math.floor(area * density / 1e6); // per km²
    
    // Estimate based on effects
    const fatalities = Math.floor(population * (0.7 * (1 - Math.exp(-data.overpressure_kpa/50))));
    const injuries = Math.floor(population * 0.6 * (1 - Math.exp(-data.thermal_cal_per_cm2/15)));
    const affected = Math.min(population, fatalities + injuries);
    
    // Update UI
    document.getElementById('fatalities').textContent = fatalities.toLocaleString();
    document.getElementById('injuries').textContent = injuries.toLocaleString();
    document.getElementById('affected').textContent = affected.toLocaleString();
    
    // Update chart
    const fatalitiesPct = Math.min(100, (fatalities / population) * 100);
    const injuriesPct = Math.min(100, (injuries / population) * 100);
    const affectedPct = Math.min(100, (affected / population) * 100);
    
    document.querySelector('.fatalities-bar').style.width = `${fatalitiesPct}%`;
    document.querySelector('.injuries-bar').style.width = `${injuriesPct}%`;
    document.querySelector('.affected-bar').style.width = `${affectedPct}%`;
}

function visualizeFallout(falloutData) {
    // Clear previous fallout
    vectorSource.clear();
    vectorSource.addFeature(groundZero);
    
    // Add fallout data
    const lonGrid = falloutData.longitude;
    const latGrid = falloutData.latitude;
    const contamination = falloutData.contamination;
    
    const gridSize = lonGrid.length;
    const step = Math.floor(gridSize / 50); // Sample every 5th point for performance
    
    for (let i = 0; i < gridSize; i += step) {
        for (let j = 0; j < gridSize; j += step) {
            const value = contamination[i][j];
            if (value > 0.1) { // Only show significant contamination
                const lon = lonGrid[i][j];
                const lat = latGrid[i][j];
                
                const point = new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.fromLonLat([lon, lat]))
                });
                
                // Style based on contamination level
                const size = Math.min(10, Math.max(2, Math.log10(value + 1)));
                const opacity = Math.min(0.7, value / 100);
                
                point.setStyle(new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: size,
                        fill: new ol.style.Fill({
                            color: `rgba(255, 100, 0, ${opacity})`
                        })
                    })
                }));
                
                vectorSource.addFeature(point);
            }
        }
    }
}

// Initialize UI
yieldSlider.dispatchEvent(new Event('input'));
burstHeightSlider.dispatchEvent(new Event('input'));
windSpeedSlider.dispatchEvent(new Event('input'));
windDirectionSlider.dispatchEvent(new Event('input'));
atmosphereSlider.dispatchEvent(new Event('input'));