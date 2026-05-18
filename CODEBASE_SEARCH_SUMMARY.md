# Smart Forest Watcher - Codebase Search Summary

## 1. PROJECT CREATION VIEWS & FORMS

### Main Project Creation Flow
**File:** [supervisor/views/project.py](supervisor/views/project.py#L48) (Lines 48-146)

**Function:** `add_project(request)`
- Handles both GET (display form) and POST (create/update project)
- Uses `ProjectForm` for form handling
- Creates or updates Project model based on name and city uniqueness
- **Key Logic:**
  - Checks if project with same name and city already exists
  - If exists: updates existing project
  - If new: creates new Project object
  - Sets initial map data from city latitude/longitude
  - Session management for UI state (`project_added`, `map_data`)

**Related Function:** `get_project_details(request, project_id)` (Lines 160-175)
- Returns project details as JSON
- Data includes: project_name, client_name, latitude, longitude

### Project Form Configuration
**File:** [supervisor/forms/projectForm.py](supervisor/forms/projectForm.py)

**Class:** `ProjectForm(forms.ModelForm)`
- **Fields:**
  - `name`: TextInput with placeholder "Project Name"
  - `city`: CustomModelChoiceField with formatted display
  - `descp`: Textarea with 2 rows
  - `client`: ModelChoiceField selecting from Client.objects.all()
  - `piece_joindre`: FileField for attachments
  - `date_debut`, `date_fin`: DateTime fields
- **Custom Field:** `CustomModelChoiceField` displays location as "gouvernorat, delegation, localite"

### Project Model
**File:** [supervisor/models/project.py](supervisor/models/project.py)

**Fields:**
- `name`: CharField(max_length=30)
- `descp`: TextField (nullable)
- `date_debut`, `date_fin`: DateTime fields
- `city`: ForeignKey → Localisation (nullable, blank)
- `piece_joindre`: FileField(upload_to='uploads/%Y/%m/%d/')
- `client`: ForeignKey → Client (nullable)
- `polygon_id`: BigAutoField (primary key for unique map regions)

**Properties:**
- `total_nodes`: Count of nodes across all parcelles in project
- `total_cameras`: Count of cameras related to project

---

## 2. LOCATION/PARCEL LIST POPULATION

### Parcel Fetching for Client (AJAX)
**File:** [client/views/fetch_parcelles.py](client/views/fetch_parcelles.py#L15)

**Function:** `fetch_parcelles_for_project(request)`
- **Access Control:** @login_required, @client_required
- **Input:** `project_id` via GET parameter
- **Returns:** JSON with parcelles, city data, and cameras
- **Data Structure:**
  ```python
  {
    'parcelles': [
      {
        'id': parcelle.id,
        'name': parcelle.name,
        'coordinates': list(parcelle.polygon.coords[0]),
        'nodes': [{id, name, latitude, longitude, ref, last_data}, ...]
      },
      ...
    ],
    'city': {
      'localite_libelle': project.city.localite_libelle,
      'latitude': project.city.latitude,
      'longitude': project.city.longitude
    },
    'cameras': [
      {
        'id': c.id,
        'name': c.name,
        'camera_id': c.camera_id,
        'latitude': float(c.latitude),
        'longitude': float(c.longitude),
        'has_alert': bool,
        'is_active': bool,
        'latest_alert_image': url,
        'latest_alert_time': timestamp
      },
      ...
    ]
  }
  ```

### Supervisor Parcel Creation/Management
**File:** [supervisor/views/project.py](supervisor/views/project.py#L183) (Lines 183-263)

**Function:** `parcelle_create(request)`
- **Method POST:** Creates or updates parcelle
  - Accepts coordinates as JSON from frontend map
  - Parses coordinates into Django GIS Polygon
  - **Validation:** Checks polygon doesn't already exist (using `equals_exact()`)
  - Saves Parcelle with ForeignKey to Project
  - Returns list of all parcelles for the project
  
- **Method GET:** Returns project data structure
  - Lists all projects with their parcelles
  - Includes coordinates for each parcelle
  - Returns parcelle_form and related forms

**Function:** `get_parcelles_for_project(request)` (Lines 265-276)
- **Input:** `project_id` via GET
- **Output:** JSON list of parcelles with coordinates

**Function:** `get_parcelles_with_nodes_for_project(request)` (Lines 330+)
- Returns parcelles with nested nodes data
- Used for detailed project/parcel visualization

### Parcel Model
**File:** [supervisor/models/parcelle.py](supervisor/models/parcelle.py)

**Fields:**
- `name`: CharField(max_length=30)
- `polygon`: PolygonField (geographic polygon, nullable)
- `project`: ForeignKey → Project (on_delete=CASCADE, nullable, related_name='parcelle')

**Related Objects:**
- One parcelle has many nodes (one-to-many via Node model)
- One parcelle has many cameras (one-to-many via Camera model)

### Parcel Form
**File:** [supervisor/forms/parcelleFom.py](supervisor/forms/parcelleFom.py)

**Class:** `ParcelleForm(forms.ModelForm)`
- **Fields:**
  - `name`: TextInput for polygon name
  - `project`: ModelChoiceField with dynamic choices
    - Displays: "Project Name (lat: X, lon: Y)"
    - Includes data attributes for latitude/longitude
- **Custom __init__:** Dynamically populates project choices with location data

---

## 3. GDAL USAGE & INITIALIZATION

### GDAL Environment Configuration
**File:** [project/settings.py](project/settings.py#L8) (Lines 8-18)

**Windows Configuration (os.name == "nt"):**
```python
VENV_BASE = os.environ.get("VIRTUAL_ENV", os.path.join(BASE_DIR, "venv"))
OSGEO_PATH = os.path.join(VENV_BASE, "Lib", "site-packages", "osgeo")
os.environ["PATH"] = OSGEO_PATH + ";" + os.environ["PATH"]
os.environ["PROJ_LIB"] = os.path.join(OSGEO_PATH, "data", "proj")
GDAL_LIBRARY_PATH = os.path.join(OSGEO_PATH, "gdal.dll")
```

**Linux Configuration:**
```python
GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH", "/usr/lib/x86_64-linux-gnu/libgdal.so.36")
```

### Docker GDAL Setup
**File:** [Dockerfile](Dockerfile#L10) (Lines 10-29)

**Environment Variables:**
```dockerfile
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so.36
```

**Installed Packages:**
- `gdal-bin`
- `libgdal-dev`

**Setup Command:**
```dockerfile
ln -sf /usr/lib/x86_64-linux-gnu/libgdal.so.36 /usr/lib/libgdal.so
```

### GDAL Usage in Django GIS
- **Models use GeoDjango:**
  - `PointField` for node/camera positions (lat/lon)
  - `PolygonField` for parcelle boundaries
- **Imports:** `from django.contrib.gis.db import models`
- **Point Creation:** `Point(latitude, longitude)` for node/camera placement
- **Polygon Creation:** `Polygon(coordinates)` for parcelle boundaries
- **Spatial Queries:** `.contains()` method to validate point-in-polygon

**File:** [supervisor/views/project.py](supervisor/views/project.py#L320)
```python
# Example: Validate node is inside parcelle
if parcelle.polygon.contains(point):
    # Node is valid
```

---

## 4. FORM CHOICES & QUERYSET POPULATION

### Client Selection in ProjectForm
**File:** [supervisor/forms/projectForm.py](supervisor/forms/projectForm.py#L24)
```python
client = forms.ModelChoiceField(
    queryset=Client.objects.all(),  # All clients available
    required=True,
    empty_label='None'
)
```

### City/Location Selection in ProjectForm
**File:** [supervisor/forms/projectForm.py](supervisor/forms/projectForm.py#L31-L40)
```python
city = CustomModelChoiceField(
    queryset=Localisation.objects.all(),  # All locations
    required=True,
    empty_label='Select Location',
    # Custom display: "gouvernorat, delegation, localite"
)
```

### Project Selection in ParcelleForm
**File:** [supervisor/forms/parcelleFom.py](supervisor/forms/parcelleFom.py#L25-L33)
```python
project = forms.ModelChoiceField(
    queryset=Project.objects.all(),
    required=True
)
```

**Custom __init__ Implementation:**
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['project'].widget.choices = [
        (project.polygon_id, 
         f"{project.name} (lat: {project.city.latitude}, lon: {project.city.longitude})",
         {'data-latitude': project.city.latitude, 'data-longitude': project.city.longitude})
        for project in Project.objects.all() if project.city
    ]
```

### Location Model
**File:** [supervisor/models/localisation.py](supervisor/models/localisation.py)

**Fields:**
- `gouvernorat_libelle`: CharField(max_length=255, nullable)
- `delegation_libelle`: CharField(max_length=255, nullable)
- `localite_libelle`: CharField(max_length=255)
- `latitude`: DecimalField(max_digits=9, decimal_places=6)
- `longitude`: DecimalField(max_digits=9, decimal_places=6)

**Constraints:**
- `unique_together = ['gouvernorat_libelle', 'delegation_libelle', 'localite_libelle']`
- Enforces geographic location uniqueness

---

## 5. CAMERA & NODE MANAGEMENT WITH LOCATIONS

### Camera Management Views
**File:** [camera_management/views.py](camera_management/views.py#L24)

**Function:** `add_camera(request)`
- POST: Creates camera at specific location on map
- Validates camera is inside parcelle using `.polygon.contains(point)`
- Saves Camera with ForeignKey to Parcelle and Project
- Returns updated camera list for UI

**Function:** `list_cameras_for_project(request)` (Lines 76+)
- AJAX endpoint returning all cameras for a project
- Includes alert status and detection information

### Camera Model
**File:** [camera_management/models.py](camera_management/models.py)

**Key Fields:**
- `parcelle`: ForeignKey → Parcelle (on_delete=CASCADE, related_name='cameras', nullable)
- `project`: ForeignKey → Project
- `position`: PointField for geographic location
- `latitude`, `longitude`: DecimalFields
- `location_description`: CharField for notes
- `is_active`: BooleanField for status

### Node Creation View
**File:** [supervisor/views/project.py](supervisor/views/project.py#L289) (Lines 289-328)

**Function:** `node_create(request)`
- Similar to camera creation
- Parses "POINT(lng lat)" coordinates from form
- Validates node is inside parcelle
- Creates Node with ForeignKey to Parcelle
- Returns updated nodes list

### Node Model
**File:** [supervisor/models/node.py](supervisor/models/node.py)

**Key Fields:**
- `name`: CharField(max_length=30)
- `position`: PointField (geographic position)
- `latitude`, `longitude`: DecimalFields
- `reference`: CharField(max_length=50)
- `parcelle`: ForeignKey → Parcelle (on_delete=CASCADE, related_name='nodes')
- `sensors`, `status`: CharField fields
- `RSSI`, `Battery_value`, `node_range`: BigIntegerFields
- `FWI`: FloatField (Fire Weather Index)
- `detection`: BigIntegerField (detection status)

---

## 6. TEMPLATE INTEGRATION & AJAX ENDPOINTS

### URL Endpoints
**File:** [client/urls.py](client/urls.py#L11)
```python
path('fetch_parcelles_for_project/', views.fetch_parcelles_for_project, 
     name='fetch_parcelles_for_project')
```

### Template Usage
**File:** [client/templates/website/node_list.html](client/templates/website/node_list.html#L292)
```html
<div id="mapContainer" 
     data-url="{% url 'fetch_parcelles_for_project' %}?project_id={{ project.polygon_id }}"
     style="height: 500px;">
</div>
```

---

## TECHNICAL STACK SUMMARY

**Geographic Data:**
- Django GIS (GeoDjango) with PostGIS for spatial queries
- Point objects for coordinates
- Polygon objects for parcel boundaries
- Spatial containment checks (.contains())

**Forms & Data Entry:**
- Django ModelForms for project/parcel/node creation
- AJAX endpoints for real-time data loading
- JSON responses for dynamic UI updates

**Location Hierarchy:**
```
Localisation (city)
  ↓
Project (has city reference)
  ↓
Parcelle (geographic polygon)
  ↓
Node (point location) + Camera (point location)
```

**GDAL Configuration:**
- Platform-specific setup (Windows OSGEO, Linux system libraries)
- Docker support with proper library linking
- Environment variables for proj data and library paths
