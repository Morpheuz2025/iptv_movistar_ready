from lxml import etree
from typing import Dict, List
import httpx

async def fetch_xmltv(url: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text

async def parse_xmltv_text(text: str) -> Dict[str, List[Dict]]:
    root = etree.fromstring(text.encode('utf-8'))
    programmes_by_channel = {}
    for prog in root.findall('programme'):
        ch = prog.get('channel')
        title_el = prog.find('title')
        start = prog.get('start')
        stop = prog.get('stop')
        title = title_el.text if title_el is not None else ''
        prog_obj = {'title': title, 'start': start, 'stop': stop}
        programmes_by_channel.setdefault(ch, []).append(prog_obj)
    return programmes_by_channel
