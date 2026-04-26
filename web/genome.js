// genome.js — génération et mutation des génomes
// Compatible avec le modèle de la vidéo :
//   chaque muscle oscille autour d'un angle de repos via des sinusoïdes.
//   Les amplitudes sont bornées pour que base ± totalAmp ∈ [BASE_MIN, BASE_MAX].

const rand    = (a, b) => a + Math.random() * (b - a);
const randInt = (a, b) => Math.floor(a + Math.random() * (b - a + 1));
const gauss   = (sd = 1) => {
  const u = 1 - Math.random(), v = Math.random();
  return sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
};
const choice = arr => arr[Math.floor(Math.random() * arr.length)];

// -----------------------------------------------------------
//  Bornes géométriques
// -----------------------------------------------------------
const SEG_MIN    = 0.6;   // longueur min d'un bras
const SEG_MAX    = 2.2;   // longueur max
const ANG_MIN    = 35;    // angle articulaire minimum (degrés) — aligné physics MIN_RAD
const ANG_MAX    = 145;   // angle articulaire maximum
const BASE_MIN   = 50;    // angle de repos minimum (degrés) — laisse de la place pour osciller
const BASE_MAX   = 130;   // angle de repos maximum
const MAX_DEG    = 3;     // max 3 bras par nœud
const DIST_MIN   = 0.45;  // distance minimale entre deux points quelconques

// Budget d'amplitude : base ± totalAmp ∈ [ANG_MIN, ANG_MAX]
// On garde aussi une marge interne de 4° pour absorber les dérives numériques
const AMP_MARGIN = 4 * Math.PI / 180;

// -----------------------------------------------------------
//  Validation complète d'un génome
// -----------------------------------------------------------
export function validateGenome(g) {
  const pts = g.points;
  const N = pts.length;
  if (N < 3 || !g.links.length || !g.muscles.length) return false;

  // 1) segments valides + degré max
  const deg = new Array(N).fill(0);
  for (const [a, b] of g.links) {
    if (a < 0 || b < 0 || a >= N || b >= N || a === b) return false;
    const d = Math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1]);
    if (d < SEG_MIN || d > SEG_MAX) return false;
    deg[a]++; deg[b]++;
  }
  for (let i = 0; i < N; i++) if (deg[i] > MAX_DEG) return false;

  // 2) pas de points trop proches
  for (let i = 0; i < N; i++)
    for (let j = i + 1; j < N; j++)
      if (Math.hypot(pts[i][0]-pts[j][0], pts[i][1]-pts[j][1]) < DIST_MIN) return false;

  // 3) muscles valides
  for (const m of g.muscles) {
    const { p0, p1, p2 } = m;
    if ([p0, p1, p2].some(p => p < 0 || p >= N)) return false;
    if (new Set([p0, p1, p2]).size < 3) return false;

    // angle géométrique initial
    const ang = angleDeg(pts[p0], pts[p1], pts[p2]);
    if (ang < ANG_MIN || ang > ANG_MAX) return false;

    // angle de repos dans les bornes
    if (m.base < BASE_MIN || m.base > BASE_MAX) return false;

    // amplitude totale : base ± totalAmp doit rester dans [ANG_MIN, ANG_MAX]
    const totalAmp = m.amps.reduce((s, a) => s + Math.abs(a), 0);
    const baseRad  = m.base * Math.PI / 180;
    if (baseRad - totalAmp < ANG_MIN * Math.PI / 180 + AMP_MARGIN) return false;
    if (baseRad + totalAmp > ANG_MAX * Math.PI / 180 - AMP_MARGIN) return false;
  }

  return true;
}

function angleDeg(p0, p1, p2) {
  const ax = p0[0]-p1[0], ay = p0[1]-p1[1];
  const bx = p2[0]-p1[0], by = p2[1]-p1[1];
  const na = Math.hypot(ax, ay), nb = Math.hypot(bx, by);
  if (na < 1e-9 || nb < 1e-9) return 0;
  const c = Math.max(-1, Math.min(1, (ax*bx + ay*by) / (na*nb)));
  return Math.acos(c) * 180 / Math.PI;
}

// -----------------------------------------------------------
//  Génération aléatoire
// -----------------------------------------------------------
export function randomGenome() {
  for (let tries = 0; tries < 60; tries++) {
    const g = choice(['chain', 'fork']) === 'fork' ? buildFork() : buildChain();
    if (g && validateGenome(g)) return g;
  }
  return buildMinimal();
}

