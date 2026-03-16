import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { casesApi } from '../services/api';

// Fix leaflet default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Known trafficking route checkpoints for visualization
const ROUTE_NODES = [
  { id: 'MSD', name: 'Murshidabad', lat: 24.183, lng: 88.267, type: 'source' },
  { id: 'MLD', name: 'Malda', lat: 25.009, lng: 88.140, type: 'source' },
  { id: 'HWH', name: 'Howrah Station', lat: 22.585, lng: 88.316, type: 'transit_hub' },
  { id: 'SDAH', name: 'Sealdah Station', lat: 22.565, lng: 88.370, type: 'transit_hub' },
  { id: 'NJP', name: 'New Jalpaiguri', lat: 26.549, lng: 88.474, type: 'transit_hub' },
  { id: 'NDLS', name: 'New Delhi Station', lat: 28.643, lng: 77.220, type: 'transit_hub' },
  { id: 'CSTM', name: 'Mumbai CST', lat: 18.940, lng: 72.835, type: 'transit_hub' },
  { id: 'CNB', name: 'Kanpur', lat: 26.459, lng: 80.331, type: 'transit_hub' },
  { id: 'MAS', name: 'Chennai', lat: 13.083, lng: 80.275, type: 'destination' },
];

const MapPage: React.FC = () => {
  const { data: casesData } = useQuery({
    queryKey: ['cases', 'active', 'map'],
    queryFn: () => casesApi.list({ status: 'active', page_size: 100 }),
  });

  const cases = casesData?.data?.items?.filter((c: any) =>
    c.last_seen_latitude && c.last_seen_longitude
  ) || [];

  const getMarkerColor = (type: string) => {
    switch (type) {
      case 'source': return '#ef5350';
      case 'transit_hub': return '#ffa726';
      case 'destination': return '#42a5f5';
      default: return '#9e9e9e';
    }
  };

  const createColoredIcon = (color: string) =>
    L.divIcon({
      html: `<div style="
        width:14px; height:14px; border-radius:50%;
        background:${color}; border:2px solid rgba(255,255,255,0.8);
        box-shadow:0 0 8px ${color}88;
      "></div>`,
      className: '',
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>Live Intelligence Map</h1>
          <p className="text-muted text-sm">
            Active cases, sightings, and known trafficking corridors
          </p>
        </div>
        <div className="flex gap-4 text-sm">
          {[
            { color: '#ef5350', label: 'Source Districts' },
            { color: '#ffa726', label: 'Transit Hubs' },
            { color: '#42a5f5', label: 'Destinations' },
            { color: '#66bb6a', label: 'Active Cases' },
          ].map(item => (
            <div key={item.label} className="flex items-center gap-2">
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: item.color }} />
              <span className="text-muted">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="map-container" style={{ height: '600px' }}>
        <MapContainer
          center={[23.5, 85.0]}
          zoom={5}
          style={{ height: '100%', width: '100%', background: '#0d0d1a' }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; OpenStreetMap contributors &copy; CARTO'
          />

          {/* Route nodes */}
          {ROUTE_NODES.map(node => (
            <Marker
              key={node.id}
              position={[node.lat, node.lng]}
              icon={createColoredIcon(getMarkerColor(node.type))}
            >
              <Popup>
                <div style={{ fontFamily: 'sans-serif' }}>
                  <strong>{node.name}</strong>
                  <br />
                  <span style={{ fontSize: '0.75rem', color: '#666' }}>
                    {node.type.replace('_', ' ').toUpperCase()}
                  </span>
                  <br />
                  <span style={{ fontSize: '0.75rem' }}>Code: {node.id}</span>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Active cases */}
          {cases.map((c: any) => (
            <React.Fragment key={c.id}>
              <Marker
                position={[c.last_seen_latitude, c.last_seen_longitude]}
                icon={createColoredIcon('#66bb6a')}
              >
                <Popup>
                  <div style={{ fontFamily: 'sans-serif' }}>
                    <strong>{c.full_name}</strong>
                    <br />
                    <span style={{ fontSize: '0.75rem', color: '#666' }}>{c.case_number}</span>
                    <br />
                    <span style={{ fontSize: '0.75rem' }}>Priority: {c.priority}</span>
                    <br />
                    <span style={{ fontSize: '0.75rem' }}>
                      Missing since: {new Date(c.date_missing).toLocaleDateString('en-IN')}
                    </span>
                  </div>
                </Popup>
              </Marker>
              <Circle
                center={[c.last_seen_latitude, c.last_seen_longitude]}
                radius={5000}
                pathOptions={{ color: '#66bb6a', fillColor: '#66bb6a', fillOpacity: 0.1, weight: 1 }}
              />
            </React.Fragment>
          ))}
        </MapContainer>
      </div>

      <div className="card" style={{ marginTop: '16px' }}>
        <p className="text-sm text-muted">
          💡 <strong>Map shows</strong> known trafficking corridors (West Bengal → Delhi → Mumbai route),
          source districts (red), transit hubs (orange), destinations (blue), and active case locations (green).
          Real-time CCTV camera locations would be overlaid in production with railway/transport hub API integration.
        </p>
      </div>
    </div>
  );
};

export default MapPage;
