# 2D Topography Surveying Application

A professional web-based topography surveying application built with Python Flask, featuring interactive maps, reference point management, and geometric calculations.

## Features

### 🗺️ **Interactive Map Visualization**
- Folium-powered maps with multiple tile layers (OpenStreetMap, Terrain, CartoDB)
- **Polygon Drawing**: Draw polygons directly on the map using interactive tools
- **Real-time Calculations**: Automatic area and perimeter calculations for drawn polygons
- Built-in measurement and drawing tools

### 📍 **Advanced Point & Polygon Management**
- Add, edit, delete reference points with labels, descriptions, and elevations
- **Polygon Support**: Create and manage survey areas, property boundaries, etc.
- Point types: waypoints, benchmarks, survey points, control points
- **GPS Coordinate Display**: Show coordinates for all polygon vertices
- **UTM Conversion**: Automatic conversion between lat/lon and UTM coordinates

### 📐 **Professional Survey Calculations**
- Distance calculations between any two points using geodesic formulas
- **Accurate Area Calculations**: UTM-based area calculations for precise measurements
- Perimeter calculations for polygons
- Elevation difference calculations

### 📊 **Multi-format Data Import/Export**
- **CSV Export/Import**: Standard spreadsheet format for data exchange
- **GeoJSON Support**: Industry-standard geospatial data format
- **KML Export**: Google Earth compatible format with rich descriptions
- Batch import of points and polygons from external sources

### 📋 **Coordinate Grid & Navigation**
- **Coordinate Grid Display**: Toggle lat/lon coordinate grid overlay
- **UTM Coordinates**: Automatic UTM zone detection and conversion
- Multiple map layer options with layer control
- Responsive design that works on desktop and mobile

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Map Visualization**: Folium (Python wrapper for Leaflet.js) with Draw plugin
- **Geometric Calculations**: Shapely, GeoPandas, and PyProj for precise calculations
- **Frontend**: Bootstrap 5, JavaScript, Bootstrap Icons
- **Data Processing**: NumPy, Pandas for data manipulation
- **Geospatial Formats**: 
  - **GeoJSON**: Standard geospatial data interchange
  - **KML**: Google Earth integration via SimpleKML
  - **CSV**: Spreadsheet compatibility
- **Coordinate Systems**: UTM conversion with PyProj

## Installation

