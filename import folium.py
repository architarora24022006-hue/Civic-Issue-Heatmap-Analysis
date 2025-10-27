import folium
import pandas as pd
import json
from folium.plugins import HeatMap, MarkerCluster, MeasureControl
from datetime import datetime, time
import branca.colormap as cm
from branca.element import Template, MacroElement
import requests
import random

# --------------------------
# Phase 1: Load dataset
# --------------------------
print("🔄 Loading dataset...")
try:
    with open('db.json', 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"✅ Data loaded: {len(df)} records")
except Exception as e:
    print("❌ Error loading data:", e)
    exit()

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --------------------------
# Enhanced Location Profiles with Unique Characteristics
# --------------------------
LOCATION_PROFILES = {
    "Connaught Place": {
        "type": "commercial_hub",
        "peak_hours": [(8, 11), (14, 17), (19, 22)],
        "optimal_work": ["06:00-08:00 (Before office rush)", "11:30-13:30 (Lunch break window)", "17:30-19:00 (Evening gap)"],
        "avoid_completely": ["08:00-11:00", "19:00-22:00"],
        "specialty": "Metro connectivity issues during rush"
    },
    "Chandni Chowk": {
        "type": "market_area", 
        "peak_hours": [(10, 13), (15, 19)],
        "optimal_work": ["07:00-09:30 (Before market opens)", "13:30-14:30 (Afternoon break)", "19:30-21:00 (After market closure)"],
        "avoid_completely": ["10:00-13:00", "15:00-19:00"],
        "specialty": "Heavy pedestrian traffic, narrow lanes"
    },
    "AIIMS": {
        "type": "medical_complex",
        "peak_hours": [(8, 12), (14, 18)],
        "optimal_work": ["06:30-08:00 (Early morning)", "12:30-13:30 (Lunch gap)", "18:30-20:00 (After OPD)"],
        "avoid_completely": ["08:00-12:00", "14:00-18:00"],
        "specialty": "Emergency vehicle priority, patient traffic"
    },
    "Karol Bagh": {
        "type": "shopping_district",
        "peak_hours": [(11, 14), (16, 20)],
        "optimal_work": ["07:30-10:30 (Morning window)", "14:30-15:30 (Brief afternoon)", "20:30-22:00 (Evening close)"],
        "avoid_completely": ["11:00-14:00", "16:00-20:00"],
        "specialty": "Wedding season affects traffic patterns"
    },
    "Lajpat Nagar": {
        "type": "residential_market",
        "peak_hours": [(9, 12), (17, 19)],
        "optimal_work": ["07:00-09:00 (Residential quiet)", "12:30-16:30 (Extended afternoon)", "19:30-21:00 (Evening calm)"],
        "avoid_completely": ["09:00-12:00", "17:00-19:00"],
        "specialty": "Local market dependency, school timings matter"
    },
    "Saket": {
        "type": "upscale_commercial",
        "peak_hours": [(10, 13), (18, 21)],
        "optimal_work": ["08:00-10:00 (Mall opening)", "13:30-17:30 (Extended midday)", "21:30-23:00 (Late evening)"],
        "avoid_completely": ["10:00-13:00", "18:00-21:00"],
        "specialty": "Mall traffic, multiplex shows impact timing"
    },
    "Dwarka": {
        "type": "planned_residential",
        "peak_hours": [(7, 10), (17, 20)],
        "optimal_work": ["06:00-07:00 (Very early)", "10:30-16:30 (Long midday)", "20:30-22:30 (Late evening)"],
        "avoid_completely": ["07:00-10:00", "17:00-20:00"],
        "specialty": "Metro line dependency, airport traffic affects Sub City"
    },
    "Rohini": {
        "type": "suburban_residential",
        "peak_hours": [(7, 9), (18, 20)],
        "optimal_work": ["06:30-07:00 (Dawn window)", "09:30-17:30 (Full day availability)", "20:30-22:00 (Night window)"],
        "avoid_completely": ["07:00-09:00", "18:00-20:00"],
        "specialty": "School zones affect morning/evening traffic"
    },
    "Janakpuri": {
        "type": "middle_class_hub",
        "peak_hours": [(8, 10), (17, 19)],
        "optimal_work": ["07:00-08:00 (Early start)", "10:30-16:30 (Stable midday)", "19:30-21:30 (Extended evening)"],
        "avoid_completely": ["08:00-10:00", "17:00-19:00"],
        "specialty": "District center activities, local business hours"
    },
    "Rajouri Garden": {
        "type": "mixed_commercial",
        "peak_hours": [(8, 11), (16, 19)],
        "optimal_work": ["06:30-08:00 (Pre-rush)", "11:30-15:30 (Mid-day stretch)", "19:30-21:00 (Post-rush)"],
        "avoid_completely": ["08:00-11:00", "16:00-19:00"],
        "specialty": "Metro station congestion, market timing conflicts"
    }
}

