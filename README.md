# 🗺️ Python Sample Application

[![Dockerized](https://img.shields.io/badge/dockerized-yes-blue)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


---

## ✨ Features

- 🔍 **Autocomplete Search** — Search for any location using Nominatim
- 🧭 **Smart Travel Mode Routing** — Get routes for driving, cycling, walking, etc.
- 📍 **Live Location View** — Show your current GPS position on the map
- 🐳 **Dockerized** — Run anywhere with a single command

---

## 📦 Installation Options

### ✅  Dockerize the Custom Python Application

#### Step 1. Clone the Repository

```
git clone https://github.com/uthrapathy-m/osm-app.git
```

#### Step 2. Moving to the Project Folder

```
cd osm-app
```

#### Step 3. Building the Docker Image

```
docker build -t osm-app .
```

#### Step 4. Running The Container

```
docker run -p 7860:7860 osm-app
```

#### Step 5. Open in Browser

```
Visit: http://localhost:7860
```

