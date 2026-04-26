// worker.js — algorithme génétique tournant en arrière-plan
import { buildState, step, evaluate } from './physics.js';
import { randomGenome, mutate, crossover } from './genome.js';

let running = false;
let cfg = {
  popSize: 80,
  steps: 800,
  dt: 0.02,
  eliteFrac: 0.1,
  mutationStrength: 0.1,
  crossoverProb: 0.3,
  immigrantFrac: 0.12,
  maxSpecies: 12,
  evalWorkers: 0,
};
let population = [];   // [{genome, fitness}]
let generation = 0;
let history = [];      // [{gen, best, mean}]
let evalPool = [];
let evalReqId = 1;

function cloneGenome(genome) {
  return JSON.parse(JSON.stringify(genome));
}

function clonePopulation(pop) {
  return pop.map((ind) => ({ genome: cloneGenome(ind.genome), fitness: Number(ind.fitness) || 0 }));
}

function buildSnapshot() {
  return {
    version: 1,
    createdAt: Date.now(),
    cfg: { ...cfg },
    generation,
    history: history.map((h) => ({ gen: h.gen, best: h.best, mean: h.mean })),
    population: clonePopulation(population),
  };
}

function restoreSnapshot(snapshot) {
  if (!snapshot || !Array.isArray(snapshot.population) || snapshot.population.length === 0) {
    throw new Error('Sauvegarde invalide: population absente');
  }
  population = clonePopulation(snapshot.population);
  generation = Number.isFinite(snapshot.generation) ? Math.max(0, Math.floor(snapshot.generation)) : 0;
  history = Array.isArray(snapshot.history)
    ? snapshot.history.map((h, i) => ({
      gen: Number.isFinite(h.gen) ? h.gen : i,
      best: Number.isFinite(h.best) ? h.best : 0,
      mean: Number.isFinite(h.mean) ? h.mean : 0,
    }))
    : [];
  cfg = {
    ...cfg,
    ...(snapshot.cfg || {}),
    popSize: population.length,
  };
}

function evalGenome(genome) {
  const s = buildState(genome);
  for (let i = 0; i < cfg.steps; i++) step(s, cfg.dt);
  return evaluate(s);
}

function getHardwareThreads() {
  if (typeof navigator !== 'undefined' && Number.isFinite(navigator.hardwareConcurrency)) {
    return Math.max(1, Math.floor(navigator.hardwareConcurrency));
  }
  return 1;
}

function targetEvalWorkers() {
  const requested = Number.isFinite(cfg.evalWorkers) ? Math.floor(cfg.evalWorkers) : 0;
  const byCfg = requested > 0 ? requested : getHardwareThreads();
  return Math.max(1, Math.min(byCfg, cfg.popSize));
}

function terminateEvalPool() {
  for (const w of evalPool) {
    try { w.terminate(); } catch (_) {}
  }
  evalPool = [];
}

function ensureEvalPool() {
  const target = targetEvalWorkers();
  if (target <= 1) {
    if (evalPool.length) terminateEvalPool();
    return;
  }
  if (evalPool.length === target) return;

  terminateEvalPool();
  try {
    for (let i = 0; i < target; i++) {
      evalPool.push(new Worker(new URL('./eval_worker.js', import.meta.url), { type: 'module' }));
    }
  } catch (_) {
    terminateEvalPool();
  }
}

function runEvalBatch(worker, jobs) {
  const reqId = evalReqId++;
  return new Promise((resolve, reject) => {
    const onMessage = (e) => {
      const data = e.data || {};
      if (data.type !== 'eval_batch_done' || data.reqId !== reqId) return;
      cleanup();
      resolve(Array.isArray(data.results) ? data.results : []);
    };
    const onError = () => {
      cleanup();
      reject(new Error('Eval worker failed'));
    };
    const cleanup = () => {
      worker.removeEventListener('message', onMessage);
      worker.removeEventListener('error', onError);
    };

    worker.addEventListener('message', onMessage);
    worker.addEventListener('error', onError);
    worker.postMessage({
      type: 'eval_batch',
      reqId,
      steps: cfg.steps,
      dt: cfg.dt,
      jobs,
    });
  });
}