function buildChain() {
  const N = randInt(3, 6);
  const points = [[0, 0]];
  let ang = rand(-0.3, 0.3);
  for (let i = 1; i < N; i++) {
    ang += rand(-0.45, 0.45);
    const len = rand(SEG_MIN + 0.1, SEG_MAX - 0.2);
    const prev = points[i-1];
    points.push([prev[0] + len * Math.cos(ang), prev[1] + len * Math.sin(ang)]);
  }
  const links   = Array.from({length: N-1}, (_, i) => [i, i+1]);
  const muscles = [];
  for (let i = 0; i < N-2; i++) {
    const m = makeMuscle(i, i+1, i+2, points);
    if (m) muscles.push(m);
  }
  return { points, links, muscles };
}

function buildFork() {
  const trunk = randInt(3, 5);
  const points = [];
  for (let i = 0; i < trunk; i++) points.push([i * 1.1, 0]);

  const root      = trunk - 1;
  const branchLen = rand(SEG_MIN + 0.1, 1.4);
  const branchAng = rand(0.75, 1.15); // ~43–66°
  const [rx, ry]  = points[root];
  points.push([rx + branchLen * Math.cos(branchAng),  branchLen * Math.sin(branchAng)]);
  points.push([rx + branchLen * Math.cos(-branchAng), branchLen * Math.sin(-branchAng)]);

  const links = Array.from({length: trunk-1}, (_, i) => [i, i+1]);
  links.push([root, trunk], [root, trunk+1]);

  const muscles = [];
  for (let i = 0; i < trunk-2; i++) {
    const m = makeMuscle(i, i+1, i+2, points);
    if (m) muscles.push(m);
  }
  const prev = root - 1 >= 0 ? root - 1 : root + 1;
  const mA = makeMuscle(prev, root, trunk,   points);
  const mB = makeMuscle(prev, root, trunk+1, points);
  if (mA) muscles.push(mA);
  if (mB) muscles.push(mB);

  return { points, links, muscles };
}

function makeMuscle(p0, p1, p2, points) {
  const angInit = angleDeg(points[p0], points[p1], points[p2]);
  if (angInit < ANG_MIN || angInit > ANG_MAX) return null;

  // base proche de l'angle initial, centré dans [BASE_MIN, BASE_MAX]
  const base = Math.max(BASE_MIN, Math.min(BASE_MAX, angInit + rand(-8, 8)));
  const baseRad = base * Math.PI / 180;

  // budget d'amplitude disponible (avec marge de sécurité)
  const budget = Math.min(
    baseRad - ANG_MIN * Math.PI / 180 - AMP_MARGIN,
    ANG_MAX * Math.PI / 180 - baseRad - AMP_MARGIN,
    0.55
  );
  if (budget < 0.04) return null;

  const K = randInt(1, 2);
  const ampPerK = budget / K;
  const freqs = [], amps = [], phases = [];
  for (let k = 0; k < K; k++) {
    freqs.push(rand(0.3, 1.6));
    amps.push(rand(0.02, ampPerK * 0.9)); // 90% du budget max par harmonique
    phases.push(rand(0, 2 * Math.PI));
  }
  return { p0, p1, p2, freqs, amps, phases, base, intensite: rand(6, 14) };
}

function buildMinimal() {
  return {
    points:  [[0,0], [1.0,0], [0.5, 0.87]],
    links:   [[0,1],[1,2]],
    muscles: [{
      p0:0, p1:1, p2:2,
      freqs:[0.7], amps:[0.35], phases:[0],
      base:90, intensite:8,
    }],
  };
}

