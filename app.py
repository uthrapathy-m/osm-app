import gradio as gr
import folium
import requests
from geopy.geocoders import Nominatim
import openrouteservice
from openrouteservice import convert

ORS_API_KEY = "5b3ce3597851110001cf624823eb9dd1265d441e87b1b8ae46a65c19"
geolocator = Nominatim(user_agent="gradio-osm")

def get_suggestions(query):
    if not query or len(query) < 3:
        return []
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "addressdetails": 1, "limit": 5, "autocomplete": 1}
    headers = {"User-Agent": "gradio-osm-autocomplete"}
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    return [f"{r['display_name']}|{r['lat']}|{r['lon']}" for r in results]

def update_dropdown(query):
    suggestions = get_suggestions(query)
    return gr.update(choices=suggestions, value=suggestions[0] if suggestions else None)

def locate_selected_suggestion(suggestion):
    if not suggestion or "|" not in suggestion:
        return "<b>No valid location selected.</b>", ""
    
    name, lat, lon = suggestion.split("|")
    lat, lon = float(lat), float(lon)

    m = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], popup=name).add_to(m)

    # 🧠 Step 1: Get osm_id & type
    query_url = f"https://nominatim.openstreetmap.org/search?format=json&q={name}&polygon_geojson=1"
    headers = {"User-Agent": "gradio-osm-autocomplete"}
    response = requests.get(query_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data and 'geojson' in data[0]:
            geo = data[0]['geojson']
            if geo['type'] == 'Polygon':
                folium.Polygon(locations=[(pt[1], pt[0]) for pt in geo['coordinates'][0]],
                               color='orange', fill=True, fill_opacity=0.2,
                               popup="Boundary").add_to(m)
            elif geo['type'] == 'MultiPolygon':
                for polygon in geo['coordinates']:
                    folium.Polygon(locations=[(pt[1], pt[0]) for pt in polygon[0]],
                                   color='orange', fill=True, fill_opacity=0.2,
                                   popup="Boundary").add_to(m)

    return m._repr_html_(), f"📍 {name}"


def show_my_location(lat=None, lon=None):
    if lat is None or lon is None or lat == 0 or lon == 0:
        return "<b>Could not get your live location. Please enable location access.</b>"
    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], popup="📍 You are here", icon=folium.Icon(color="purple")).add_to(m)
    return m._repr_html_()

def get_route(from_place, to_place, mode_label):
    profile_map = {
        "Best travel modes": "driving-car",
        "Driving": "driving-car",
        "Two-Wheeler": "cycling-electric",
        "Walking": "foot-walking",
        "Cycling": "cycling-regular",
        "Transit": None,  # Not available in OpenRouteService
        "Flights": None   # Not supported
    }

    profile = profile_map.get(mode_label)
    if not profile:
        return f"<b>{mode_label} is not supported in this demo (OpenRouteService limitation).</b>", ""

    loc_from = geolocator.geocode(from_place)
    loc_to = geolocator.geocode(to_place)
    if not loc_from or not loc_to:
        return "<b>Could not find one or both locations.</b>", ""

    client = openrouteservice.Client(key=ORS_API_KEY)
    coords = ((loc_from.longitude, loc_from.latitude), (loc_to.longitude, loc_to.latitude))

    try:
        route = client.directions(coords, profile=profile)
    except Exception as e:
        return f"<b>Routing error:</b> {e}", ""

    geometry = route['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)
    route_coords = [(pt[1], pt[0]) for pt in decoded['coordinates']]

    summary = route['routes'][0]['summary']
    distance_km = summary['distance'] / 1000
    duration_sec = int(summary['duration'])

    hours = duration_sec // 3600
    minutes = (duration_sec % 3600) // 60
    seconds = duration_sec % 60

    duration_str = []
    if hours > 0:
        duration_str.append(f"{hours} hr")
    if minutes > 0:
        duration_str.append(f"{minutes} min")
    if hours == 0 and seconds > 0:
        duration_str.append(f"{seconds} sec")

    duration_hr = summary['duration'] / 3600
    avg_speed = distance_km / duration_hr if duration_hr > 0 else 0

    info_text = (
        f"📏 Distance: {distance_km:.2f} km | "
        f"⏱ Duration: {' '.join(duration_str)} | "
        f"🚗 Avg Speed: {avg_speed:.1f} km/h"
    )

    m = folium.Map(location=[(loc_from.latitude + loc_to.latitude)/2, (loc_from.longitude + loc_to.longitude)/2], zoom_start=13)
    folium.Marker(route_coords[0], popup=from_place, icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(route_coords[-1], popup=to_place, icon=folium.Icon(color="red")).add_to(m)

    styles = {
        "driving-car": {"color": "blue"},
        "foot-walking": {"color": "green", "weight": 4, "dash_array": "10,10"},
        "cycling-regular": {"color": "orange", "weight": 4, "dash_array": "1,6"},
        "cycling-electric": {"color": "purple", "weight": 4, "dash_array": "1,6"}
    }

    style = styles.get(profile, {"color": "gray"})
    folium.PolyLine(route_coords, color=style["color"], weight=5, opacity=0.8).add_to(m)
    m.fit_bounds([route_coords[0], route_coords[-1]])

    return m._repr_html_(), info_text

with gr.Blocks() as demo:
    gr.Markdown("## 🗺️ Bhuvanesh Map: Autocomplete, Smart Travel Modes, Live Location")

    with gr.Tab("🔍 Search & View Location"):
        search_input = gr.Textbox(label="Enter a Location")
        suggestions_dropdown = gr.Dropdown(label="Suggestions", choices=[], interactive=True, allow_custom_value=True)
        map_output = gr.HTML()
        address_output = gr.Label()

        search_input.change(fn=update_dropdown, inputs=search_input, outputs=suggestions_dropdown)
        suggestions_dropdown.change(fn=locate_selected_suggestion, inputs=suggestions_dropdown, outputs=[map_output, address_output])

        gr.Markdown("### 📍 Show My Location")
        show_location_btn = gr.Button("📍 Show My Location")
        my_location_output = gr.HTML()

        show_location_btn.click(
            fn=show_my_location,
            inputs=[gr.Number(visible=False), gr.Number(visible=False)],
            outputs=my_location_output,
            js="""
            () => new Promise((resolve) => {
                navigator.geolocation.getCurrentPosition(
                    (pos) => resolve([pos.coords.latitude, pos.coords.longitude]),
                    () => resolve([null, null])
                );
            })
            """
        )

    with gr.Tab("🧭 Get Directions"):
        from_input = gr.Textbox(label="From")
        to_input = gr.Textbox(label="To")
        mode_select = gr.Radio(
            ["Best travel modes", "Driving", "Two-Wheeler", "Walking", "Cycling"],
            value="Best travel modes",
            label="Mode of Transport"
        )
        direction_button = gr.Button("Get Directions")
        directions_map = gr.HTML()
        route_info = gr.Label(label="Route Info")

        direction_button.click(
            fn=get_route,
            inputs=[from_input, to_input, mode_select],
            outputs=[directions_map, route_info]
        )

demo.launch(server_name="0.0.0.0", server_port=7860)

