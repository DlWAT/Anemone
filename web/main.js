// main.js — orchestration UI
import { CreatureRenderer, GridRenderer, FitnessChart } from './renderer.js';
import { randomGenome } from './genome.js';

const bootLog = window.__evolveBootLog || (() => {});
const log = (msg) => {
  bootLog(msg);
  console.log('[Evolve]', msg);
};

window.__evolveMainStarted = true;
bootLog('main.js initialise');

function byId(id) {
  const el = document.getElementById(id);
  if (!el) {
    log('Element introuvable: #' + id);
    throw new Error('Missing element #' + id);
  }
  return el;
}

// ----- Canvas
const bigCanvas = byId('big');
const gridCanvas = byId('grid');
const chartCanvas = byId('chart');
const gridScroll = byId('gridScroll');

function resize() {
  for (const c of [bigCanvas, gridCanvas, chartCanvas]) {
    const rect = c.getBoundingClientRect();
    const fallbackW = c.parentElement ? c.parentElement.clientWidth : 600;
    const fallbackH = c === bigCanvas ? 520 : (c === gridCanvas ? 260 : 120);
    // taille canvas robuste, meme si le layout n'a pas encore resolu les hauteurs
    c.width  = Math.max(50, Math.floor(rect.width || fallbackW));
    c.height = Math.max(50, Math.floor(rect.height || fallbackH));
  }
}
window.addEventListener('resize', resize);
window.addEventListener('load', resize);
resize();
requestAnimationFrame(resize);
log('Canvas initialises: big=' + bigCanvas.width + 'x' + bigCanvas.height + ', grid=' + gridCanvas.width + 'x' + gridCanvas.height);

const big = new CreatureRenderer(bigCanvas);
const grid = new GridRenderer(gridCanvas);
const chart = new FitnessChart(chartCanvas);

let currentGenome = randomGenome();
big.setGenome(currentGenome);
log('Genome initial charge: points=' + currentGenome.points.length + ', links=' + currentGenome.links.length + ', muscles=' + currentGenome.muscles.length);

// Pré-remplir la grille avec quelques créatures aléatoires
grid.setGenomes(Array.from({ length: 24 }, () => randomGenome()));
setGridModePopulation();

// ----- Worker GA
const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
let gaRunning = false;
log('Worker cree');

worker.onerror = (err) => {
  byId('gaState').textContent = 'Erreur worker';
  log('Erreur worker: ' + (err.message || 'inconnue'));
  console.error('Worker error:', err);
};

window.addEventListener('error', (err) => {
  log('Erreur runtime: ' + (err.message || 'inconnue'));
  console.error('Runtime error:', err.error || err.message || err);
});

worker.onmessage = (e) => {
  const m = e.data;
  if (m.type === 'gen') {
    byId('gen').textContent  = m.generation;
    byId('best').textContent = m.best.toFixed(4);
    byId('mean').textContent = m.mean.toFixed(4);
    chart.setHistory(m.history);
    lastTopGenomes = m.topGenomes || [];
    lastSpeciesBest = m.speciesBest || [];
    renderSpeciesList(lastSpeciesBest);
    if (gaRunning) {
      setGridModePopulation();
      grid.setGenomes(lastTopGenomes);
      byId('gridTitle').textContent = `Top 40 — population (${m.speciesCount || 0}/${m.speciesCap || 0} espèces, brut ${m.speciesCountRaw || 0})`;
    }
    if (m.generation % 5 === 0) {
      log('Generation ' + m.generation + ' best=' + m.best.toFixed(4) + ' species=' + (m.speciesCount || 0));
    }
    if (followBest) {
      currentGenome = m.bestGenome;
      big.setGenome(currentGenome);
    }
  }
};

// ----- Controls
let playing = true;
let speed = 1;
let followBest = true;
let lastTopGenomes = [];
let lastSpeciesBest = [];
let selectedSpeciesId = null;

function renderSpeciesList(speciesRows) {
  const container = byId('speciesList');
  container.innerHTML = '';
  for (const sp of speciesRows) {
    const row = document.createElement('button');
    row.className = 'species-item' + (selectedSpeciesId === sp.id ? ' active' : '');
    row.type = 'button';
    row.innerHTML = `<span class="left"><span>${sp.label}</span><span class="tree">${sp.tree || ''}</span></span><span>${sp.fitness.toFixed(3)}</span>`;
    row.onclick = () => {
      selectedSpeciesId = sp.id;
      followBest = false;
      byId('toggleBest').checked = false;
      currentGenome = sp.genome;
      big.setGenome(currentGenome);
      byId('gaState').textContent = `Focus ${sp.label}`;
      log('Focus espece -> ' + sp.label + ' fit=' + sp.fitness.toFixed(3));
      renderSpeciesList(speciesRows);
    };
    container.appendChild(row);
  }
}