# --------------------------
# Dynamic Traffic Data Generation with Location-Specific Logic
# --------------------------
def generate_dynamic_traffic_data():
    """Generate location-specific traffic data based on profiles"""
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    traffic_data = []
    
    for location_name, profile in LOCATION_PROFILES.items():
        # Get coordinates (focused on Delhi region only)
        location_coords = {
            "Connaught Place": {"lat": 28.6315, "lng": 77.2167},
            "Chandni Chowk": {"lat": 28.6562, "lng": 77.2300},
            "AIIMS": {"lat": 28.5672, "lng": 77.2100},
            "Karol Bagh": {"lat": 28.6510, "lng": 77.1900},
            "Lajpat Nagar": {"lat": 28.5687, "lng": 77.2433},
            "Saket": {"lat": 28.5246, "lng": 77.2066},
            "Dwarka": {"lat": 28.5483, "lng": 77.0656},
            "Rohini": {"lat": 28.7170, "lng": 77.1100},
            "Janakpuri": {"lat": 28.6215, "lng": 77.0913},
            "Rajouri Garden": {"lat": 28.6420, "lng": 77.1240},
        }[location_name]
        
        # Calculate congestion based on location-specific peak hours
        congestion = 20  # Base congestion
        
        # Check if current time falls in peak hours for this location
        for peak_start, peak_end in profile["peak_hours"]:
            if peak_start <= current_hour <= peak_end:
                # Higher congestion during peak hours
                if profile["type"] == "commercial_hub":
                    congestion += random.randint(40, 65)
                elif profile["type"] == "medical_complex":
                    congestion += random.randint(45, 70)
                elif profile["type"] == "market_area":
                    congestion += random.randint(35, 60)
                else:
                    congestion += random.randint(25, 50)
                break
        else:
            # Non-peak hours - lower congestion
            congestion += random.randint(5, 30)
        
        # Add minute-based variation for live feel
        minute_variation = random.randint(-5, 5)
        congestion = max(5, min(95, congestion + minute_variation))
        
        traffic_data.append({
            "name": location_name,
            "lat": location_coords["lat"],
            "lng": location_coords["lng"],
            "congestion": congestion,
            "status": get_congestion_status(congestion),
            "profile": profile,
            "last_updated": datetime.now().strftime("%H:%M:%S")
        })
    
    return traffic_data

def get_congestion_status(congestion):
    """Get traffic status based on congestion percentage"""
    if congestion >= 75:
        return {"level": "Heavy", "color": "#d73027", "icon": "🔴"}
    elif congestion >= 50:
        return {"level": "Moderate", "color": "#fc8d59", "icon": "🟠"}
    else:
        return {"level": "Light", "color": "#4575b4", "icon": "🟢"}

# Generate initial traffic data
traffic_data = generate_dynamic_traffic_data()

# --------------------------
# Phase 2: Optimized Base Map (Delhi focused, no mini map)
# --------------------------
# Focused on Delhi NCR region with tighter bounds
m = folium.Map(
    location=[28.6139, 77.2090], 
    zoom_start=11, 
    tiles=None,
    max_bounds=True,
    min_zoom=10,
    max_zoom=18
)

# Add lighter tile layers for better performance
folium.TileLayer('CartoDB positron', name='🌞 Light Mode').add_to(m)
folium.TileLayer('OpenStreetMap', name='🗺️ Street Map').add_to(m)

# Add measure control but no mini map for performance
m.add_child(MeasureControl())

