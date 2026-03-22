import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function GeoMap() {
  const [positions, setPositions] = useState([
    { id: 'E007', lat: 40.7128, lng: -74.0060, color: '#ef4444' },
    { id: 'E012', lat: 40.7250, lng: -73.9900, color: '#f97316' },
    { id: 'E015', lat: 40.6950, lng: -74.0250, color: '#eab308' },
  ]);

  // Simulate convergence
  useEffect(() => {
    const interval = setInterval(() => {
      setPositions(prev => prev.map(p => {
        // Move slightly towards center (40.7100, -74.0000)
        const targetLat = 40.7100;
        const targetLng = -74.0000;
        return {
          ...p,
          lat: p.lat + (targetLat - p.lat) * 0.05,
          lng: p.lng + (targetLng - p.lng) * 0.05
        };
      }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-48 w-full relative z-0 bg-[#0a0a0f]">
      <MapContainer 
        center={[40.7100, -74.0000]} 
        zoom={12} 
        style={{ height: '100%', width: '100%', background: '#0a0a0f' }} 
        zoomControl={false}
        attributionControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        {positions.map(p => (
          <CircleMarker 
            key={p.id} 
            center={[p.lat, p.lng]} 
            radius={6} 
            pathOptions={{ color: p.color, fillColor: p.color, fillOpacity: 0.7, weight: 2 }}
          >
            <Popup className="bg-black text-white border-white/10">{p.id}</Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="absolute top-2 left-2 z-[400] bg-black/80 backdrop-blur-sm px-2 py-1 rounded text-[10px] font-mono text-slate-300 border border-white/10 shadow-lg">
        <span className="inline-block w-2 h-2 rounded-full bg-red-500 animate-pulse mr-1.5"></span>
        GEO-CONVERGENCE
      </div>
    </div>
  );
}
