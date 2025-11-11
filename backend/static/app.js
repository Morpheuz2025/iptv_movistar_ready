// Estado global
let channels = [];
let epg = {};
let currentChannelIdx = null;
let currentHls = null;
let searchTerm = '';

// Elementos del DOM
const channelsEl = document.getElementById('channels');
const playerEl = document.getElementById('player');
const epgEl = document.getElementById('epg');
const searchInput = document.getElementById('search');
const filterBtns = document.querySelectorAll('.filter-btn');
const refreshBtn = document.getElementById('refresh-btn');
const loadingEl = document.getElementById('loading');

// Fetch helper con manejo de errores
async function fetchJSON(path) {
  try {
    const r = await fetch(path);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    console.error('Error fetching:', path, e);
    showNotification('Error de conexión', 'error');
    return null;
  }
}

// Crear tarjeta de canal
function createChannelCard(c, idx) {
  const d = document.createElement('div');
  d.className = 'card';
  d.dataset.idx = idx;
  
  const img = document.createElement('img');
  img.className = 'logo';
  img.src = c.tvg_logo || '';
  img.alt = c.title;
  img.onerror = () => img.style.display = 'none';
  
  const meta = document.createElement('div');
  meta.className = 'meta';
  
  const name = document.createElement('div');
  name.className = 'name';
  name.innerText = c.title;
  
  const group = document.createElement('div');
  group.className = 'group';
  group.innerText = c.group || 'Sin categoría';
  
  meta.appendChild(name);
  meta.appendChild(group);
  d.appendChild(img);
  d.appendChild(meta);
  
  d.onclick = () => selectChannel(idx);
  
  return d;
}

// Cargar todos los datos
async function loadAll() {
  showLoading(true);
  channelsEl.innerHTML = '<div class="loading-text">Cargando canales...</div>';
  
  channels = await fetchJSON('/api/channels') || [];
  epg = await fetchJSON('/api/epg') || {};
  
  renderChannels();
  showLoading(false);
  
  if (channels.length === 0) {
    showNotification('No se encontraron canales', 'warning');
  }
}

// Renderizar canales filtrados
function renderChannels() {
  channelsEl.innerHTML = '';
  
  const filtered = channels.filter(c => {
    const matchSearch = !searchTerm || 
      c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (c.group || '').toLowerCase().includes(searchTerm.toLowerCase());
    return matchSearch;
  });
  
  if (filtered.length === 0) {
    channelsEl.innerHTML = '<div class="no-results">No se encontraron canales</div>';
    return;
  }
  
  filtered.forEach((c, i) => {
    const idx = channels.indexOf(c);
    channelsEl.appendChild(createChannelCard(c, idx));
  });
}

// Seleccionar canal
function selectChannel(i) {
  const c = channels[i];
  if (!c) return;
  
  console.log('═══════════════════════════════════════════════════');
  console.log('🎬 INTENTANDO REPRODUCIR CANAL');
  console.log('📺 Nombre:', c.title);
  console.log('🆔 ID:', i);
  console.log('🔗 URL del M3U:', c.url);
  console.log('═══════════════════════════════════════════════════');
  
  currentChannelIdx = i;
  
  // Actualizar selección visual
  document.querySelectorAll('.card').forEach(n => n.classList.remove('selected'));
  document.querySelector(`.card[data-idx="${i}"]`)?.classList.add('selected');
  
  // Limpiar reproductor anterior
  if (currentHls) {
    currentHls.destroy();
    currentHls = null;
  }
  
  playerEl.innerHTML = '';
  
  // Crear nuevo reproductor
  const video = document.createElement('video');
  video.controls = true;
  video.autoplay = true;
  video.className = 'player';
  video.poster = c.tvg_logo || '';
  
  playerEl.appendChild(video);
  
  // Determinar si usar proxy o URL directa
  let streamUrl = c.url;
  
  // Si la URL tiene problemas conocidos de codificación, usar el proxy
  if (streamUrl.includes('¶') || streamUrl.includes('&para;')) {
    console.warn('⚠️ URL con problemas de encoding detectada, usando proxy');
    streamUrl = `/api/stream/${i}`;
  } else {
    console.log('✅ URL parece correcta, intentando reproducción directa');
  }
  
  console.log('🎯 URL Final a usar:', streamUrl);
  
  // Inicializar HLS
  if (Hls.isSupported()) {
    currentHls = new Hls({
      enableWorker: true,
      lowLatencyMode: true,
      backBufferLength: 90,
      xhrSetup: function(xhr, url) {
        console.log('📡 HLS solicitando:', url.substring(0, 100) + '...');
        // Agregar headers CORS
        xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
      }
    });
    
    currentHls.on(Hls.Events.MANIFEST_LOADED, () => {
      console.log('✅ Manifest HLS cargado correctamente');
    });
    
    currentHls.on(Hls.Events.LEVEL_LOADED, (event, data) => {
      console.log('✅ Nivel de calidad cargado:', data.level);
    });
    
    currentHls.loadSource(streamUrl);
    currentHls.attachMedia(video);
    
    currentHls.on(Hls.Events.ERROR, (event, data) => {
      console.error('❌ Error HLS:', data.type, data.details);
      
      if (data.fatal) {
        console.error('💀 Error FATAL:', data);
        
        // Si falla, intentar con el proxy
        if (!streamUrl.startsWith('/api/stream/')) {
          console.log('🔄 Reintentando con proxy...');
          currentHls.destroy();
          currentHls = new Hls();
          const proxyUrl = `/api/stream/${i}`;
          console.log('🎯 Nueva URL (proxy):', proxyUrl);
          currentHls.loadSource(proxyUrl);
          currentHls.attachMedia(video);
        } else {
          showNotification('Error reproduciendo el canal', 'error');
        }
      }
    });
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    console.log('🍎 Usando reproducción nativa de Safari');
    video.src = streamUrl;
  } else {
    console.error('❌ Formato de video no soportado en este navegador');
    showNotification('Formato de video no soportado', 'error');
  }
  
  // Mostrar EPG
  renderEPG(c);
}

