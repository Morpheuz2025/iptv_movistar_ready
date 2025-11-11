# 📺 IPTV Movistar+ Style

Aplicación web moderna para visualizar IPTV con diseño inspirado en Movistar+. Incluye reproductor de video HLS, guía EPG y búsqueda de canales.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-green)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen)

## ✨ Características

- 🎬 **Reproductor HLS** con soporte para múltiples formatos
- 📺 **Lista de canales** con logos y categorías
- 📅 **Guía EPG** (Electronic Program Guide) en tiempo real
- 🔍 **Búsqueda** de canales por nombre o categoría
- 🎨 **Diseño moderno** inspirado en Movistar+
- ⚡ **Rendimiento optimizado** con caché de datos
- 🐳 **Docker** para fácil despliegue
- ⌨️ **Navegación con teclado** (flechas arriba/abajo)
- 📱 **Responsive** para diferentes dispositivos

## 🚀 Instalación Rápida

### Requisitos Previos

- Docker y Docker Compose instalados
- Acceso a un servidor xTeVe o similar con M3U y XMLTV

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

```bash
git clone <tu-repo>
cd iptv-movistar
```

2. **Configurar URLs de xTeVe**

Editar `backend/config.py` o las variables de entorno en `docker-compose.yml`:

```python
M3U_URL = "http://TU_IP:34400/m3u/xteve.m3u"
XMLTV_URL = "http://TU_IP:34400/xmltv/xteve.xml"
```

3. **Construir y ejecutar**

```bash
docker compose up -d --build
```

4. **Acceder a la aplicación**

Abrir en el navegador: `http://localhost:8080`

## 📁 Estructura del Proyecto

```
iptv-movistar/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app principal
│   │   ├── routes.py          # Endpoints API
│   │   ├── m3u_parser.py      # Parser de archivos M3U
│   │   └── xmltv_parser.py    # Parser de archivos XMLTV
│   ├── static/
│   │   ├── index.html         # Frontend
│   │   ├── app.js             # Lógica JavaScript
│   │   └── styles.css         # Estilos Movistar+
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.py
├── docker-compose.yml
└── README.md
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Puedes configurar las siguientes variables en `docker-compose.yml`:

```yaml
environment:
  - M3U_URL=http://192.168.1.198:34400/m3u/xteve.m3u
  - XMLTV_URL=http://192.168.1.198:34400/xmltv/xteve.xml
  - TZ=America/Lima
  - LOG_LEVEL=info
```

### Cambiar Puerto

Modificar en `docker-compose.yml`:

```yaml
ports:
  - "TU_PUERTO:8080"
```

### Límites de Recursos

Ajustar según tu hardware en `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G
```

## 🎮 Uso de la Aplicación

### Navegación

- **Click en canal**: Reproduce el canal seleccionado
- **Búsqueda**: Filtra canales por nombre o categoría
- **Flechas ↑↓**: Navega entre canales (cuando hay uno seleccionado)
- **Botón refresh**: Actualiza datos de canales y EPG

### API Endpoints

La aplicación expone los siguientes endpoints:

- `GET /api/channels` - Lista de canales
- `GET /api/epg` - Guía EPG
- `POST /api/refresh` - Refrescar datos
- `GET /api/health` - Estado del servicio

Ejemplo:
```bash
curl http://localhost:8080/api/channels
```

## 🔍 Solución de Problemas

### Los canales no cargan

1. Verificar que xTeVe esté accesible:
   ```bash
   curl http://TU_IP:34400/m3u/xteve.m3u
   ```

2. Revisar logs del contenedor:
   ```bash
   docker logs iptv-movistar
   ```

3. Verificar URLs en `config.py` o variables de entorno

### Video no reproduce

- Asegúrate de que tu navegador soporte HLS
- Verifica que las URLs de streaming sean accesibles
- Algunos canales pueden requerir codecs específicos

### Performance lento

- Aumentar límites de recursos en docker-compose.yml
- Verificar velocidad de red con el servidor xTeVe
- Considerar usar caché de red local

## 🛠️ Desarrollo

### Ejecutar en modo desarrollo

```bash
# Instalar dependencias
pip install -r backend/requirements.txt

# Ejecutar servidor
cd backend
uvicorn app.main:app --reload --port 8080
```

### Modificar Frontend

Los archivos están en `backend/static/`:
- `index.html` - Estructura
- `app.js` - Lógica
- `styles.css` - Estilos

Después de modificar, reconstruir la imagen Docker.

## 📊 Mejoras Implementadas

### Backend
✅ Manejo robusto de errores  
✅ Logging detallado  
✅ Parser M3U mejorado con soporte para más atributos  
✅ Parser XMLTV con descripción y categoría  
✅ Endpoint de health check  
✅ Variables de entorno para configuración  

### Frontend
✅ Diseño moderno estilo Movistar+  
✅ Búsqueda en tiempo real  
✅ Indicador de programa actual en EPG  
✅ Animaciones suaves  
✅ Notificaciones de estado  
✅ Loading overlay  
✅ Navegación por teclado  
✅ Responsive design  

### Docker
✅ Multi-stage build optimizado  
✅ Usuario no-root para seguridad  
✅ Health checks  
✅ Límites de recursos  
✅ Volúmenes para persistencia  

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🙏 Créditos

- Diseño inspirado en Movistar+ España
- HLS.js para reproducción de video
- FastAPI para el backend
- xTeVe para agregación de canales

## 📧 Soporte

Si encuentras algún problema o tienes sugerencias, por favor abre un issue en GitHub.

---

**Nota**: Este proyecto es solo para uso personal y educativo. Asegúrate de tener los derechos necesarios para transmitir el contenido que utilizas.
