from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import folium
from folium import plugins
import json
import csv
import io
import tempfile
import os
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union, transform
import geopandas as gpd
import pandas as pd
import math
import pyproj
from pyproj import Transformer
import simplekml
import geojson
import ezdxf
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///topography.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class ReferencePoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    elevation = db.Column(db.Float)
    point_type = db.Column(db.String(50), default='waypoint')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'elevation': self.elevation,
            'point_type': self.point_type
        }

class SurveyPolygon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    coordinates = db.Column(db.Text, nullable=False)  # JSON string of coordinates
    area_sqm = db.Column(db.Float)
    perimeter_m = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    polygon_type = db.Column(db.String(50), default='survey_area')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'coordinates': json.loads(self.coordinates),
            'area_sqm': self.area_sqm,
            'perimeter_m': self.perimeter_m,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'polygon_type': self.polygon_type
        }

# Create tables
with app.app_context():
    db.create_all()

# Utility functions
def lat_lon_to_utm(lat, lon):
    """Convert latitude/longitude to UTM coordinates"""
    try:
        # Determine UTM zone
        utm_zone = int((lon + 180) / 6) + 1
        hemisphere = 'north' if lat >= 0 else 'south'
        
        # Create transformer
        transformer = Transformer.from_crs(
            "EPSG:4326",  # WGS84
            f"EPSG:326{utm_zone:02d}" if hemisphere == 'north' else f"EPSG:327{utm_zone:02d}",
            always_xy=True
        )
        
        x, y = transformer.transform(lon, lat)
        return f"Zone {utm_zone}{hemisphere[0].upper()}: {x:.2f}E, {y:.2f}N"
    except:
        return "UTM conversion failed"

def calculate_polygon_metrics(coordinates):
    """Calculate area and perimeter of a polygon"""
    if len(coordinates) < 3:
        return 0, 0
    
    # Create shapely polygon (lon, lat format for shapely)
    coords_shapely = [(coord[1], coord[0]) for coord in coordinates]
    polygon = Polygon(coords_shapely)
    
    # Use more accurate geodesic calculations
    # Convert to UTM for area calculation
    first_point = coordinates[0]
    utm_zone = int((first_point[1] + 180) / 6) + 1
    hemisphere = 'north' if first_point[0] >= 0 else 'south'
    
    try:
        # Transform to UTM
        transformer = Transformer.from_crs(
            "EPSG:4326",
            f"EPSG:326{utm_zone:02d}" if hemisphere == 'north' else f"EPSG:327{utm_zone:02d}",
            always_xy=True
        )
        
        utm_coords = []
        for coord in coordinates:
            x, y = transformer.transform(coord[1], coord[0])  # lon, lat
            utm_coords.append((x, y))
        
        utm_polygon = Polygon(utm_coords)
        area_sqm = utm_polygon.area
        perimeter_m = utm_polygon.length
        
        return area_sqm, perimeter_m
    except:
        # Fallback to simple calculation
        area_degrees = polygon.area
        area_sqm = area_degrees * (111320 ** 2)  # Rough approximation
        perimeter_m = polygon.length * 111320
        return area_sqm, perimeter_m

def dms_to_decimal(degrees, minutes, seconds):
    """Convert degrees, minutes, seconds to decimal degrees"""
    return degrees + minutes/60.0 + seconds/3600.0