// Renderizar guía EPG
function renderEPG(channel) {
  const id = channel.tvg_id || channel.title;
  const list = epg[id] || [];
  
  if (list.length === 0) {
    epgEl.innerHTML = `
      <div class="epg-header">
        <h3>EPG - ${channel.title}</h3>
      </div>
      <div class="epg-empty">No hay información de programación disponible</div>
    `;
    return;
  }
  
  // Formatear fechas
  const formatted = list.map(p => {
    const start = formatDateTime(p.start);
    const stop = formatDateTime(p.stop);
    return {
      ...p,
      startFormatted: start,
      stopFormatted: stop,
      isNow: isCurrentlyAiring(p.start, p.stop)
    };
  });
  
  epgEl.innerHTML = `
    <div class="epg-header">
      <h3>EPG - ${channel.title}</h3>
    </div>
    <ul class="epg-list">
      ${formatted.map(p => `
        <li class="epg-item ${p.isNow ? 'epg-now' : ''}">
          <div class="epg-time">
            <strong>${p.startFormatted}</strong>
            ${p.stopFormatted ? ` - ${p.stopFormatted}` : ''}
          </div>
          <div class="epg-title">${p.title}</div>
        </li>
      `).join('')}
    </ul>
  `;
}

// Formatear fecha/hora desde XMLTV
function formatDateTime(xmltvTime) {
  if (!xmltvTime) return '';
  // Formato: 20231105120000 +0000
  const year = xmltvTime.substr(0, 4);
  const month = xmltvTime.substr(4, 2);
  const day = xmltvTime.substr(6, 2);
  const hour = xmltvTime.substr(8, 2);
  const min = xmltvTime.substr(10, 2);
  return `${day}/${month} ${hour}:${min}`;
}

// Verificar si un programa está en emisión
function isCurrentlyAiring(start, stop) {
  if (!start || !stop) return false;
  const now = new Date();
  const startDate = parseXMLTVDate(start);
  const stopDate = parseXMLTVDate(stop);
  return now >= startDate && now <= stopDate;
}

// Parsear fecha XMLTV
function parseXMLTVDate(xmltvTime) {
  const year = xmltvTime.substr(0, 4);
  const month = xmltvTime.substr(4, 2);
  const day = xmltvTime.substr(6, 2);
  const hour = xmltvTime.substr(8, 2);
  const min = xmltvTime.substr(10, 2);
  const sec = xmltvTime.substr(12, 2);
  return new Date(`${year}-${month}-${day}T${hour}:${min}:${sec}`);
}

// Mostrar notificación
function showNotification(msg, type = 'info') {
  const notif = document.createElement('div');
  notif.className = `notification notification-${type}`;
  notif.innerText = msg;
  document.body.appendChild(notif);
  
  setTimeout(() => {
    notif.classList.add('show');
  }, 10);
  
  setTimeout(() => {
    notif.classList.remove('show');
    setTimeout(() => notif.remove(), 300);
  }, 3000);
}

// Mostrar/ocultar loading
function showLoading(show) {
  loadingEl.style.display = show ? 'flex' : 'none';
}

// Refrescar datos
async function refreshData() {
  showLoading(true);
  try {
    const result = await fetchJSON('/api/refresh');
    if (result && result.ok) {
      await loadAll();
      showNotification('Datos actualizados correctamente', 'success');
    }
  } catch (e) {
    showNotification('Error actualizando datos', 'error');
  }
  showLoading(false);
}

// Event listeners
searchInput?.addEventListener('input', (e) => {
  searchTerm = e.target.value;
  renderChannels();
});

refreshBtn?.addEventListener('click', refreshData);

// Navegación con teclado
document.addEventListener('keydown', (e) => {
  if (currentChannelIdx === null) return;
  
  if (e.key === 'ArrowUp' && currentChannelIdx > 0) {
    selectChannel(currentChannelIdx - 1);
    e.preventDefault();
  } else if (e.key === 'ArrowDown' && currentChannelIdx < channels.length - 1) {
    selectChannel(currentChannelIdx + 1);
    e.preventDefault();
  }
});

// Inicializar
loadAll();