async function evaluatePopulation(pop) {
  ensureEvalPool();
  if (evalPool.length <= 1) {
    for (const ind of pop) ind.fitness = evalGenome(ind.genome);
    return;
  }

  const shards = Array.from({ length: evalPool.length }, () => []);
  for (let i = 0; i < pop.length; i++) {
    shards[i % evalPool.length].push({ idx: i, genome: pop[i].genome });
  }

  try {
    const tasks = [];
    for (let i = 0; i < evalPool.length; i++) {
      if (shards[i].length === 0) continue;
      tasks.push(runEvalBatch(evalPool[i], shards[i]));
    }
    const allResults = await Promise.all(tasks);
    for (const batch of allResults) {
      for (const r of batch) {
        if (!r || !Number.isFinite(r.idx) || r.idx < 0 || r.idx >= pop.length) continue;
        pop[r.idx].fitness = Number(r.fitness) || 0;
      }
    }
  } catch (_) {
    terminateEvalPool();
    for (const ind of pop) ind.fitness = evalGenome(ind.genome);
  }
}

function initPopulation(seed) {
  population = [];
  for (let i = 0; i < cfg.popSize; i++) {
    let g;
    if (seed && i < cfg.popSize * 0.2) {
      g = mutate(seed, cfg.mutationStrength);
    } else {
      g = randomGenome();
    }
    population.push({ genome: g, fitness: 0 });
  }
}

