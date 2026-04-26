// physics.js — modèle inspiré de la vidéo
//
// PRINCIPE (comme dans la vidéo) :
//   Chaque muscle a une horloge interne t et une liste de positions-cibles
//   qu'il essaie d'atteindre à chaque instant via une simple force de rappel élastique.
//   La physique de l'eau = drag anisotrope par segment (résistance latérale >> résistance frontale).
//   Contraintes de distance entre points adjacents résolues par PBD.
//   Pas d'angle, pas de couple, pas d'oriSign — juste F = k*(target - pos).

export const FLUID = {
  C_perp:    1.8,   // drag perpendiculaire au segment (résistance latérale forte)
  C_para:    0.04,  // drag parallèle (glisse bien dans l'axe du membre)
  damping:   0.12,  // amortissement global (évite l'emballement)
};

const MAX_V    = 5.0;   // vitesse max par point
const PBD_ITER = 8;     // itérations de correction de distance
const MUSCLE_K = 12.0;  // raideur du ressort musculaire (global, ajusté par génome)

// -----------------------------------------------------------
//  Construction de l'état depuis un génome
// -----------------------------------------------------------
export function buildState(genome) {
  const N = genome.points.length;
  const px  = new Float64Array(N);
  const py  = new Float64Array(N);
  const opx = new Float64Array(N);
  const opy = new Float64Array(N);
  const vx  = new Float64Array(N);
  const vy  = new Float64Array(N);
  const mass = new Float64Array(N);

  for (let i = 0; i < N; i++) {
    px[i]  = genome.points[i][0];
    py[i]  = genome.points[i][1];
    opx[i] = px[i];
    opy[i] = py[i];
    mass[i] = 1.0;
  }

  // Liens rigides : longueur de repos = distance initiale
  const links = genome.links.map(([a, b]) => ({
    i: a, j: b,
    L0: Math.hypot(px[a] - px[b], py[a] - py[b]),
  }));

  // Muscles : chaque muscle est défini sur un pivot p1 avec deux bras p0 et p2.
  // Il oscille entre plusieurs positions-cibles (angle autour du pivot).
  // On stocke l'angle de repos (base) et les oscillations sinusoïdales.
  const muscles = genome.muscles.map(m => {
    const i0 = m.p0, i1 = m.p1, i2 = m.p2;
    // Longueurs des bras au départ (restent fixes)
    const L0 = Math.hypot(px[i0] - px[i1], py[i0] - py[i1]);
    const L2 = Math.hypot(px[i2] - px[i1], py[i2] - py[i1]);
    return {
      i0, i1, i2,
      L0, L2,
      freqs:  m.freqs.slice(),
      amps:   m.amps.slice(),
      phases: m.phases.slice(),
      base:   m.base,        // angle de repos en degrés
      k:      m.intensite,   // raideur propre à ce muscle
    };
  });

  return {
    N, px, py, opx, opy, vx, vy, mass,
    links, muscles,
    t: 0,
    energy: 0,
    angAccum: 0,
    cx0: mean(px),
    cy0: mean(py),
  };
}

function mean(a) {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i];
  return s / a.length;
}

// -----------------------------------------------------------
//  Angle cible du muscle au temps t
//  Retourne un angle en radians, garanti dans [MIN_RAD, MAX_RAD]
// -----------------------------------------------------------
const MIN_RAD = 30 * Math.PI / 180;
const MAX_RAD = 150 * Math.PI / 180;

function targetAngle(m, t) {
  let osc = 0;
  for (let k = 0; k < m.freqs.length; k++)
    osc += m.amps[k] * Math.sin(2 * Math.PI * m.freqs[k] * t + m.phases[k]);
  const raw = (m.base * Math.PI / 180) + osc;
  return Math.max(MIN_RAD, Math.min(MAX_RAD, raw));
}