def decimal_to_dms(decimal_degrees):
    """Convert decimal degrees to degrees, minutes, seconds"""
    degrees = int(decimal_degrees)
    minutes_float = (decimal_degrees - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    return degrees, minutes, seconds

def calculate_point_from_distance_azimuth(start_lat, start_lon, distance_m, azimuth_degrees):
    """Calculate new point from start point, distance (meters), and azimuth (degrees)"""
    from geopy.distance import geodesic
    
    # Use geopy for accurate geodesic calculations
    start_point = (start_lat, start_lon)
    
    # Calculate bearing (azimuth) - geopy uses bearing from north clockwise
    bearing = azimuth_degrees
    
    # Calculate destination point
    destination = geodesic(meters=distance_m).destination(start_point, bearing)
    
    return destination.latitude, destination.longitude

def calculate_azimuth_distance(lat1, lon1, lat2, lon2):
    """Calculate azimuth and distance between two points"""
    from geopy.distance import geodesic
    import math
    
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    
    # Calculate distance
    dist = geodesic(point1, point2).meters
    
    # Calculate bearing (azimuth) using basic spherical trigonometry
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    
    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360  # Normalize to 0-360
    
    return bearing, dist

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def show_map():
    # Get all reference points and polygons
    points = ReferencePoint.query.all()
    polygons = SurveyPolygon.query.all()
    
    # Create folium map centered on first point or default location
    if points:
        center_lat = sum(p.latitude for p in points) / len(points)
        center_lon = sum(p.longitude for p in points) / len(points)
    else:
        center_lat, center_lon = 40.7128, -74.0060  # Default to NYC
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Add multiple map layers with better naming
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='OpenStreetMap',
        name='Street Map',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Terrain Map',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='CartoDB',
        name='Light Map',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add reference points to map
    for point in points:
        popup_text = f"""
        <b>{point.name}</b><br>
        {point.description or 'No description'}<br>
        Lat: {point.latitude:.6f}<br>
        Lon: {point.longitude:.6f}<br>
        Elevation: {point.elevation or 'N/A'} m<br>
        UTM: {lat_lon_to_utm(point.latitude, point.longitude)}
        """
        
        folium.Marker(
            [point.latitude, point.longitude],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=point.name,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
    
    # Add polygons to map
    for polygon in polygons:
        coords = json.loads(polygon.coordinates)
        popup_text = f"""
        <b>{polygon.name}</b><br>
        {polygon.description or 'No description'}<br>
        Area: {polygon.area_sqm:.2f} m²<br>
        Perimeter: {polygon.perimeter_m:.2f} m<br>
        Vertices: {len(coords)}
        """
        
        folium.Polygon(
            locations=coords,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=polygon.name,
            color='red',
            weight=2,
            fillColor='red',
            fillOpacity=0.2
        ).add_to(m)
        
        # Add vertex markers
        for i, coord in enumerate(coords):
            folium.CircleMarker(
                coord,
                radius=3,
                popup=f"Vertex {i+1}: {coord[0]:.6f}, {coord[1]:.6f}",
                color='red',
                fillColor='red',
                fillOpacity=0.8
            ).add_to(m)
    
    # Add drawing tools
    draw = plugins.Draw(
        export=True,
        filename='survey_data.geojson',
        position='topleft',
        draw_options={
            'polyline': True,
            'polygon': True,
            'circle': False,
            'rectangle': True,
            'marker': True,
            'circlemarker': False,
        },
        edit_options={'edit': True}
    )
    draw.add_to(m)
    
    # Add measurement tools
    plugins.MeasureControl().add_to(m)
    
    # Add coordinate grid
    # Note: Folium doesn't have built-in coordinate grid, so we'll add it via JavaScript
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Convert map to HTML
    map_html = m._repr_html_()
    
    return render_template('map.html', map_html=map_html, points=points, polygons=polygons)

@app.route('/api/points', methods=['GET'])
def get_points():
    points = ReferencePoint.query.all()
    return jsonify([point.to_dict() for point in points])

@app.route('/api/points', methods=['POST'])
def add_point():
    data = request.get_json()
    
    point = ReferencePoint(
        name=data['name'],
        description=data.get('description', ''),
        latitude=float(data['latitude']),
        longitude=float(data['longitude']),
        elevation=float(data['elevation']) if data.get('elevation') else None,
        point_type=data.get('point_type', 'waypoint')
    )
    
    db.session.add(point)
    db.session.commit()
    
    return jsonify(point.to_dict()), 201

@app.route('/api/points/<int:point_id>', methods=['PUT'])
def update_point(point_id):
    point = ReferencePoint.query.get_or_404(point_id)
    data = request.get_json()
    
    point.name = data.get('name', point.name)
    point.description = data.get('description', point.description)
    point.latitude = float(data.get('latitude', point.latitude))
    point.longitude = float(data.get('longitude', point.longitude))
    point.elevation = float(data['elevation']) if data.get('elevation') else point.elevation
    point.point_type = data.get('point_type', point.point_type)
    
    db.session.commit()
    return jsonify(point.to_dict())

@app.route('/api/points/<int:point_id>', methods=['DELETE'])
def delete_point(point_id):
    point = ReferencePoint.query.get_or_404(point_id)
    db.session.delete(point)
    db.session.commit()
    return '', 204

@app.route('/api/calculate/distance')
def calculate_distance():
    point1_id = request.args.get('point1_id')
    point2_id = request.args.get('point2_id')
    
    if not point1_id or not point2_id:
        return jsonify({'error': 'Both point1_id and point2_id are required'}), 400
    
    point1 = ReferencePoint.query.get_or_404(point1_id)
    point2 = ReferencePoint.query.get_or_404(point2_id)
    
    # Create Shapely points
    p1 = Point(point1.longitude, point1.latitude)
    p2 = Point(point2.longitude, point2.latitude)
    
    # Calculate distance using Shapely (approximate)
    distance_degrees = p1.distance(p2)
    # Convert to meters (rough approximation)
    distance_meters = distance_degrees * 111320
    
    # Calculate elevation difference
    elevation_diff = None
    if point1.elevation and point2.elevation:
        elevation_diff = abs(point1.elevation - point2.elevation)
    
    return jsonify({
        'distance_meters': distance_meters,
        'distance_degrees': distance_degrees,
        'elevation_difference': elevation_diff,
        'point1': point1.to_dict(),
        'point2': point2.to_dict()
    })

@app.route('/api/calculate/area')
def calculate_area():
    point_ids = request.args.getlist('point_ids')
    
    if len(point_ids) < 3:
        return jsonify({'error': 'At least 3 points are required to calculate area'}), 400
    
    points = []
    for point_id in point_ids:
        point = ReferencePoint.query.get_or_404(point_id)
        points.append((point.longitude, point.latitude))
    
    # Create polygon
    polygon = Polygon(points)
    
    # Calculate area (in square degrees, rough approximation)
    area_degrees = polygon.area
    # Convert to square meters (very rough approximation)
    area_meters = area_degrees * (111320 ** 2)
    
    return jsonify({
        'area_square_meters': area_meters,
        'area_square_degrees': area_degrees,
        'perimeter_meters': polygon.length * 111320,
        'points_count': len(points)
    })

@app.route('/api/calculate/point_from_distance_azimuth', methods=['POST'])
def calculate_point_from_distance_azimuth_api():
    """Calculate new point coordinates from reference point, distance and azimuth"""
    data = request.get_json()
    
    try:
        start_lat = float(data['start_lat'])
        start_lon = float(data['start_lon'])
        distance_m = float(data['distance_m'])
        azimuth_degrees = float(data['azimuth_degrees'])
        
        # Calculate new point
        new_lat, new_lon = calculate_point_from_distance_azimuth(
            start_lat, start_lon, distance_m, azimuth_degrees
        )
        
        return jsonify({
            'latitude': new_lat,
            'longitude': new_lon,
            'utm_coordinates': lat_lon_to_utm(new_lat, new_lon)
        })
        
    except Exception as e:
        return jsonify({'error': f'Calculation failed: {str(e)}'}), 400

@app.route('/api/calculate/azimuth_distance', methods=['POST'])
def calculate_azimuth_distance_api():
    """Calculate azimuth and distance between two points"""
    data = request.get_json()
    
    try:
        lat1 = float(data['lat1'])
        lon1 = float(data['lon1'])
        lat2 = float(data['lat2'])
        lon2 = float(data['lon2'])
        
        # Calculate azimuth and distance
        azimuth, distance = calculate_azimuth_distance(lat1, lon1, lat2, lon2)
        
        # Convert azimuth to DMS
        degrees, minutes, seconds = decimal_to_dms(azimuth)
        
        return jsonify({
            'azimuth_decimal': azimuth,
            'azimuth_dms': {
                'degrees': degrees,
                'minutes': minutes,
                'seconds': seconds
            },
            'distance_meters': distance,
            'distance_km': distance / 1000
        })
        
    except Exception as e:
        return jsonify({'error': f'Calculation failed: {str(e)}'}), 400

# Polygon API endpoints
@app.route('/api/polygons', methods=['GET'])
def get_polygons():
    polygons = SurveyPolygon.query.all()
    return jsonify([polygon.to_dict() for polygon in polygons])

@app.route('/api/polygons', methods=['POST'])
def add_polygon():
    data = request.get_json()
    
    coordinates = data['coordinates']
    area_sqm, perimeter_m = calculate_polygon_metrics(coordinates)
    
    polygon = SurveyPolygon(
        name=data['name'],
        description=data.get('description', ''),
        coordinates=json.dumps(coordinates),
        area_sqm=area_sqm,
        perimeter_m=perimeter_m,
        polygon_type=data.get('polygon_type', 'survey_area')
    )
    
    db.session.add(polygon)
    db.session.commit()
    
    return jsonify(polygon.to_dict()), 201

@app.route('/api/polygons/<int:polygon_id>', methods=['PUT'])
def update_polygon(polygon_id):
    polygon = SurveyPolygon.query.get_or_404(polygon_id)
    data = request.get_json()
    
    if 'coordinates' in data:
        coordinates = data['coordinates']
        area_sqm, perimeter_m = calculate_polygon_metrics(coordinates)
        polygon.coordinates = json.dumps(coordinates)
        polygon.area_sqm = area_sqm
        polygon.perimeter_m = perimeter_m
    
    polygon.name = data.get('name', polygon.name)
    polygon.description = data.get('description', polygon.description)
    polygon.polygon_type = data.get('polygon_type', polygon.polygon_type)
    
    db.session.commit()
    return jsonify(polygon.to_dict())

@app.route('/api/polygons/<int:polygon_id>', methods=['DELETE'])
def delete_polygon(polygon_id):
    polygon = SurveyPolygon.query.get_or_404(polygon_id)
    db.session.delete(polygon)
    db.session.commit()
    return '', 204

# Import/Export endpoints
@app.route('/api/export/csv')
def export_csv():
    """Export points and polygons to CSV"""
    points = ReferencePoint.query.all()
    polygons = SurveyPolygon.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write points
    writer.writerow(['Type', 'Name', 'Description', 'Latitude', 'Longitude', 'Elevation', 'Point_Type', 'Area_SqM', 'Perimeter_M'])
    
    for point in points:
        writer.writerow([
            'Point', point.name, point.description or '', point.latitude, point.longitude,
            point.elevation or '', point.point_type, '', ''
        ])
    
    for polygon in polygons:
        coords = json.loads(polygon.coordinates)
        coord_str = '; '.join([f"{coord[0]},{coord[1]}" for coord in coords])
        writer.writerow([
            'Polygon', polygon.name, polygon.description or '', coord_str, '',
            '', polygon.polygon_type, polygon.area_sqm, polygon.perimeter_m
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'survey_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/export/geojson')
def export_geojson():
    """Export points and polygons to GeoJSON"""
    points = ReferencePoint.query.all()
    polygons = SurveyPolygon.query.all()
    
    features = []
    
    # Add points
    for point in points:
        feature = geojson.Feature(
            geometry=geojson.Point((point.longitude, point.latitude)),
            properties={
                'name': point.name,
                'description': point.description,
                'elevation': point.elevation,
                'point_type': point.point_type,
                'type': 'point'
            }
        )
        features.append(feature)
    
    # Add polygons
    for polygon in polygons:
        coords = json.loads(polygon.coordinates)
        # Convert to [lon, lat] format for GeoJSON
        geojson_coords = [[[coord[1], coord[0]] for coord in coords]]
        
        feature = geojson.Feature(
            geometry=geojson.Polygon(geojson_coords),
            properties={
                'name': polygon.name,
                'description': polygon.description,
                'polygon_type': polygon.polygon_type,
                'area_sqm': polygon.area_sqm,
                'perimeter_m': polygon.perimeter_m,
                'type': 'polygon'
            }
        )
        features.append(feature)
    
    feature_collection = geojson.FeatureCollection(features)
    
    return send_file(
        io.BytesIO(json.dumps(feature_collection).encode()),
        mimetype='application/geo+json',
        as_attachment=True,
        download_name=f'survey_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.geojson'
    )

@app.route('/api/export/kml')
def export_kml():
    """Export points and polygons to KML"""
    points = ReferencePoint.query.all()
    polygons = SurveyPolygon.query.all()
    
    kml = simplekml.Kml()
    
    # Add points
    points_folder = kml.newfolder(name="Reference Points")
    for point in points:
        pnt = points_folder.newpoint(name=point.name)
        pnt.coords = [(point.longitude, point.latitude, point.elevation or 0)]
        pnt.description = f"""
        Description: {point.description or 'No description'}
        Point Type: {point.point_type}
        Elevation: {point.elevation or 'N/A'} m
        Coordinates: {point.latitude:.6f}, {point.longitude:.6f}
        UTM: {lat_lon_to_utm(point.latitude, point.longitude)}
        """
    
    # Add polygons
    polygons_folder = kml.newfolder(name="Survey Polygons")
    for polygon in polygons:
        coords = json.loads(polygon.coordinates)
        pol = polygons_folder.newpolygon(name=polygon.name)
        # Convert to (lon, lat, elevation) format for KML
        kml_coords = [(coord[1], coord[0], 0) for coord in coords]
        pol.outerboundaryis = kml_coords
        pol.description = f"""
        Description: {polygon.description or 'No description'}
        Polygon Type: {polygon.polygon_type}
        Area: {polygon.area_sqm:.2f} m²
        Perimeter: {polygon.perimeter_m:.2f} m
        Vertices: {len(coords)}
        """
        pol.style.polystyle.color = simplekml.Color.red
        pol.style.polystyle.fill = 1
        pol.style.polystyle.outline = 1
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.kml')
    kml.save(temp_file.name)
    
    return send_file(
        temp_file.name,
        mimetype='application/vnd.google-earth.kml+xml',
        as_attachment=True,
        download_name=f'survey_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.kml'
    )

@app.route('/api/export/dxf')
def export_dxf():
    """Export points and polygons to DXF format"""
    points = ReferencePoint.query.all()
    polygons = SurveyPolygon.query.all()
    
    # Create new DXF document
    doc = ezdxf.new('R2010')  # Use AutoCAD 2010 version
    msp = doc.modelspace()  # Get the modelspace
    
    # Add points as point entities
    for point in points:
        # Add point entity
        msp.add_point((point.longitude, point.latitude, point.elevation or 0))
        
        # Add text label for the point
        msp.add_text(
            point.name,
            dxfattribs={
                'insert': (point.longitude, point.latitude + 0.0001, point.elevation or 0),
                'height': 0.0005,
                'style': 'Standard'
            }
        )
    
    # Add polygons as polylines/lwpolylines
    for polygon in polygons:
        coords = json.loads(polygon.coordinates)
        
        # Convert coordinates to proper format (lon, lat, elevation)
        dxf_coords = []
        for coord in coords:
            dxf_coords.append((coord[1], coord[0], 0))  # Convert lat,lon to lon,lat
        
        # Close the polygon by adding the first point at the end
        if len(dxf_coords) > 0 and dxf_coords[0] != dxf_coords[-1]:
            dxf_coords.append(dxf_coords[0])
        
        # Add as polyline
        polyline = msp.add_lwpolyline(
            dxf_coords,
            dxfattribs={'layer': 'SURVEY_POLYGONS', 'color': 1}  # Red color
        )
        
        # Add polygon label at centroid
        if len(coords) >= 3:
            # Calculate centroid
            centroid_lat = sum(coord[0] for coord in coords) / len(coords)
            centroid_lon = sum(coord[1] for coord in coords) / len(coords)
            
            # Add text at centroid
            msp.add_text(
                f"{polygon.name}\nArea: {polygon.area_sqm:.2f} m²",
                dxfattribs={
                    'insert': (centroid_lon, centroid_lat, 0),
                    'height': 0.001,
                    'style': 'Standard',
                    'layer': 'SURVEY_LABELS'
                }
            )
    
    # Create layers
    doc.layers.new(name='SURVEY_POINTS', dxfattribs={'color': 3})  # Green
    doc.layers.new(name='SURVEY_POLYGONS', dxfattribs={'color': 1})  # Red
    doc.layers.new(name='SURVEY_LABELS', dxfattribs={'color': 7})  # White/Black
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.dxf')
    doc.saveas(temp_file.name)
    
    return send_file(
        temp_file.name,
        mimetype='application/dxf',
        as_attachment=True,
        download_name=f'survey_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.dxf'
    )

@app.route('/api/import/csv', methods=['POST'])
def import_csv():
    """Import points from CSV file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read CSV
        csv_data = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        imported_points = 0
        imported_polygons = 0
        
        for row in csv_reader:
            if row.get('Type') == 'Point':
                point = ReferencePoint(
                    name=row['Name'],
                    description=row.get('Description', ''),
                    latitude=float(row['Latitude']),
                    longitude=float(row['Longitude']),
                    elevation=float(row['Elevation']) if row.get('Elevation') else None,
                    point_type=row.get('Point_Type', 'waypoint')
                )
                db.session.add(point)
                imported_points += 1
            
            elif row.get('Type') == 'Polygon':
                # Parse coordinates from string format
                coord_str = row['Latitude']  # Coordinates stored in Latitude field for polygons
                coords = []
                for coord_pair in coord_str.split('; '):
                    lat, lon = map(float, coord_pair.split(','))
                    coords.append([lat, lon])
                
                area_sqm, perimeter_m = calculate_polygon_metrics(coords)
                
                polygon = SurveyPolygon(
                    name=row['Name'],
                    description=row.get('Description', ''),
                    coordinates=json.dumps(coords),
                    area_sqm=area_sqm,
                    perimeter_m=perimeter_m,
                    polygon_type=row.get('Point_Type', 'survey_area')
                )
                db.session.add(polygon)
                imported_polygons += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'imported_points': imported_points,
            'imported_polygons': imported_polygons
        })
    
    except Exception as e:
        return jsonify({'error': f'Import failed: {str(e)}'}), 400

@app.route('/api/import/geojson', methods=['POST'])
def import_geojson():
    """Import data from GeoJSON file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        geojson_data = json.loads(file.read().decode('utf-8'))
        
        imported_points = 0
        imported_polygons = 0
        
        for feature in geojson_data.get('features', []):
            geometry = feature['geometry']
            properties = feature.get('properties', {})
            
            if geometry['type'] == 'Point':
                lon, lat = geometry['coordinates']
                point = ReferencePoint(
                    name=properties.get('name', 'Imported Point'),
                    description=properties.get('description', ''),
                    latitude=lat,
                    longitude=lon,
                    elevation=properties.get('elevation'),
                    point_type=properties.get('point_type', 'waypoint')
                )
                db.session.add(point)
                imported_points += 1
            
            elif geometry['type'] == 'Polygon':
                # Convert from [lon, lat] to [lat, lon] format
                coords = [[coord[1], coord[0]] for coord in geometry['coordinates'][0]]
                
                area_sqm, perimeter_m = calculate_polygon_metrics(coords)
                
                polygon = SurveyPolygon(
                    name=properties.get('name', 'Imported Polygon'),
                    description=properties.get('description', ''),
                    coordinates=json.dumps(coords),
                    area_sqm=area_sqm,
                    perimeter_m=perimeter_m,
                    polygon_type=properties.get('polygon_type', 'survey_area')
                )
                db.session.add(polygon)
                imported_polygons += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'imported_points': imported_points,
            'imported_polygons': imported_polygons
        })
    
    except Exception as e:
        return jsonify({'error': f'Import failed: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True)