async function evolveOnce() {
  // Évalue tout le monde
  await evaluatePopulation(population);
  population.sort((a, b) => b.fitness - a.fitness);

  const best = population[0].fitness;
  const mean = population.reduce((s, x) => s + x.fitness, 0) / population.length;
  const species = buildSpecies(population);
  const activeSpecies = species.slice(0, Math.max(2, cfg.maxSpecies));
  const speciesMembers = new Map();
  for (const ind of population) {
    if (!speciesMembers.has(ind.species)) speciesMembers.set(ind.species, []);
    speciesMembers.get(ind.species).push(ind);
  }
  for (const members of speciesMembers.values()) {
    members.sort((a, b) => b.fitness - a.fitness);
  }
  history.push({ gen: generation, best, mean });

  // Push state to main
  postMessage({
    type: 'gen',
    generation,
    best,
    mean,
    bestGenome: population[0].genome,
    topGenomes: population.slice(0, Math.min(40, population.length)).map((p, i) => ({
      genome: p.genome,
      fitness: p.fitness,
      label: `#${i + 1}`,
    })),
    speciesCount: activeSpecies.length,
    speciesCountRaw: species.length,
    speciesCap: cfg.maxSpecies,
    speciesBest: activeSpecies.map((sp, i) => ({
      id: sp.key,
      label: `S${i + 1} (${sp.size})`,
      tree: sp.shape,
      size: sp.size,
      fitness: sp.best.fitness,
      genome: sp.best.genome,
    })),
    evalWorkers: Math.max(1, evalPool.length || targetEvalWorkers()),
    history,
  });

  // Sélection + reproduction
  const nElite = Math.max(2, Math.floor(cfg.popSize * cfg.eliteFrac));
  const nImmigrants = Math.max(1, Math.floor(cfg.popSize * cfg.immigrantFrac));
  const newPop = [];

  // Elitisme par espèce active pour garder de la diversité
  for (const sp of activeSpecies) {
    if (newPop.length >= nElite) break;
    newPop.push({ genome: cloneGenome(sp.best.genome), fitness: 0 });
  }

  // Complément élitisme inter-espèces: 2e, 3e... meilleur de chaque espèce active
  let rankInSpecies = 1;
  while (newPop.length < nElite) {
    let added = false;
    for (const sp of activeSpecies) {
      if (newPop.length >= nElite) break;
      const members = speciesMembers.get(sp.key) || [];
      if (members.length > rankInSpecies) {
        newPop.push({ genome: cloneGenome(members[rankInSpecies].genome), fitness: 0 });
        added = true;
      }
    }
    if (!added) break;
    rankInSpecies++;
  }

  // Dernier recours: complément global si nécessaire
  for (let i = 0; i < population.length && newPop.length < nElite; i++) {
    newPop.push({ genome: cloneGenome(population[i].genome), fitness: 0 });
  }

  const activeKeys = new Set(activeSpecies.map((sp) => sp.key));
  const breederPool = population.filter((ind) => activeKeys.has(ind.species));
  const pool = breederPool.length >= 4 ? breederPool : population;

  const birthsTarget = cfg.popSize - nImmigrants - newPop.length;
  const speciesBirthQuota = new Map();
  if (activeSpecies.length > 0 && birthsTarget > 0) {
    const base = Math.floor(birthsTarget / activeSpecies.length);
    let remainder = birthsTarget % activeSpecies.length;
    const offset = generation % activeSpecies.length;
    for (let i = 0; i < activeSpecies.length; i++) {
      const sp = activeSpecies[(i + offset) % activeSpecies.length];
      const extra = remainder > 0 ? 1 : 0;
      speciesBirthQuota.set(sp.key, base + extra);
      if (remainder > 0) remainder--;
    }
  }

  for (const sp of activeSpecies) {
    const quota = speciesBirthQuota.get(sp.key) || 0;
    const localPool = speciesMembers.get(sp.key) || pool;
    for (let i = 0; i < quota && newPop.length < cfg.popSize - nImmigrants; i++) {
      const a = tournament(localPool);
      const bPool = Math.random() < 0.7 ? localPool : pool;
      const b = tournament(bPool);
      let child;
      if (Math.random() < cfg.crossoverProb) child = crossover(a.genome, b.genome);
      else child = cloneGenome(a.genome);
      child = mutate(child, cfg.mutationStrength);
      newPop.push({ genome: child, fitness: 0 });
    }
  }

  while (newPop.length < cfg.popSize - nImmigrants) {
    const a = tournament(pool);
    const b = tournament(pool);
    let child;
    if (Math.random() < cfg.crossoverProb) child = crossover(a.genome, b.genome);
    else child = cloneGenome(a.genome);
    child = mutate(child, cfg.mutationStrength);
    newPop.push({ genome: child, fitness: 0 });
  }

  // Immigrants aléatoires pour maintenir une forte diversité inter-espèces
  for (let i = 0; i < nImmigrants && newPop.length < cfg.popSize; i++) {
    newPop.push({ genome: randomGenome(), fitness: 0 });
  }

  population = newPop;
  generation++;
}

function buildSpecies(pop) {
  const buckets = new Map();
  for (const ind of pop) {
    const shape = speciesShape(ind.genome);
    const key = shape;
    ind.species = key;
    let b = buckets.get(key);
    if (!b) {
      b = { key, shape, size: 0, best: ind };
      buckets.set(key, b);
    }
    b.size++;
    if (ind.fitness > b.best.fitness) b.best = ind;
  }
  return Array.from(buckets.values()).sort((a, b) => b.best.fitness - a.best.fitness);
}

function speciesShape(g) {
  const n = g.points.length;
  const links = g.links;
  // Signature structurelle pure: forme d'arbre canonique (AHU)
  if (links.length === n - 1) {
    const canonical = canonicalTree(links, n);
    return `T${n}:${canonical}`;
  }
  // Fallback robuste si la topologie n'est pas exactement un arbre
  const deg = new Array(n).fill(0);
  for (const [i, j] of links) {
    if (i >= 0 && i < n) deg[i]++;
    if (j >= 0 && j < n) deg[j]++;
  }
  deg.sort((a, b) => a - b);
  return `G${n}:${links.length}:${deg.join('.')}`;
}

