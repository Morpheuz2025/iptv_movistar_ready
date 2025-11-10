async function fetchJSON(path){ const r=await fetch(path); return r.json().catch(()=>null); }
let channels = []; let epg = {};
const channelsEl = document.getElementById('channels');
const playerEl = document.getElementById('player');
const epgEl = document.getElementById('epg');

function createChannelCard(c, idx){
  const d = document.createElement('div'); d.className='card'; d.dataset.idx=idx;
  const img = document.createElement('img'); img.className='logo'; img.src=c.tvg_logo||''; img.onerror=()=>img.style.display='none';
  const meta = document.createElement('div'); meta.className='meta';
  const name = document.createElement('div'); name.className='name'; name.innerText=c.title;
  const group = document.createElement('div'); group.className='group'; group.innerText=c.group||'';
  meta.appendChild(name); meta.appendChild(group);
  d.appendChild(img); d.appendChild(meta);
  d.onclick = ()=> selectChannel(idx);
  return d;
}

async function loadAll(){
  channelsEl.innerText='Cargando canales...';
  channels = await fetchJSON('/api/channels') || [];
  epg = await fetchJSON('/api/epg') || {};
  channelsEl.innerHTML='';
  channels.forEach((c,i)=>channelsEl.appendChild(createChannelCard(c,i)));
}

function selectChannel(i){
  const c = channels[i];
  if(!c) return;
  document.querySelectorAll('.card').forEach(n=>n.classList.remove('selected'));
  document.querySelector('.card[data-idx="'+i+'"]')?.classList.add('selected');
  playerEl.innerHTML='';
  const video = document.createElement('video'); video.controls=true; video.autoplay=true; video.className='player';
  playerEl.appendChild(video);
  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(c.url);
    hls.attachMedia(video);
  } else {
    video.src = c.url;
  }
  const id = c.tvg_id || c.title;
  const list = epg[id] || [];
  epgEl.innerHTML = '<h3>EPG - '+c.title+'</h3><ul>' + list.map(p=>('<li><strong>'+p.start+'</strong> — '+p.title+'</li>')).join('') + '</ul>';
}

loadAll();
