# CLAUDE.md — Guía para Vibe Coding

Catalog Studio es una herramienta visual standalone para gestionar catálogos de productos con imágenes. Proyecto separado de gs-ecom.

---

## Stack

| Capa | Tecnología |
|---|---|
| UI | HTML + Vanilla JS (single file `index.html`) |
| Backend API | Python + http.server (servidor local) |
| Descarga imágenes | Node.js + sharp + fetch |
| Persistencia | Archivos JSON en carpeta `data/` |
| Imágenes | WebP, 800x800px, 80% quality |

---

## Comandos

```bash
# Lanzar servidor
python3 server.py                    # Puerto default 3456
python3 server.py 8080               # Puerto custom

# Verificar sintaxis
node --check download-images.js
python3 -m py_compile server.py

# Dependencias Node (para download-images.js)
npm install sharp
```

---

## Estructura de archivos

```
catalog-studio/
├── index.html              # App completa (HTML + JS vanilla)
├── download-images.js      # Script Node para descargar imágenes
├── server.py               # Servidor Python (API endpoints)
├── .env                    # API keys (NO commitear)
├── .env.example           # Template de variables
├── data/                  # Archivos JSON de trabajo
│   └── proyectos.json
├── exports/                # Catálogos exportados (generado)
└── docs/                  # Documentación
    ├── USAGE.md
    ├── API.md
    └── IMPORT_EXPORT.md
```

---

## Variables de entorno (.env)

```
PEXELS_API_KEY=       # pexels.com/api (200 imágenes/mes)
UNSPLASH_ACCESS_KEY=  # unsplash.com/developers (50 req/hora)
SERPER_API_KEY=       # serper.dev (2500 búsquedas/mes)
```

---

## Flujo de datos

```
1. ABRIR catalog.json → State.catalog (en memoria)
          ↓
2. SELECCIONAR productos → State.selectedForWork (Set)
          ↓
3. DESCARGAR → download-images.js → _candidates/NN-slug/
          ↓
4. SELECCIONAR imagen → State.productState[id].selectedIdx
          ↓
5. EXPORTAR → exports/<nombre>/catalog.json + images/
```

---

## Estado de la aplicación (State)

```javascript
const STATE = {
  catalog: null,           // { giros: [], products: [] }
  imagesBasePath: '',       // Ruta a carpeta de imágenes
  
  workingProducts: [],      // Productos seleccionados para trabajar
  selectedForWork: new Set(), // IDs de productos marcados
  
  currentStep: 'welcome',  // welcome | select | work
  currentPage: 0,
  pageSize: 6,             // Productos por página en vista trabajo
  
  filter: 'all',           // all | no-image | has-image
  search: '',
  
  productState: {},         // { productId: { candidates: [], selectedIdx, downloading } }
  
  isDownloading: false,
  downloadQueue: [],
};
```

---

## API Endpoints (server.py)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/status` | GET | Verifica Node + Sharp |
| `/api/download` | POST | Descarga candidatas para 1 producto |
| `/api/export` | POST | Genera export folder |

---

## Formato de catálogo JSON

```json
{
  "giros": [{ "slug": "frutas-verduras", "name": "Frutas y Verduras" }],
  "products": [{
    "id": "p-1",
    "num": 1,
    "name": "Aguacate",
    "category": "frutas",
    "price": 45,
    "unit_key": "kg",
    "image": "/images/catalogs/aguacate.webp",
    "giros": ["frutas-verduras"]
  }]
}
```

---

## naming de imágenes

```javascript
// "Chile güero" → "chile-guero.webp"
function slugify(name) {
  return name.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, '')
    .trim().replace(/\s+/g, '-');
}
```

### Estructura de candidates
```
_candidates/
└── 01-chile-guero/
    ├── 01.webp
    ├── 02.webp
    └── ... hasta 18.webp
```

---

## Patrones clave

### Agregar un nuevo paso en el flow
1. Agregar a `STATE.currentStep` el nuevo step name
2. Crear función `render<StepName>()` que retorna HTML
3. Agregar case en el `render()` switch
4. Agregar navegación en `attachEventListeners()`

### Agregar endpoint en server.py
```python
def do_POST(self):
    parsed = urlparse(self.path)
    if parsed.path == "/api/nuevo":
        self.handle_nuevo()
    # ... otros endpoints

def handle_nuevo(self):
    # procesar request
    self.send_json({ "success": True, ... })
```

### Agregar filtro en vista selección
1. Agregar opción en el `<select>` con `onchange="onFilterChange(this.value)"`
2. Agregar case en `getFilteredProducts()`
3. Actualizar contadores en `renderSelectStep()`

---

## gs-ecom (proyecto relacionado)

Catalog Studio genera catálogos para gs-ecom:

| Catalog Studio | gs-ecom |
|----------------|---------|
| `exports/<giro>/catalog.json` | `backend/data/catalogs/<giro>.json` |
| `exports/<giro>/images/*.webp` | `frontend/public/images/catalogs/*.webp` |

---

## Reglas de vibe coding

- **UI primero**: antes de agregar lógica, asegurar que el HTML/CSS funcione visualmente
- **State es la fuente de verdad**: todo se deriva de `STATE`, no de DOM queries
- **Separación concerns**: `render()` solo renderiza, handlers solo actualizan state
- **No duplicar lógica**: reuse `slugify()`, `getProductState()`, `getExistingImage()` etc.

---

## Debugging

### Imágenes no cargan
1. Verificar que `imagesBasePath` sea correcto (debe terminar en `/`)
2. Verificar que las imágenes existan en esa ruta
3. Revisar consola del navegador por errores CORS

### Descarga no funciona
1. Verificar que `.env` tenga al menos una API key
2. Ejecutar `curl http://localhost:3456/api/status` para ver estado
3. Revisar output de `download-images.js` en terminal

### Server no inicia
1. Verificar que Python 3.8+ esté instalado: `python3 --version`
2. Verificar que el puerto no esté en uso: `lsof -i :3456`