function canonicalTree(links, n) {
  const adj = Array.from({ length: n }, () => []);
  for (const [a, b] of links) {
    if (a < 0 || b < 0 || a >= n || b >= n || a === b) continue;
    adj[a].push(b);
    adj[b].push(a);
  }
  const centers = treeCenters(adj);
  if (centers.length === 1) return encodeRooted(adj, centers[0], -1);
  const c1 = encodeRooted(adj, centers[0], centers[1]);
  const c2 = encodeRooted(adj, centers[1], centers[0]);
  return c1 < c2 ? `${c1}|${c2}` : `${c2}|${c1}`;
}

function treeCenters(adj) {
  const n = adj.length;
  const deg = adj.map((a) => a.length);
  let leaves = [];
  for (let i = 0; i < n; i++) if (deg[i] <= 1) leaves.push(i);
  let removed = leaves.length;
  while (removed < n) {
    const next = [];
    for (const leaf of leaves) {
      for (const nb of adj[leaf]) {
        deg[nb]--;
        if (deg[nb] === 1) next.push(nb);
      }
    }
    removed += next.length;
    if (!next.length) break;
    leaves = next;
  }
  return leaves;
}

function encodeRooted(adj, node, parent) {
  const parts = [];
  for (const nb of adj[node]) {
    if (nb === parent) continue;
    parts.push(encodeRooted(adj, nb, node));
  }
  parts.sort();
  return `(${parts.join('')})`;
}

function tournament(pool, k = 3) {
  let best = null;
  for (let i = 0; i < k; i++) {
    const c = pool[Math.floor(Math.random() * pool.length)];
    if (!best || c.fitness > best.fitness) best = c;
  }
  return best;
}

async function loop() {
  while (running) {
    await evolveOnce();
    // céder le contrôle pour ne pas bloquer le worker
    await new Promise(r => setTimeout(r, 0));
  }
}

onmessage = (e) => {
  const msg = e.data;
  if (msg.type === 'start') {
    Object.assign(cfg, msg.cfg || {});
    ensureEvalPool();
    if (population.length === 0) {
      initPopulation(msg.seed);
      generation = 0;
      history = [];
    }
    if (!running) {
      running = true;
      loop();
    }
  } else if (msg.type === 'pause') {
    running = false;
  } else if (msg.type === 'reset') {
    running = false;
    ensureEvalPool();
    initPopulation(msg.seed);
    generation = 0;
    history = [];
    postMessage({ type: 'reset_ack' });
  } else if (msg.type === 'cfg') {
    Object.assign(cfg, msg.cfg);
    ensureEvalPool();
  } else if (msg.type === 'snapshot') {
    if (!population.length) {
      postMessage({ type: 'error', message: 'Aucune evolution a sauvegarder pour le moment' });
    } else {
      postMessage({ type: 'snapshot', snapshot: buildSnapshot() });
    }
  } else if (msg.type === 'import') {
    try {
      running = false;
      restoreSnapshot(msg.snapshot);
      ensureEvalPool();
      population.sort((a, b) => b.fitness - a.fitness);
      const species = buildSpecies(population);
      const activeSpecies = species.slice(0, Math.max(2, cfg.maxSpecies));
      const best = population.reduce((m, ind) => Math.max(m, ind.fitness), -Infinity);
      const mean = population.reduce((s, ind) => s + ind.fitness, 0) / population.length;
      postMessage({
        type: 'import_ack',
        generation,
        best: Number.isFinite(best) ? best : 0,
        mean: Number.isFinite(mean) ? mean : 0,
        cfg: { ...cfg },
        history,
        topGenomes: population.slice(0, Math.min(40, population.length)).map((p, i) => ({
          genome: p.genome,
          fitness: p.fitness,
          label: `#${i + 1}`,
        })),
        speciesBest: activeSpecies.map((sp, i) => ({
          id: sp.key,
          label: `S${i + 1} (${sp.size})`,
          tree: sp.shape,
          size: sp.size,
          fitness: sp.best.fitness,
          genome: sp.best.genome,
        })),
      });
    } catch (err) {
      postMessage({ type: 'error', message: err && err.message ? err.message : 'Import impossible' });
    }
  }
};