// -----------------------------------------------------------
//  Mutation
// -----------------------------------------------------------
export function mutate(genome, strength = 0.1) {
  const g = JSON.parse(JSON.stringify(genome));

  for (const m of g.muscles) {
    const baseRad = m.base * Math.PI / 180;
    const r = Math.random();

    if (r < 0.25 && m.freqs.length) {
      const k = randInt(0, m.freqs.length - 1);
      m.freqs[k] = Math.max(0.1, Math.min(3.0, m.freqs[k] + gauss(strength * 0.5)));

    } else if (r < 0.50 && m.amps.length) {
      const k = randInt(0, m.amps.length - 1);
      const otherTotal = m.amps.reduce((s, a, i) => i === k ? s : s + Math.abs(a), 0);
      const maxK = Math.min(
        baseRad - ANG_MIN * Math.PI / 180 - AMP_MARGIN - otherTotal,
        ANG_MAX * Math.PI / 180 - baseRad - AMP_MARGIN - otherTotal,
        0.55
      );
      if (maxK > 0.02)
        m.amps[k] = Math.max(0.02, Math.min(maxK, m.amps[k] + gauss(strength * 0.15)));

    } else if (r < 0.70 && m.phases.length) {
      const k = randInt(0, m.phases.length - 1);
      m.phases[k] = (m.phases[k] + gauss(strength * 1.5)) % (2 * Math.PI);

    } else if (r < 0.82) {
      // mutation de base : recalcule les amplitudes si nécessaire
      const newBase = Math.max(BASE_MIN, Math.min(BASE_MAX, m.base + gauss(strength * 8)));
      const newBaseRad = newBase * Math.PI / 180;
      const totalAmp   = m.amps.reduce((s, a) => s + Math.abs(a), 0);
      const newBudget  = Math.min(
        newBaseRad - ANG_MIN * Math.PI / 180 - AMP_MARGIN,
        ANG_MAX * Math.PI / 180 - newBaseRad - AMP_MARGIN
      );
      if (newBudget >= totalAmp) {
        m.base = newBase; // OK direct
      } else if (newBudget > 0.04) {
        // scale down les amplitudes pour rester dans le budget
        const scale = newBudget / totalAmp * 0.95;
        m.amps = m.amps.map(a => a * scale);
        m.base = newBase;
      }

    } else if (r < 0.92) {
      m.intensite = Math.max(2, Math.min(20, m.intensite + gauss(strength * 3)));

    } else if (m.freqs.length < 3) {
      // ajouter une harmonique dans le budget restant
      const totalAmp = m.amps.reduce((s, a) => s + Math.abs(a), 0);
      const budget   = Math.min(
        baseRad - ANG_MIN * Math.PI / 180 - AMP_MARGIN - totalAmp,
        ANG_MAX * Math.PI / 180 - baseRad - AMP_MARGIN - totalAmp
      );
      if (budget > 0.03) {
        m.freqs.push(rand(0.2, 2.0));
        m.amps.push(rand(0.02, budget * 0.8));
        m.phases.push(rand(0, 2 * Math.PI));
      }
    }
  }

  // Mutations morphologiques rares
  if (Math.random() < 0.07 && g.points.length < 8) tryAddBranch(g);
  if (Math.random() < 0.04 && g.points.length > 3) tryRemoveLeaf(g);

  return validateGenome(g) ? g : JSON.parse(JSON.stringify(genome));
}

function tryAddBranch(g) {
  const pts = g.points, N = pts.length;
  const deg = new Array(N).fill(0);
  for (const [a, b] of g.links) { deg[a]++; deg[b]++; }
  const candidates = Array.from({length: N}, (_, i) => i).filter(i => deg[i] < MAX_DEG);
  if (!candidates.length) return;

  for (let attempt = 0; attempt < 15; attempt++) {
    const parent = candidates[randInt(0, candidates.length - 1)];
    const len = rand(SEG_MIN + 0.1, SEG_MAX - 0.2);
    const ang = rand(0, 2 * Math.PI);
    const np  = [pts[parent][0] + len * Math.cos(ang), pts[parent][1] + len * Math.sin(ang)];

    if (pts.some(p => Math.hypot(p[0]-np[0], p[1]-np[1]) < DIST_MIN)) continue;

    const idx = pts.length;
    g.points.push(np);
    g.links.push([Math.min(parent, idx), Math.max(parent, idx)]);

    // chercher un troisième point adjacent au parent pour créer un muscle valide
    const adj = g.links
      .filter(([a, b]) => a === parent || b === parent)
      .map(([a, b]) => a === parent ? b : a)
      .filter(p => p !== idx);

    let added = false;
    for (const nb of adj) {
      const m = makeMuscle(nb, parent, idx, g.points);
      if (m) { g.muscles.push(m); added = true; break; }
    }
    if (!added) { g.points.pop(); g.links.pop(); }
    else return;
  }
}

function tryRemoveLeaf(g) {
  const deg = new Array(g.points.length).fill(0);
  for (const [a, b] of g.links) { deg[a]++; deg[b]++; }
  const leaves = deg.map((d, i) => d === 1 ? i : -1).filter(i => i >= 0);
  if (!leaves.length) return;

  const idx = leaves[randInt(0, leaves.length - 1)];
  g.points.splice(idx, 1);
  const fix = k => k > idx ? k - 1 : k;
  g.links   = g.links.filter(([a, b]) => a !== idx && b !== idx).map(([a, b]) => [fix(a), fix(b)]);
  g.muscles = g.muscles
    .filter(m => m.p0 !== idx && m.p1 !== idx && m.p2 !== idx)
    .map(m => ({ ...m, p0: fix(m.p0), p1: fix(m.p1), p2: fix(m.p2) }));
}

// -----------------------------------------------------------
//  Crossover
// -----------------------------------------------------------
export function crossover(a, b) {
  if (a.points.length !== b.points.length || a.muscles.length !== b.muscles.length)
    return JSON.parse(JSON.stringify(a));
  const child = JSON.parse(JSON.stringify(a));
  for (let i = 0; i < child.muscles.length; i++)
    if (Math.random() < 0.5) child.muscles[i] = JSON.parse(JSON.stringify(b.muscles[i]));
  return validateGenome(child) ? child : JSON.parse(JSON.stringify(a));
}