// -----------------------------------------------------------
//  Calcul des positions cibles des extrémités p0 et p2
//  en fonction de l'angle cible autour du pivot p1
//  C'EST LE PRINCIPE CLÉ DE LA VIDÉO :
//    on calcule où p0 et p2 DEVRAIENT être si l'angle était theta,
//    puis on applique une force F = k * (target - pos)
// -----------------------------------------------------------
function muscleTargetPositions(m, px, py) {
  const { i0, i1, i2, L0, L2 } = m;

  // Vecteur pivot -> p0 (direction de référence)
  const rx = px[i0] - px[i1];
  const ry = py[i0] - py[i1];
  const rn = Math.hypot(rx, ry);
  if (rn < 1e-9) return null;

  // Direction unitaire du bras p1->p0
  const dx = rx / rn, dy = ry / rn;
  // Perpendiculaire (rotation +90°)
  const ox = -dy, oy = dx;

  const theta = targetAngle(m, 0); // angle cible (t passé en dehors)
  const half  = theta / 2;
  const c = Math.cos(half), s = Math.sin(half);

  // p0 cible : L0 dans la direction (cos(half)*dir + sin(half)*perp)
  const t0x = px[i1] + L0 * ( c * dx + s * ox);
  const t0y = py[i1] + L0 * ( c * dy + s * oy);
  // p2 cible : L2 dans la direction (cos(half)*dir - sin(half)*perp)
  const t2x = px[i1] + L2 * ( c * dx - s * ox);
  const t2y = py[i1] + L2 * ( c * dy - s * oy);

  return { t0x, t0y, t2x, t2y };
}

