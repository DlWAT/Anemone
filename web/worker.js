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
};
let population = [];   // [{genome, fitness}]
let generation = 0;
let history = [];      // [{gen, best, mean}]

function evalGenome(genome) {
  const s = buildState(genome);
  for (let i = 0; i < cfg.steps; i++) step(s, cfg.dt);
  return evaluate(s);
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

function evolveOnce() {
  // Évalue tout le monde
  for (const ind of population) {
    ind.fitness = evalGenome(ind.genome);
  }
  population.sort((a, b) => b.fitness - a.fitness);

  const best = population[0].fitness;
  const mean = population.reduce((s, x) => s + x.fitness, 0) / population.length;
  const species = buildSpecies(population);
  const activeSpecies = species.slice(0, Math.max(2, cfg.maxSpecies));
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
    history,
  });

  // Sélection + reproduction
  const nElite = Math.max(2, Math.floor(cfg.popSize * cfg.eliteFrac));
  const nImmigrants = Math.max(1, Math.floor(cfg.popSize * cfg.immigrantFrac));
  const newPop = [];

  // Elitisme par espèce active pour garder de la diversité
  for (const sp of activeSpecies) {
    if (newPop.length >= nElite) break;
    newPop.push({ genome: JSON.parse(JSON.stringify(sp.best.genome)), fitness: 0 });
  }
  // Complément élitisme global
  for (let i = 0; i < population.length && newPop.length < nElite; i++) {
    newPop.push({ genome: JSON.parse(JSON.stringify(population[i].genome)), fitness: 0 });
  }

  const activeKeys = new Set(activeSpecies.map((sp) => sp.key));
  const breederPool = population.filter((ind) => activeKeys.has(ind.species));
  const pool = breederPool.length >= 4 ? breederPool : population;

  while (newPop.length < cfg.popSize - nImmigrants) {
    // tournoi
    const a = tournament(pool), b = tournament(pool);
    let child;
    if (Math.random() < cfg.crossoverProb) child = crossover(a.genome, b.genome);
    else child = JSON.parse(JSON.stringify(a.genome));
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
    evolveOnce();
    // céder le contrôle pour ne pas bloquer le worker
    await new Promise(r => setTimeout(r, 0));
  }
}

onmessage = (e) => {
  const msg = e.data;
  if (msg.type === 'start') {
    Object.assign(cfg, msg.cfg || {});
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
    initPopulation(msg.seed);
    generation = 0;
    history = [];
    postMessage({ type: 'reset_ack' });
  } else if (msg.type === 'cfg') {
    Object.assign(cfg, msg.cfg);
  }
};
