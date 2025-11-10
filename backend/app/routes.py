import backend.config as config
from fastapi import APIRouter, HTTPException
from .m3u_parser import fetch_m3u, parse_m3u_text
from .xmltv_parser import fetch_xmltv, parse_xmltv_text

router = APIRouter()

_cached = {'channels': None, 'epg': None}

@router.get('/channels')
async def get_channels():
    try:
        if _cached['channels'] is None:
            text = await fetch_m3u(config.M3U_URL)
            _cached['channels'] = await parse_m3u_text(text)
        return _cached['channels']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/epg')
async def get_epg():
    try:
        if _cached['epg'] is None:
            text = await fetch_xmltv(config.XMLTV_URL)
            _cached['epg'] = await parse_xmltv_text(text)
        return _cached['epg']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/refresh')
async def refresh_all():
    text = await fetch_m3u(config.M3U_URL)
    _cached['channels'] = await parse_m3u_text(text)
    text2 = await fetch_xmltv(config.XMLTV_URL)
    _cached['epg'] = await parse_xmltv_text(text2)
    return {'ok': True}
