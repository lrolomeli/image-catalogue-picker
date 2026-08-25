# Formato de Importación y Exportación

## Catálogo JSON

El formato de catálogo es compatible con gs-ecom. Un catálogo consiste en:

- Un array de **giros** (categorías de negocio)
- Un array de **productos**

### Estructura completa

```json
{
  "giros": [
    {
      "slug": "frutas-verduras",
      "name": "Frutas y Verduras"
    },
    {
      "slug": "abarrotes",
      "name": "Abarrotes"
    }
  ],
  "products": [
    {
      "id": "p-1",
      "num": 1,
      "name": "Aguacate",
      "category": "frutas",
      "price": 45,
      "unit_key": "kg",
      "image": "/images/catalogs/aguacate.webp",
      "giros": ["frutas-verduras"]
    }
  ]
}
```

### Campos del catálogo

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `giros` | array | Lista de giros/categorías de negocio |
| `products` | array | Lista de productos |

### Campos de un giro

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `slug` | string | Identificador único (URL-friendly) |
| `name` | string | Nombre legible del giro |

### Campos de un producto

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único (opcional, se genera si no existe) |
| `num` | integer | Número de orden (para naming de imágenes) |
| `name` | string | Nombre del producto |
| `category` | string | Categoría del producto (opcional) |
| `price` | number | Precio (opcional) |
| `unit_key` | string | Unidad de venta: `"pieces"` o `"kg"` (opcional) |
| `image` | string | Ruta a la imagen seleccionada (opcional, `null` si no hay) |
| `giros` | array | Giros a los que pertenece el producto |

## Imágenes

### Ubicación de imágenes

```
carpeta-imagenes/
├── aguacate.webp              # Imagen directa (original)
├── ajo.webp
├── _candidates/               # Imágenes candidatas descargadas
│   ├── 01-aguacate/
│   │   ├── 01.webp
│   │   ├── 02.webp
│   │   └── ...
│   └── 02-ajo/
│       ├── 01.webp
│       └── ...
```

### naming de archivos

El nombre del archivo se genera a partir del nombre del producto:

```
"Aguacate hass" → aguacate-hass.webp
"Chile güero"   → chile-guero.webp
"Elote"         → elote.webp
```

**Reglas de conversión:**
1. Convertir a minúsculas
2. Eliminar acentos (á → a, é → e, etc.)
3. Eliminar caracteres especiales
4. Reemplazar espacios por guiones
5. Agregar extensión `.webp`

## Exportación a gs-ecom

### Pasos

1. Exporta desde Catalog Studio a una carpeta temporal
2. Copia `catalog.json` a:
   ```
   gs-ecom/backend/data/catalogs/<nombre>.json
   ```
3. Copia las imágenes a:
   ```
   gs-ecom/frontend/public/images/catalogs/
   ```

### Ejemplo práctico

```bash
# 1. Exportar desde Catalog Studio genera:
exports/mi-catalogo/
├── catalog.json
└── images/
    ├── aguacate.webp
    └── ajo.webp

# 2. Copiar a gs-ecom:
cp exports/mi-catalogo/catalog.json gs-ecom/backend/data/catalogs/mi-catalogo.json
cp exports/mi-catalogo/images/* gs-ecom/frontend/public/images/catalogs/
```

## Combinar catálogos

Para combinar múltiples giros en un solo catálogo:

1. Exporta cada giro por separado desde Catalog Studio
2. Une los arrays `products` manualmente o con un script

```javascript
// Ejemplo de combinación
const catalogo1 = require('./giros/frutas.json');
const catalogo2 = require('./giros/abarrotes.json');

const combinado = {
  giros: [...catalogo1.giros, ...catalogo2.giros],
  products: [...catalogo1.products, ...catalogo2.products]
};
```

## Productos sin imagen

Un producto puede tener `image: null` o no tener el campo:

```json
{
  "name": "Producto nuevo",
  "category": "Sin Categoría",
  "image": null
}
```

Estos productos aparecerán como "Sin imagen" en Catalog Studio y podrás descargar candidatas para ellos.
