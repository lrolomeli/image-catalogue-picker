# Guía de uso de Catalog Studio

## Pasos del flujo de trabajo

### 1. Pantalla de inicio

Al abrir la aplicación verás dos opciones:

- **Nuevo Catálogo**: Crear un catálogo desde cero con productos vacíos
- **Abrir Catálogo**: Cargar un JSON existente (ej: master-catalog.json de gs-ecom)

### 2. Cargar un catálogo existente

1. Haz clic en **"Abrir Catálogo"**
2. Selecciona el archivo `.json` del catálogo
3. Cuando se solicite, ingresa la ruta a la carpeta de imágenes

**Ejemplo de ruta:**
```
/home/usuario/gs-ecom/frontend/public/images/catalogs/
```

La aplicación detectará automáticamente:
- Productos **con imagen** (✓ tiene imagen)
- Productos **sin imagen** (○ sin imagen)

### 3. Seleccionar productos para trabajar

En la vista de selección you'll see a list of all products with their status:

| Elemento | Descripción |
|----------|-------------|
| Filtros | Todos / Con imagen / Sin imagen |
| Búsqueda | Filtrar por nombre de producto |
| Checkboxes | Seleccionar productos para trabajar |

**Selección múltiple:**
- Usa **"Seleccionar todos"** para marcar todos los visibles
- Usa **"Limpiar"** para deseleccionar
- Solo se trabaja con los productos que marques con check

Después de seleccionar, haz clic en **"Trabajar con N productos →"**

### 4. Vista de trabajo (descarga y selección)

La vista de trabajo muestra los productos seleccionados en cards:

**Elementos de la card:**
- Nombre y categoría del producto
- Thumbnails de imágenes disponibles
- Botones de acción

**Acciones por producto:**
- **Ver más**: Abre un modal con todas las candidatas en grid
- **Thumbnail click**: Expande la imagen para verla en detalle
- **Clic en imagen**: Selecciona esa imagen como la definitiva

### 5. Descargar imágenes

1. Haz clic en **"🔍 Descargar imágenes"**
2. Las imágenes se descargan en background
3. Los thumbnails aparecen conforme se descargan
4. Puedes seleccionar mientras descarga sigue en paralelo

**Nota:** Los productos que ya tienen imagen en el JSON original no necesitan descarga.

### 6. Navegación

- Usa **"← Anterior"** y **"Siguiente →"** para navegar entre páginas
- La paginación muestra **2-3 productos por página**

### 7. Modal de imagen expandida

Al hacer clic en un thumbnail:

- Imagen se muestra en tamaño grande
- Navega con **←** y **→** entre candidatas
- **"✓ Seleccionar esta"** marca la imagen como elegida
- **"Cerrar"** vuelve a la vista de trabajo

### 8. Exportar

1. Haz clic en **"📦 Exportar"**
2. Ingresa la ruta de la carpeta de imágenes destino
3. Se genera:
   - `exports/<nombre>/catalog.json`
   - `exports/<nombre>/images/` con las imágenes seleccionadas

## Operaciones adicionales

### Agregar productos manualmente

Aún no disponible en esta versión. Se recomienda agregar productos via JSON.

### Editar productos existentes

- Para cambiar una selección: clic en otra imagen del mismo producto
- Para limpiar selección: clic en **"✓ Seleccionada"** (cambia a disponible)

### Guardar progreso

Usa el botón **"💾 Guardar"** para descargar el JSON con el estado actual de selecciones.

## Solución de problemas

### "No hay imágenes"

- Verifica que las API keys estén configuradas en `.env`
- Comprueba tu conexión a internet
- Algunas fuentes pueden tener rate limits

### Imágenes no cargan

- Verifica que la ruta de imágenes sea correcta
- Asegúrate de que las imágenes existan en esa ubicación

### Descarga lenta

- Las API de imágenes tienen límites de velocidad
- El script incluye delays para evitar bloqueos
- Puedes pausar y continuar más tarde
