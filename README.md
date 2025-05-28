# 🗺️ OSM App – Gradio-based OpenStreetMap Application

[![Dockerized](https://img.shields.io/badge/dockerized-yes-blue)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**OSM App** is a Python application that provides an interactive OpenStreetMap interface using [Gradio](https://www.gradio.app/), [Folium](https://python-visualization.github.io/folium/), and [OpenRouteService](https://openrouteservice.org/).

---

## ✨ Features

- 🔍 **Autocomplete Search** — Search for any location using Nominatim
- 🧭 **Smart Travel Mode Routing** — Get routes for driving, cycling, walking, etc.
- 📍 **Live Location View** — Show your current GPS position on the map
- 🐳 **Dockerized** — Run anywhere with a single command

---

## 📦 Installation Options

### ✅ Option 1: Run with Docker

#### 1. Clone the Repository
```bash
git clone https://github.com/uthrapathy-m/osm-app.git
cd osm-app


docker build -t osm-app .


docker run -p 7860:7860 osm-app


4. Open in Browser
Visit: http://localhost:7860