// -----------------------------------------------------------
//  Un pas de simulation
// -----------------------------------------------------------
export function step(s, dt) {
  const { px, py, opx, opy, vx, vy, mass, N } = s;
  const invDt = 1 / dt;

  // 1) Vitesses depuis Verlet
  for (let i = 0; i < N; i++) {
    vx[i] = (px[i] - opx[i]) * invDt;
    vy[i] = (py[i] - opy[i]) * invDt;
  }

  // 2) Forces musculaires : F = k * (position_cible - position_actuelle)
  //    Exactement comme dans la vidéo.
  const fx = new Float64Array(N);
  const fy = new Float64Array(N);

  for (const m of s.muscles) {
    const { i0, i1, i2, L0, L2, k } = m;

    const rx = px[i0] - px[i1];
    const ry = py[i0] - py[i1];
    const rn = Math.hypot(rx, ry);
    if (rn < 1e-9) continue;

    const dx = rx / rn, dy = ry / rn;
    const ox = -dy,    oy = dx;

    const theta = targetAngle(m, s.t);
    const half  = theta / 2;
    const c = Math.cos(half), si = Math.sin(half);

    // Positions cibles
    const t0x = px[i1] + L0 * ( c * dx + si * ox);
    const t0y = py[i1] + L0 * ( c * dy + si * oy);
    const t2x = px[i1] + L2 * ( c * dx - si * ox);
    const t2y = py[i1] + L2 * ( c * dy - si * oy);

    // Forces de rappel élastique (comme un ressort vers la cible)
    const K = k * MUSCLE_K / 10; // normalise intensite (5-15) → raideur raisonnable
    const F0x = K * (t0x - px[i0]);
    const F0y = K * (t0y - py[i0]);
    const F2x = K * (t2x - px[i2]);
    const F2y = K * (t2y - py[i2]);

    fx[i0] += F0x; fy[i0] += F0y;
    fx[i2] += F2x; fy[i2] += F2y;
    // Newton 3 : réaction sur le pivot
    fx[i1] -= F0x + F2x;
    fy[i1] -= F0y + F2y;
  }

  // 3) Drag anisotrope par segment (physique de l'eau de la vidéo)
  //    Résistance forte ⊥ au membre, faible ∥ au membre
  for (const L of s.links) {
    const i = L.i, j = L.j;
    const ex = px[j] - px[i], ey = py[j] - py[i];
    const len = Math.hypot(ex, ey);
    if (len < 1e-9) continue;

    const tx = ex / len, ty = ey / len; // tangente (axe du membre)
    const nx = -ty,      ny = tx;       // normale (perpendiculaire)

    // Vitesse moyenne du segment
    const vmx = 0.5 * (vx[i] + vx[j]);
    const vmy = 0.5 * (vy[i] + vy[j]);

    // Composantes parallèle et perpendiculaire
    const vt = vmx * tx + vmy * ty; // ∥ : glisse bien
    const vn = vmx * nx + vmy * ny; // ⊥ : résistance forte

    // Force de drag : F = -C * v * L  (linéaire, plus stable que quadratique)
    const Ft = -FLUID.C_para * vt * len;
    const Fn = -FLUID.C_perp * vn * len;

    const Fsx = Ft * tx + Fn * nx;
    const Fsy = Ft * ty + Fn * ny;

    fx[i] += 0.5 * Fsx; fy[i] += 0.5 * Fsy;
    fx[j] += 0.5 * Fsx; fy[j] += 0.5 * Fsy;
  }

  // 4) Amortissement global + plafond de force
  for (let i = 0; i < N; i++) {
    fx[i] -= FLUID.damping * vx[i];
    fy[i] -= FLUID.damping * vy[i];
    const fn = Math.hypot(fx[i], fy[i]);
    if (fn > 40) { fx[i] *= 40 / fn; fy[i] *= 40 / fn; }
  }

  // 5) Intégration Euler semi-implicite (plus simple et stable que Verlet ici)
  for (let i = 0; i < N; i++) {
    vx[i] += (fx[i] / mass[i]) * dt;
    vy[i] += (fy[i] / mass[i]) * dt;
    // Clamp vitesse
    const spd = Math.hypot(vx[i], vy[i]);
    if (spd > MAX_V) { vx[i] *= MAX_V / spd; vy[i] *= MAX_V / spd; }
  }

  // 6) PBD — contraintes de distance (liens rigides)
  for (let it = 0; it < PBD_ITER; it++) {
    for (const L of s.links) {
      const i = L.i, j = L.j;
      const dx = px[j] - px[i] + (vx[j] - vx[i]) * dt;
      const dy = py[j] - py[i] + (vy[j] - vy[i]) * dt;
      const d = Math.hypot(dx, dy);
      if (d < 1e-9) continue;
      const err = (d - L.L0) / d * 0.5;
      // Correction des vitesses (XPBD style)
      vx[i] += err * dx / dt; vy[i] += err * dy / dt;
      vx[j] -= err * dx / dt; vy[j] -= err * dy / dt;
    }
  }

  // 7) Intégration des positions
  for (let i = 0; i < N; i++) {
    opx[i] = px[i]; opy[i] = py[i];
    px[i] += vx[i] * dt;
    py[i] += vy[i] * dt;
  }

  // 8) Freinage angulaire (réduit la rotation du corps entier)
  let cmx = 0, cmy = 0, mt = 0;
  for (let i = 0; i < N; i++) { cmx += px[i]; cmy += py[i]; mt++; }
  cmx /= mt; cmy /= mt;
  let vcmx = 0, vcmy = 0;
  for (let i = 0; i < N; i++) { vcmx += vx[i]; vcmy += vy[i]; }
  vcmx /= mt; vcmy /= mt;
  let Lz = 0, Irot = 0;
  for (let i = 0; i < N; i++) {
    const rx = px[i] - cmx, ry = py[i] - cmy;
    Lz   += rx * (vy[i] - vcmy) - ry * (vx[i] - vcmx);
    Irot += rx * rx + ry * ry;
  }
  const omega = Irot > 1e-9 ? Lz / Irot : 0;
  const rotDamp = Math.min(1.0, 5.0 * dt);
  for (let i = 0; i < N; i++) {
    const rx = px[i] - cmx, ry = py[i] - cmy;
    vx[i] -= rotDamp * (-omega * ry);
    vy[i] -= rotDamp * ( omega * rx);
  }

  s.angAccum += Math.abs(omega) * dt;

  // Énergie cinétique
  let Ek = 0;
  for (let i = 0; i < N; i++)
    Ek += 0.5 * mass[i] * (vx[i] * vx[i] + vy[i] * vy[i]);
  s.energy += Ek * dt;
  s.t += dt;
}

// -----------------------------------------------------------
//  Fitness : distance² / (1 + énergie + pénalité rotation)
// -----------------------------------------------------------
export function evaluate(s) {
  const cx = mean(s.px), cy = mean(s.py);
  const dist = Math.hypot(cx - s.cx0, cy - s.cy0);
  return (dist * dist) / (1 + s.energy + 2.0 * s.angAccum);
}

export function centerOfMass(s) {
  return [mean(s.px), mean(s.py)];
}
