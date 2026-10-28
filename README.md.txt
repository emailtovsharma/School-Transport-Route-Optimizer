# Campus Bus Route Optimization & Network Mapping

An interactive geospatial visualization tool built for **CAMPUS**. This project transforms route coordinates into clean, sequenced, metro-style route maps.

## 🌟 Key Features
- **Sequence-Preserving Routing:** Maps pickup paths strictly in order using custom Excel sequence rankings (`S.No`).
- **Privacy & Anonymization:** Addresses are dynamically sanitized using regular expressions to strip house/flat numbers, leaving only major Sector and Area identifiers.
- **Reliable Basemaps:** Powered by Esri World Topo tile servers for high availability and zero tile-blocking errors.
- **Layer Control & Interactivity:** Interactive toggle overlays allowing parents and route managers to inspect specific bus lines.

## 🛠️ Data Pipeline & Tech Stack
- **Python 3.x**
- **Pandas** (Data loading & sequencing)
- **Folium / Leaflet.js** (Geospatial rendering & custom legends)