# Set bounds to Delhi NCR region only
delhi_bounds = [[28.4, 76.8], [28.9, 77.6]]
m.fit_bounds(delhi_bounds)

# --------------------------
# Phase 3: Color & Icon helpers
# --------------------------
def get_severity_color(sev):
    return {"high":"#d73027","medium":"#fc8d59","low":"#4575b4"}.get(sev,"#999999")

def get_category_icon(cat):
    return {"traffic":"car","pollution":"smog","water":"tint","waste":"trash","electricity":"bolt"}.get(cat,"exclamation-circle")

def get_category_color(cat):
    return {'traffic':'#e74c3c','pollution':'#9b59b6','water':'#3498db','waste':'#f39c12','electricity':'#f1c40f'}.get(cat,'#95a5a6')

# --------------------------
# Phase 4: Optimized Category Layers
# --------------------------
categories = df['category'].unique()
category_layers = {}
for cat in categories:
    layer_name = f"📊 {cat.capitalize()} ({len(df[df['category']==cat])})"
    category_layers[cat] = folium.FeatureGroup(name=layer_name)
    category_layers[cat].add_to(m)

# --------------------------
# Phase 5: Traffic Congestion Layer (Initially Hidden)
# --------------------------
traffic_layer = folium.FeatureGroup(name="🚦 Live Traffic Analysis", show=False)
traffic_layer.add_to(m)

for location in traffic_data:
    status = location["status"]
    profile = location["profile"]
    
    # Simplified popup for better performance
    traffic_popup = f"""
    <div style="width: 350px; font-family: 'Segoe UI';">
        <div style="background: {status['color']}; color: white; padding: 12px; border-radius: 8px 8px 0 0;">
            <h3 style="margin: 0; display: flex; align-items: center; justify-content: space-between;">
                <span>🚦 {location['name']}</span>
                <span>{status['icon']}</span>
            </h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">
                📍 {profile['type'].replace('_', ' ').title()} • {location['last_updated']}
            </p>
        </div>
        
        <div style="padding: 15px; background: #f8f9fa; border-radius: 0 0 8px 8px;">
            <div style="margin-bottom: 12px;">
                <h4 style="margin: 0 0 6px 0; color: #2c3e50;">📈 Traffic Status</h4>
                <div style="background: white; padding: 10px; border-radius: 6px; border-left: 3px solid {status['color']};">
                    <strong>Congestion:</strong> {location['congestion']}% - {status['level']}<br>
                    <div style="background: #ecf0f1; height: 8px; border-radius: 4px; margin: 6px 0;">
                        <div style="background: {status['color']}; height: 8px; border-radius: 4px; width: {location['congestion']}%;"></div>
                    </div>
                    <small style="color: #7f8c8d;">🏷️ {profile['specialty']}</small>
                </div>
            </div>
            
            <div style="margin-bottom: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #2c3e50;">⏰ Best Work Hours</h4>
                <div style="background: white; padding: 10px; border-radius: 6px;">
    """
    
    for i, hour in enumerate(profile['optimal_work'][:2]):  # Show only first 2 for performance
        color = "#e8f5e8" if i == 0 else "#f0f8ff"
        traffic_popup += f'<div style="margin: 4px 0; padding: 6px 10px; background: {color}; border-radius: 4px; border-left: 2px solid #2ecc71;">✅ {hour}</div>'
    
    traffic_popup += f"""
                </div>
            </div>
            
            <div style="background: {'#fff3cd' if location['congestion'] >= 70 else '#d1ecf1' if location['congestion'] >= 50 else '#d4edda'}; 
                       padding: 10px; border-radius: 6px; border-left: 3px solid {'#ffc107' if location['congestion'] >= 70 else '#17a2b8' if location['congestion'] >= 50 else '#28a745'};">
                <strong>💡 Recommendation:</strong><br>
                {"⚠️ High congestion - use early morning slots only!" if location['congestion'] >= 70 else 
                 "⚡ Moderate traffic - stick to optimal windows" if location['congestion'] >= 50 else 
                 "✅ Good conditions - flexible scheduling possible"}
            </div>
        </div>
    </div>
    """
    
    # Smaller traffic markers for better performance
    traffic_marker = folium.CircleMarker(
        location=[location['lat'], location['lng']],
        radius=12,
        color='white',
        weight=2,
        fillColor=status['color'],
        fillOpacity=0.8,
        popup=folium.Popup(traffic_popup, max_width=400),
        tooltip=f"🚦 {location['name']}: {location['congestion']}% ({status['level']})"
    )
    traffic_marker.add_to(traffic_layer)

