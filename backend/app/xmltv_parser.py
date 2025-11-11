from lxml import etree
from typing import Dict, List
import httpx
import logging

logger = logging.getLogger(__name__)

async def fetch_xmltv(url: str, timeout: int = 60) -> str:
    """
    Descarga el archivo XMLTV desde la URL especificada.
    
    Args:
        url: URL del archivo XMLTV
        timeout: Tiempo máximo de espera en segundos
        
    Returns:
        Contenido del archivo XMLTV como string
        
    Raises:
        httpx.HTTPError: Si hay un error en la descarga
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info(f"Descargando XMLTV desde: {url}")
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
            logger.info(f"XMLTV descargado exitosamente ({len(r.text)} bytes)")
            return r.text
    except httpx.HTTPError as e:
        logger.error(f"Error descargando XMLTV: {e}")
        raise

async def parse_xmltv_text(text: str) -> Dict[str, List[Dict]]:
    """
    Parsea el contenido de un archivo XMLTV y extrae la guía EPG.
    
    Args:
        text: Contenido del archivo XMLTV
        
    Returns:
        Diccionario con canal_id como clave y lista de programas como valor
    """
    try:
        root = etree.fromstring(text.encode('utf-8'))
    except etree.XMLSyntaxError as e:
        logger.error(f"Error parseando XML: {e}")
        return {}
    
    programmes_by_channel = {}
    programme_count = 0
    
    # Parsear todos los programas
    for prog in root.findall('programme'):
        ch = prog.get('channel')
        if not ch:
            continue
        
        # Extraer información del programa
        title_el = prog.find('title')
        desc_el = prog.find('desc')
        category_el = prog.find('category')
        
        start = prog.get('start')
        stop = prog.get('stop')
        title = title_el.text if title_el is not None and title_el.text else 'Sin título'
        desc = desc_el.text if desc_el is not None and desc_el.text else ''
        category = category_el.text if category_el is not None and category_el.text else ''
        
        prog_obj = {
            'title': title,
            'start': start,
            'stop': stop,
            'desc': desc,
            'category': category
        }
        
        programmes_by_channel.setdefault(ch, []).append(prog_obj)
        programme_count += 1
    
    # Ordenar programas por hora de inicio
    for channel_id in programmes_by_channel:
        programmes_by_channel[channel_id].sort(
            key=lambda p: p['start'] if p['start'] else ''
        )
    
    logger.info(f"Parseados {programme_count} programas para {len(programmes_by_channel)} canales")
    
    return programmes_by_channel