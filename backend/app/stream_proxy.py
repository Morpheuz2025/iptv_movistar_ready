import httpx
import logging
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import html

logger = logging.getLogger(__name__)

async def proxy_stream(stream_url: str, request: Request) -> StreamingResponse:
    """
    Proxy para el streaming de video que maneja:
    - Decodificación de URLs mal formateadas
    - Headers necesarios
    - Tokens de autenticación
    """
    
    # Decodificar entidades HTML que xTeVe puede haber mal codificado
    clean_url = html.unescape(stream_url)
    clean_url = clean_url.replace('¶llel', '&parallel')  # Fix específico para xTeVe
    
    logger.info("🔧 PROCESANDO STREAM")
    logger.info(f"   URL Limpia: {clean_url[:150]}...")
    if clean_url != stream_url:
        logger.info(f"   ✅ URL fue modificada durante la limpieza")
    
    # Headers para el streaming
    headers = {
        'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
        'Referer': request.headers.get('Referer', ''),
        'Origin': request.headers.get('Origin', ''),
        'Range': request.headers.get('Range', ''),
    }
    
    # Limpiar headers vacíos
    headers = {k: v for k, v in headers.items() if v}
    logger.info(f"📤 Headers enviados: {list(headers.keys())}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            logger.info(f"🌐 Conectando al servidor de streaming...")
            async with client.stream('GET', clean_url, headers=headers) as response:
                logger.info(f"📥 Respuesta recibida: HTTP {response.status_code}")
                logger.info(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                response.raise_for_status()
                
                # Obtener content-type del stream
                content_type = response.headers.get('content-type', 'application/vnd.apple.mpegurl')
                
                # Si es un playlist M3U8, podemos procesarlo
                if 'mpegurl' in content_type or 'm3u8' in content_type:
                    content = await response.aread()
                    return StreamingResponse(
                        iter([content]),
                        media_type=content_type,
                        headers={
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, OPTIONS',
                            'Access-Control-Allow-Headers': '*',
                        }
                    )
                
                # Para video streaming directo
                async def stream_generator() -> AsyncGenerator[bytes, None]:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk
                
                return StreamingResponse(
                    stream_generator(),
                    media_type=content_type,
                    headers={
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, OPTIONS',
                        'Access-Control-Allow-Headers': '*',
                        'Accept-Ranges': 'bytes',
                    }
                )
                
    except httpx.HTTPError as e:
        logger.error(f"Error proxying stream: {e}")
        raise HTTPException(status_code=502, detail=f"Error accessing stream: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")