import re
from typing import List, Dict
import httpx

EXTINF_RE = re.compile(r'#EXTINF:-?\d+(.*),(.*)')
ATTR_RE = re.compile(r'(\w+?)="(.*?)"')

async def fetch_m3u(url: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text

async def parse_m3u_text(text: str) -> List[Dict]:
    lines = text.splitlines()
    channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            m = EXTINF_RE.match(line)
            attrs_raw = m.group(1) if m else ''
            title = m.group(2).strip() if m else ''
            attrs = dict(ATTR_RE.findall(attrs_raw))
            url = ''
            if i + 1 < len(lines):
                url = lines[i+1].strip()
            channel = {
                'title': title,
                'tvg_id': attrs.get('tvg-id') or attrs.get('tvg_id') or title,
                'tvg_logo': attrs.get('tvg-logo') or attrs.get('tvg_logo') or '',
                'group': attrs.get('group-title') or attrs.get('group') or '',
                'url': url
            }
            channels.append(channel)
            i += 2
        else:
            i += 1
    return channels
