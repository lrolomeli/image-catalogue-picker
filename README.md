# Catalog Studio

Herramienta visual para crear y editar catálogos de productos con imágenes.

Permite cargar catálogos existentes, descargar imágenes de múltiples fuentes (Pexels, Unsplash, Serper), seleccionar las mejores opciones visualmente, y exportar el resultado listo para usar en gs-ecom.

## Requisitos

- **Node.js** 18+ (para ejecutar el script de descarga de imágenes)
- **Python** 3.8+ (para el servidor local)
- **API Keys** (para búsqueda de imágenes)

## Instalación

```bash
# 1. Navegar al directorio del proyecto
cd catalog-studio

# 2. Copiar el archivo de variables de entorno
cp .env.example .env

# 3. Editar .env y agregar las API keys
nano .env
```

## API Keys requeridas

Obtén tus claves en los siguientes servicios:

| Servicio | Para qué | Cómo obtener |
|----------|----------|--------------|
| `PEXELS_API_KEY` | Imágenes de stock (fotos profesionales) | [pexels.com/api](https://www.pexels.com/api/) |
| `UNSPLASH_ACCESS_KEY` | Imágenes de stock (alta calidad) | [unsplash.com/developers](https://unsplash.com/developers) |
| `SERPER_API_KEY` | Búsqueda de imágenes vía Google | [serper.dev](https://serper.dev) |

**Nota:** Las tres claves son opcionales pero se recomienda tener al menos una para poder descargar imágenes.

## Uso

```bash
# 1. Lanzar el servidor
python3 server.py

# 2. Abrir en el navegador
# http://localhost:3456
```

## Estructura del proyecto

```
catalog-studio/
├── index.html              # Aplicación web (abre en navegador)
├── download-images.js       # Script Node para descargar imágenes
├── server.py                # Servidor API local
├── .env                     # API keys (crear desde .env.example)
├── .env.example            # Template de variables de entorno
├── data/                   # Datos temporales de trabajo
│   └── proyectos.json
├── docs/                   # Documentación
│   ├── USAGE.md
│   ├── API.md
│   └── IMPORT_EXPORT.md
└── exports/                # Catálogos exportados (generado al exportar)
```

## Flujo de trabajo básico

1. **Abrir** un catálogo existente (JSON) o crear uno nuevo
2. **Seleccionar** los productos con los que quieres trabajar
3. **Descargar** imágenes para esos productos
4. **Seleccionar** la mejor imagen para cada producto
5. **Exportar** el resultado

Para instrucciones detalladas, ver [docs/USAGE.md](docs/USAGE.md).

## Integración con gs-ecom

Catalog Studio genera catálogos compatibles con gs-ecom. Para importar:

1. Exporta desde Catalog Studio
2. Copia `catalog.json` a `gs-ecom/backend/data/catalogs/`
3. Copia las imágenes a `gs-ecom/frontend/public/images/catalogs/`

Ver [docs/IMPORT_EXPORT.md](docs/IMPORT_EXPORT.md) para más detalles.
