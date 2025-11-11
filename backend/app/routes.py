from fastapi import APIRouter, HTTPException
from .m3u_parser import fetch_m3u, parse_m3u_text
from .xmltv_parser import fetch_xmltv, parse_xmltv_text
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Cargar URLs desde variables de entorno o config
M3U_URL = os.getenv('M3U_URL', 'http://192.168.1.198:34400/m3u/xteve.m3u')
XMLTV_URL = os.getenv('XMLTV_URL', 'http://192.168.1.198:34400/xmltv/xteve.xml')

_cached = {'channels': None, 'epg': None}

@router.get('/channels')
async def get_channels():
    """Obtiene la lista de canales desde el M3U"""
    try:
        if _cached['channels'] is None:
            text = await fetch_m3u(M3U_URL)
            _cached['channels'] = await parse_m3u_text(text)
            logger.info(f"✅ Cargados {len(_cached['channels'])} canales")
        return _cached['channels']
    except Exception as e:
        logger.error(f"❌ Error obteniendo canales: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo canales: {str(e)}")

@router.get('/epg')
async def get_epg():
    """Obtiene la guía electrónica de programación (EPG)"""
    try:
        if _cached['epg'] is None:
            text = await fetch_xmltv(XMLTV_URL)
            _cached['epg'] = await parse_xmltv_text(text)
        return _cached['epg']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo EPG: {str(e)}")

@router.post('/refresh')
async def refresh_all():
    """Refresca manualmente los datos de canales y EPG"""
    try:
        text = await fetch_m3u(M3U_URL)
        _cached['channels'] = await parse_m3u_text(text)
        text2 = await fetch_xmltv(XMLTV_URL)
        _cached['epg'] = await parse_xmltv_text(text2)
        return {'ok': True, 'message': 'Datos actualizados correctamente'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refrescando datos: {str(e)}")

@router.get('/health')
async def health_check():
    """Endpoint de salud para verificar el estado del servicio"""
    return {'status': 'healthy', 'cached': {
        'channels': _cached['channels'] is not None,
        'epg': _cached['epg'] is not None
    }}