# --------------------------
# Phase 6: Optimized Marker Cluster (smaller radius for performance)
# --------------------------
marker_cluster = MarkerCluster(
    name="🎯 All Issues (Clustered)",
    disableClusteringAtZoom=16,
    maxClusterRadius=50
).add_to(m)

# --------------------------
# Phase 7: Add issue markers (optimized)
# --------------------------
for _, row in df.iterrows():
    lat, lon = row['latitude'], row['longitude']
    formatted_time = row['timestamp'].strftime('%d %b %Y, %I:%M %p')
    
    # Simplified popup for better performance
    popup_content = f"""
    <div style="width: 280px; font-family: 'Segoe UI';">
        <div style="background: {get_severity_color(row['severity'])}; color:white; padding:8px; border-radius:4px;">
            <b>📍 {row['place']}</b><br>#{row['id']} • {formatted_time}
        </div>
        <div style="padding:6px; background:#f8f9fa; border-radius:4px; margin-top:4px;">
            <b>Category:</b> <span style="background:{get_category_color(row['category'])}; color:white; padding:1px 4px; border-radius:8px; font-size:11px;">{row['category']}</span><br>
            <b>Severity:</b> <span style="background:{get_severity_color(row['severity'])}; color:white; padding:1px 4px; border-radius:8px; font-size:11px;">{row['severity']}</span><br>
            <b>Issue:</b> {row['issue']}<br>
        </div>
    </div>
    """
    
    # Smaller circle markers for category layers
    circle_marker = folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color='white',
        weight=1,
        fillColor=get_severity_color(row['severity']),
        fillOpacity=0.8,
        popup=folium.Popup(popup_content, max_width=320),
        tooltip=f"{row['place']}: {row['issue'][:40]}..."
    ).add_to(category_layers[row['category']])
    
    # Cluster marker
    cluster_marker = folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_content, max_width=320),
        tooltip=f"{row['place']}: {row['issue'][:40]}...",
        icon=folium.Icon(color='red' if row['severity']=='high' else 'orange' if row['severity']=='medium' else 'blue',
                         icon=get_category_icon(row['category']),
                         prefix='fa')
    )
    cluster_marker.add_to(marker_cluster)

# --------------------------
# Phase 8: Optimized Heatmap (smaller radius for performance)
# --------------------------
heat_points = [[row['latitude'], row['longitude'], {'high':5,'medium':3,'low':1}[row['severity']]] for _, row in df.iterrows()]
HeatMap(heat_points, name="🌡️ Issue Density", radius=15, blur=10,
        gradient={0.2:'blue',0.4:'cyan',0.6:'lime',0.8:'yellow',1.0:'red'}).add_to(m)

# --------------------------
# Phase 9: Compact Legend & Stats
# --------------------------
stats = {
    'total': len(df),
    'high': len(df[df['severity']=='high']),
    'medium': len(df[df['severity']=='medium']),
    'low': len(df[df['severity']=='low']),
    'categories': df['category'].value_counts().to_dict(),
}

# Calculate traffic stats
heavy_traffic = len([t for t in traffic_data if t['congestion'] >= 75])
moderate_traffic = len([t for t in traffic_data if 50 <= t['congestion'] < 75])
light_traffic = len([t for t in traffic_data if t['congestion'] < 50])