function setGridModePopulation() {
  gridCanvas.style.height = '420px';
  requestAnimationFrame(resize);
  gridScroll.scrollTop = 0;
}

function setGridModeSpecies(speciesCount) {
  const cells = Math.max(1, speciesCount);
  const cols = Math.ceil(Math.sqrt(cells));
  const rows = Math.ceil(cells / cols);
  const target = Math.max(420, rows * 140);
  gridCanvas.style.height = `${target}px`;
  requestAnimationFrame(resize);
  gridScroll.scrollTop = 0;
}

byId('btnPlay').onclick = () => {
  playing = !playing;
  byId('btnPlay').textContent = playing ? '⏸ Pause' : '▶ Play';
  byId('gaState').textContent = playing ? 'Simulation active' : 'Simulation en pause';
  log('Click btnPlay -> ' + (playing ? 'play' : 'pause'));
};
byId('btnReset').onclick = () => {
  big.reset();
  log('Click btnReset');
};
byId('speed').oninput = e => {
  speed = parseInt(e.target.value, 10);
  byId('speedVal').textContent = speed + '×';
};
byId('btnRand').onclick = () => {
  currentGenome = randomGenome();
  big.setGenome(currentGenome);
  byId('gaState').textContent = 'Nouveau genome charge';
  log('Click btnRand -> nouveau genome');
};
byId('toggleField').onchange = e => { big.showField = e.target.checked; log('toggleField=' + e.target.checked); };
byId('toggleForces').onchange = e => { big.showForces = e.target.checked; log('toggleForces=' + e.target.checked); };
byId('toggleFollow').onchange = e => { big.followCam = e.target.checked; log('toggleFollow=' + e.target.checked); };
byId('toggleBest').onchange = e => { followBest = e.target.checked; log('toggleBest=' + e.target.checked); };

// GA controls
byId('btnGAStart').onclick = () => {
  if (gaRunning) {
    byId('gaState').textContent = 'Déjà en cours';
    return;
  }
  selectedSpeciesId = null;
  gaRunning = true;
  byId('gaState').textContent = 'En cours…';
  byId('gridTitle').textContent = 'Top 40 — population';
  setGridModePopulation();
  worker.postMessage({
    type: 'start',
    seed: currentGenome,
    cfg: {
      popSize: parseInt(byId('popSize').value),
      steps: parseInt(byId('simSteps').value),
      mutationStrength: parseFloat(byId('mutStrength').value),
    },
  });
  log('Click btnGAStart');
};
byId('btnGAPause').onclick = () => {
  if (!gaRunning) {
    byId('gaState').textContent = 'Déjà en pause';
    return;
  }
  gaRunning = false;
  byId('gaState').textContent = 'En pause (vue espèces)';
  worker.postMessage({ type: 'pause' });
  if (lastSpeciesBest.length) {
    setGridModeSpecies(lastSpeciesBest.length);
    grid.setGenomes(lastSpeciesBest.map((s) => ({ genome: s.genome, label: s.label, fitness: s.fitness })));
    byId('gridTitle').textContent = `Best par espece (${lastSpeciesBest.length})`;
    log('Pause: affichage meilleure creature de chaque espece');
  } else {
    byId('gridTitle').textContent = 'Best par espece (aucune donnee)';
  }
  log('Click btnGAPause');
};
byId('btnGAReset').onclick = () => {
  gaRunning = false;
  selectedSpeciesId = null;
  byId('btnPlay').textContent = '⏸ Pause';
  playing = true;
  worker.postMessage({ type: 'reset', seed: currentGenome });
  byId('gaState').textContent = 'Réinitialisé';
  byId('gridTitle').textContent = 'Top 40 — population';
  setGridModePopulation();
  chart.setHistory([]);
  byId('gen').textContent = '0';
  byId('best').textContent = '—';
  byId('mean').textContent = '—';
  byId('speciesList').innerHTML = '';
  grid.setGenomes(Array.from({ length: 24 }, () => randomGenome()));
  lastTopGenomes = [];
  lastSpeciesBest = [];
  log('Click btnGAReset');
};

// ----- Boucle de rendu
function loop() {
  try {
    if (playing) {
      big.step(speed);
      grid.step(1);
    }
    big.draw();
    grid.draw();
    chart.draw();
  } catch (err) {
    log('Erreur dans loop: ' + (err.message || err));
    console.error(err);
  }
  requestAnimationFrame(loop);
}
loop();