1. **Clone or download the project**:
   ```bash
   cd /home/babybear/project/MapTest
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### 🎯 **Drawing Polygons on the Map**

1. **Navigate to Map View**: Click "View Map" from the home page
2. **Use Drawing Tools**: Located on the left side of the map
   - **Polygon Tool**: Draw custom survey areas
   - **Rectangle Tool**: Quick rectangular areas
   - **Line Tool**: Measure distances
   - **Marker Tool**: Add individual points
3. **Automatic Calculations**: Area and perimeter are calculated instantly
4. **Save Polygons**: Name and save drawn polygons for future reference

### 📍 **Managing Reference Points**

1. **Add Points Manually**:
   - Click "Add Reference Point" button
   - Enter coordinates, elevation, and description
   - Choose point type (waypoint, benchmark, control point, etc.)

2. **View Coordinates**:
   - **GPS Coordinates**: Displayed for every point and polygon vertex
   - **UTM Conversion**: Automatic conversion to UTM coordinates
   - Click on map markers to see detailed coordinate information

### 📊 **Import/Export Data**

1. **Export Data**:
   - **CSV Format**: `/api/export/csv` - Spreadsheet compatible
   - **GeoJSON Format**: `/api/export/geojson` - Standard geospatial format
   - **KML Format**: `/api/export/kml` - Google Earth compatible

2. **Import Data**:
   - Use "Import Data" button on Map view
   - Support for CSV and GeoJSON formats
   - Batch import of points and polygons

### 📐 **Professional Calculations**

1. **Distance Calculator**: Select two points to calculate geodesic distance
2. **Area Calculator**: Select multiple points to calculate enclosed area
3. **Polygon Analysis**: Automatic area/perimeter for all drawn polygons
4. **UTM Precision**: Accurate measurements using UTM projections

### 🗺️ **Coordinate Grid & Navigation**

- **Toggle Coordinate Grid**: Display lat/lon grid overlay
- **Multiple Map Layers**: OpenStreetMap, Terrain, CartoDB Positron
- **Layer Control**: Switch between different base maps
- **UTM Display**: Automatic UTM zone detection and display

## API Endpoints

### Points Management
- `GET /api/points` - List all reference points
- `POST /api/points` - Add a new reference point
- `PUT /api/points/<id>` - Update an existing point
- `DELETE /api/points/<id>` - Delete a reference point

### Polygon Management
- `GET /api/polygons` - List all survey polygons
- `POST /api/polygons` - Add a new polygon with automatic area/perimeter calculation
- `PUT /api/polygons/<id>` - Update an existing polygon
- `DELETE /api/polygons/<id>` - Delete a polygon

### Calculations
- `GET /api/calculate/distance?point1_id=X&point2_id=Y` - Calculate distance between two points
- `GET /api/calculate/area?point_ids=X&point_ids=Y&point_ids=Z` - Calculate area of polygon

### Import/Export
- `GET /api/export/csv` - Export all data to CSV format
- `GET /api/export/geojson` - Export all data to GeoJSON format
- `GET /api/export/kml` - Export all data to KML format
- `POST /api/import/csv` - Import data from CSV file
- `POST /api/import/geojson` - Import data from GeoJSON file

## Data Formats

### Reference Points
```json
{
  "id": 1,
  "name": "Survey Point A",
  "description": "Primary control point for site survey",
  "latitude": 40.712800,
  "longitude": -74.006000,
  "elevation": 15.5,
  "point_type": "control_point"
}
```

### Survey Polygons
```json
{
  "id": 1,
  "name": "Property Boundary",
  "description": "Main property boundary survey",
  "coordinates": [[40.7128, -74.0060], [40.7130, -74.0058], [40.7132, -74.0062]],
  "area_sqm": 1250.75,
  "perimeter_m": 145.30,
  "polygon_type": "property_boundary",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Point Types
- `waypoint`: General waypoint or location marker
- `benchmark`: Permanent survey benchmark
- `survey_point`: Temporary survey point
- `control_point`: Primary control point for surveying

### Polygon Types
- `survey_area`: General survey area
- `property_boundary`: Property boundary lines
- `restricted_zone`: Restricted or protected areas
- `construction_zone`: Construction or development areas

## File Structure

```
MapTest/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page with tools
│   └── map.html          # Map visualization page
├── topography.db         # SQLite database (created automatically)
└── README.md            # This file
```

## Technical Notes

### Coordinate System
- Uses WGS84 coordinate system (latitude/longitude)
- Distance calculations are approximate using simple geometric formulas
- For precision surveying, consider implementing proper geodesic calculations

### Database
- SQLite database is created automatically on first run
- Database file: `topography.db`
- Tables: `reference_point`

### Performance
- Suitable for projects with hundreds to thousands of points
- For larger datasets, consider upgrading to PostgreSQL with PostGIS

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure all dependencies are installed via `pip install -r requirements.txt`

2. **Database Error**: Delete `topography.db` file and restart the application to recreate

3. **Map Not Loading**: Check internet connection for map tiles

4. **Port Already in Use**: Change the port in `app.py`:
   ```python
   app.run(debug=True, port=5001)
   ```

### Development Mode

The application runs in debug mode by default. For production deployment:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Configure proper database connection for production use

## Contributing

This is a complete surveying application that can be extended with:

- GPS integration for real-time point collection
- Advanced geodesic calculations
- Export to CAD formats (DXF, DWG)
- Integration with surveying instruments
- Multi-user support with authentication
- Project management features

## License

This project is provided as-is for educational and professional use.