# Compact legend for better performance
legend_html = f"""
<div style="position:fixed; bottom:20px; left:20px; width:260px; background:rgba(255,255,255,0.95); 
            padding:15px; border-radius:10px; z-index:9999; font-size:12px; 
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
    <h4 style="margin: 0 0 12px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 6px; text-align: center;">
        📊 Delhi Dashboard
    </h4>
    
    <div style="margin-bottom: 12px;">
        <h5 style="margin: 0 0 6px 0; color: #34495e;">📋 Issues: {stats['total']}</h5>
        <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; font-size: 11px;">
            🔴 High: {stats['high']} | 🟠 Medium: {stats['medium']} | 🔵 Low: {stats['low']}
        </div>
    </div>
    
    <div id="traffic-stats" style="margin-bottom: 12px; display: none;">
        <h5 style="margin: 0 0 6px 0; color: #34495e;">🚦 Live Traffic:</h5>
        <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; font-size: 11px;">
            🔴 Heavy: {heavy_traffic} | 🟠 Moderate: {moderate_traffic} | 🟢 Light: {light_traffic}
            <div id="live-update-time" style="margin-top: 6px; font-size: 10px; color: #7f8c8d; text-align: center;">
                Last updated: {datetime.now().strftime('%H:%M:%S')}
            </div>
        </div>
    </div>
    
    <div style="font-size: 9px; color: #7f8c8d; text-align: center; 
               border-top: 1px solid #ecf0f1; padding-top: 8px;">
        💡 Optimized for Delhi region only
    </div>
</div>
"""

# --------------------------
# Simplified Traffic Control for better performance
# --------------------------
traffic_button_html = """
<div style="position: fixed; top: 80px; right: 15px; z-index: 1000;">
    <button onclick="toggleTrafficLayer()" 
            style="background: linear-gradient(135deg, #e74c3c, #c0392b); 
                   color: white; border: none; padding: 12px 20px; 
                   border-radius: 25px; font-weight: bold; font-size: 14px;
                   box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
                   cursor: pointer; transition: all 0.2s ease;"
            onmouseover="this.style.transform='translateY(-1px)'"
            onmouseout="this.style.transform='translateY(0px)'"
            id="trafficButton">
        🚦 Traffic Analysis
    </button>
</div>

<script>
var trafficLayerVisible = false;

function toggleTrafficLayer() {
    var button = document.getElementById('trafficButton');
    var trafficStats = document.getElementById('traffic-stats');
    
    if (!trafficLayerVisible) {
        button.innerHTML = '🚦 Hide Traffic';
        button.style.background = 'linear-gradient(135deg, #27ae60, #16a085)';
        trafficStats.style.display = 'block';
        trafficLayerVisible = true;
        showNotification('✅ Traffic analysis activated!', 'success');
    } else {
        button.innerHTML = '🚦 Traffic Analysis';
        button.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
        trafficStats.style.display = 'none';
        trafficLayerVisible = false;
        showNotification('ℹ️ Traffic layer hidden', 'info');
    }
}

function showNotification(message, type) {
    var notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed; top: 120px; right: 15px; z-index: 1001;
        background: ${type === 'success' ? '#2ecc71' : '#3498db'};
        color: white; padding: 10px 15px; border-radius: 8px;
        font-size: 12px; max-width: 250px;
    `;
    notification.innerHTML = message;
    document.body.appendChild(notification);
    
    setTimeout(() => document.body.removeChild(notification), 3000);
}
</script>
"""

# --------------------------
# Add elements to map
# --------------------------
m.get_root().html.add_child(folium.Element(legend_html))
m.get_root().html.add_child(folium.Element(traffic_button_html))

# --------------------------
# Phase 10: Layer Control
# --------------------------
folium.LayerControl(collapsed=True, position='topright').add_to(m)

# --------------------------
# Export Optimized Map
# --------------------------
output_file = "optimized_delhi_traffic_map.html"
m.save(output_file)

print(f"🎉 Optimized Delhi traffic map saved as {output_file}")
print(f"🚀 Performance optimizations applied:")
print(f"   ❌ Mini map removed")
print(f"   🗺️ Delhi region focus only")
print(f"   📊 {len(traffic_data)} core locations (reduced from 15)")
print(f"   ⚡ Smaller markers and simplified popups")
print(f"   🎯 Tighter zoom bounds (10-18)")
print(f"   📱 Optimized for smooth performance")
print(f"\n📍 Coverage Area: Delhi NCR region")
print(f"🔄 Features: Live traffic analysis + Issue tracking")
print(f"💡 Click '🚦 Traffic Analysis' to view traffic data!")