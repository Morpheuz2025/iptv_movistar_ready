import re
from typing import List, Dict
import httpx
import logging

logger = logging.getLogger(__name__)

# Regex mejorados para parsing M3U
EXTINF_RE = re.compile(r'#EXTINF:(-?\d+)\s*(.*?),\s*(.*?)$')
ATTR_RE = re.compile(r'(\w+(?:-\w+)?)=["\'](.*?)["\']')

async def fetch_m3u(url: str, timeout: int = 30) -> str:
    """
    Descarga el archivo M3U desde la URL especificada.
    
    Args:
        url: URL del archivo M3U
        timeout: Tiempo máximo de espera en segundos
        
    Returns:
        Contenido del archivo M3U como string
        
    Raises:
        httpx.HTTPError: Si hay un error en la descarga
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info(f"Descargando M3U desde: {url}")
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
            logger.info(f"M3U descargado exitosamente ({len(r.text)} bytes)")
            return r.text
    except httpx.HTTPError as e:
        logger.error(f"Error descargando M3U: {e}")
        raise

async def parse_m3u_text(text: str) -> List[Dict]:
    """
    Parsea el contenido de un archivo M3U y extrae los canales.
    
    Args:
        text: Contenido del archivo M3U
        
    Returns:
        Lista de diccionarios con información de cada canal
    """
    lines = text.splitlines()
    channels = []
    i = 0
    
    logger.info(f"Parseando M3U con {len(lines)} líneas")
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF'):
            # Parsear línea EXTINF
            m = EXTINF_RE.match(line)
            if not m:
                logger.warning(f"Línea EXTINF mal formada: {line}")
                i += 1
                continue
            
            duration = m.group(1)
            attrs_raw = m.group(2)
            title = m.group(3).strip()
            
            # Extraer atributos
            attrs = dict(ATTR_RE.findall(attrs_raw))
            
            # Obtener URL del canal (siguiente línea)
            url = ''
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('#'):
                    url = next_line
            
            if not url:
                logger.warning(f"Canal sin URL: {title}")
                i += 1
                continue
            
            # Crear objeto de canal
            channel = {
                'title': title or 'Sin título',
                'tvg_id': attrs.get('tvg-id') or attrs.get('tvg_id') or title,
                'tvg_logo': attrs.get('tvg-logo') or attrs.get('tvg_logo') or '',
                'group': attrs.get('group-title') or attrs.get('group') or 'Sin categoría',
                'url': url,
                'tvg_name': attrs.get('tvg-name') or attrs.get('tvg_name') or title,
                'duration': duration
            }
            
            channels.append(channel)
            i += 2  # Saltar línea EXTINF y URL
        else:
            i += 1
    
    logger.info(f"Parseados {len(channels)} canales")
    
    # Ordenar por grupo y luego por título
    channels.sort(key=lambda c: (c['group'].lower(), c['title'].lower()))
    
    return channels