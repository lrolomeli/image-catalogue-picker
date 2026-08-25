# API del servidor Catalog Studio

El servidor (`server.py`) expone endpoints para manejar descargas y exportación de catálogos.

## Endpoints

### `GET /api/status`

Verifica el estado del servidor y sus dependencias.

**Response:**
```json
{
  "status": "ok",
  "node": true,
  "sharp": true,
  "python_version": "3.11.0",
  "base_dir": "/path/to/catalog-studio"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `status` | string | Siempre `"ok"` si el servidor responde |
| `node` | boolean | `true` si Node.js está disponible |
| `sharp` | boolean | `true` si la librería sharp está instalada |
| `python_version` | string | Versión de Python |

---

### `POST /api/download`

Descarga imágenes candidatas para un producto específico.

**Request:**
```json
{
  "productNum": 1,
  "productName": "Aguacate",
  "imagesBasePath": "/home/user/images/"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `productNum` | integer | Sí | Número de producto para naming |
| `productName` | string | Sí | Nombre del producto (se usa para búsqueda) |
| `imagesBasePath` | string | No | Ruta base de imágenes |

**Response:**
```json
{
  "success": true,
  "count": 12,
  "downloaded": 12
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `success` | boolean | `true` si la descarga terminó sin errores |
| `count` | integer | Total de candidatas disponibles |
| `downloaded` | integer | Número de imágenes descargadas en esta llamada |

**Estructura de archivos generados:**
```
<imagesBasePath>/
└── _candidates/
    └── 01-aguacate/
        ├── 01.webp
        ├── 02.webp
        └── ... hasta 18.webp
```

---

### `POST /api/export`

Exporta el catálogo y copia las imágenes seleccionadas.

**Request:**
```json
{
  "catalog": {
    "giros": [...],
    "products": [...]
  },
  "imagesBasePath": "/home/user/images/",
  "workingProducts": ["p-1", "p-2"]
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `catalog` | object | Sí | Objeto completo del catálogo |
| `imagesBasePath` | string | Sí | Ruta donde están las imágenes |
| `workingProducts` | array | No | IDs de productos trabajados |

**Response:**
```json
{
  "success": true,
  "exportPath": "/path/to/catalog-studio/exports/mi-catalogo"
}
```

**Estructura de archivos exportados:**
```
exports/<nombre>/
├── catalog.json          # JSON del catálogo actualizado
└── images/
    ├── aguacate.webp
    ├── ajo.webp
    └── ...
```

---

## Uso desde el navegador

La aplicación web (`index.html`) consume estos endpoints automáticamente. No necesitas llamarlos manualmente.

## Uso desde terminal

Puedes probar los endpoints con `curl`:

```bash
# Ver estado
curl http://localhost:3456/api/status

# Descargar imágenes (requiere JSON body)
curl -X POST http://localhost:3456/api/download \
  -H "Content-Type: application/json" \
  -d '{"productNum":1,"productName":"Aguacate","imagesBasePath":"/tmp/test/"}'

# Exportar
curl -X POST http://localhost:3456/api/export \
  -H "Content-Type: application/json" \
  -d '{"catalog":{"giros":[],"products":[]},"imagesBasePath":"/tmp/test/"}'
```

## Códigos de error

| Código | Significado |
|--------|-------------|
| 200 | OK (siempre para esta API) |
| 400 | Parámetros faltantes |
| 404 | Endpoint no encontrado |
| 500 | Error interno del servidor |

Los errores se indican en el campo `error` del response:
```json
{
  "success": false,
  "error": "Missing parameters"
}
```
