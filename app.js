const response = await fetch('./countries.json');
if (!response.ok) throw new Error(`Could not load countries.json (${response.status})`);
const countries = await response.json();

if (!Array.isArray(countries) || countries.length === 0) {
  throw new Error('countries.json needs at least one country entry.');
}

// Temporary rotation: each country's fact returns after 195 calendar days.
const COUNTRY_CYCLE_DAYS = 195;
if (countries.length !== COUNTRY_CYCLE_DAYS) {
  throw new Error(`The temporary daily cycle expects ${COUNTRY_CYCLE_DAYS} countries.`);
}
const now = new Date();
const dayNumber = Math.floor(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()) / 86_400_000);
const index = ((dayNumber % COUNTRY_CYCLE_DAYS) + COUNTRY_CYCLE_DAYS) % COUNTRY_CYCLE_DAYS;
const country = countries[index];
const countryDate = document.querySelector('#country-date');
countryDate.dateTime = now.toISOString().slice(0, 10);
countryDate.textContent = new Intl.DateTimeFormat(undefined, {
  day: 'numeric', month: 'long', year: 'numeric',
}).format(now);

document.querySelector('#country-name').textContent = country.country;
const flag = document.querySelector('#country-flag');
const flagEmoji = document.querySelector('#country-flag-emoji');
flag.onerror = () => {
  if (!flag.dataset.triedAlternate) {
    flag.dataset.triedAlternate = 'true';
    flag.src = `https://flagsapi.com/${country.flagCode.toUpperCase()}/flat/64.png`;
    return;
  }
  flag.hidden = true;
  flagEmoji.textContent = [...country.flagCode.toUpperCase()]
    .map((letter) => String.fromCodePoint(127397 + letter.charCodeAt(0)))
    .join('');
  flagEmoji.hidden = false;
};
flag.src = `https://flagcdn.com/w160/${country.flagCode}.png`;
document.querySelector('#location-summary').textContent = country.location.summary;
document.querySelector('#fact-text').textContent = country.fact.text;
document.querySelector('#key-cities').textContent = (country.keyCities ?? [country.capital]).join(' · ');
document.querySelector('#memberships').textContent = (country.memberships ?? []).join(' · ');
document.querySelector('#globe').setAttribute('aria-label', `Interactive globe centered near ${country.capital}, ${country.country}`);
const sources = country.sources ?? [];
const membershipSource = country.membershipSources?.[1] ?? country.membershipSources?.[0];
for (const item of [
  sources[0] && { ...sources[0], title: 'Country overview' },
  membershipSource && { ...membershipSource, title: 'Membership source' },
].filter(Boolean)) {
  const link = document.createElement('a');
  link.href = item.url;
  link.target = '_blank';
  link.rel = 'noreferrer';
  link.textContent = item.title;
  document.querySelector('#sources').append(link, document.createTextNode(' · '));
}
document.querySelector('#sources').lastChild?.remove();

const mapError = document.querySelector('#map-error');
function showMapError(message) {
  mapError.textContent = message;
  mapError.hidden = false;
}

try {
  // MapLibre GL JS v6 is served as an ES module.
  const maplibregl = await import('https://unpkg.com/maplibre-gl@6.15.0/dist/maplibre-gl.mjs');
  const map = new maplibregl.Map({
    container: 'globe',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [country.location.longitude, country.location.latitude],
    zoom: 1.6,
    attributionControl: true,
  });

  map.on('style.load', () => {
    map.setProjection({ type: 'globe' });
    const colors = [
      ['background', 'background-color', '#E7EFF2'],
      ['countries-fill', 'fill-color', '#AFC8D8'],
      ['crimea-fill', 'fill-color', '#AFC8D8'],
      ['countries-boundary', 'line-color', 'rgba(247, 245, 240, 0.9)'],
      ['coastline', 'line-color', '#6D8978'],
      ['countries-label', 'text-color', '#43635C'],
      ['countries-label', 'text-halo-color', '#E7EFF2'],
      ['geolines', 'line-color', '#6D8978'],
      ['geolines-label', 'text-color', '#43635C'],
    ];
    colors.forEach(([layer, property, color]) => {
      if (map.getLayer(layer)) map.setPaintProperty(layer, property, color);
    });

    if (map.getLayer('countries-fill') && map.getSource('maplibre')) {
      map.addLayer({
        id: 'daily-country-highlight',
        type: 'fill',
        source: 'maplibre',
        'source-layer': 'countries',
        filter: ['==', ['get', 'ADM0_A3'], country.id.toUpperCase()],
        paint: { 'fill-color': '#C98F7D', 'fill-opacity': 0.78 },
      }, 'countries-boundary');
    }
  });
  map.on('error', (event) => {
    console.error('MapLibre map error:', event.error);
    showMapError('The globe could not load. Check the browser console for details.');
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
  new maplibregl.Marker({ color: '#43635C' })
    .setLngLat([country.location.longitude, country.location.latitude])
    .setPopup(new maplibregl.Popup({ offset: 18 }).setText(country.country))
    .addTo(map);
} catch (error) {
  console.error('Could not load the MapLibre globe:', error);
  showMapError('The globe could not load. Check the browser console for details.');
}
