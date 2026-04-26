// renderer.js — rendu Canvas optimisé pour la créature et la grille de population
import { buildState, step, centerOfMass } from './physics.js';

// =============================================================
//  Rendu d'une créature unique avec trails et muscles colorés
// =============================================================
export class CreatureRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.state = null;
    this.genome = null;
    this.dt = 0.02;
    this.scale = 30;        // pixels par unité
    this.cam = [0, 0];
    this.followCam = true;
    this.trails = [];
    this.maxTrail = 240;
    this.showField = false;
    this.showForces = false;
  }

  setGenome(genome) {
    this.genome = JSON.parse(JSON.stringify(genome));
    this.state = buildState(this.genome);
    const [cx, cy] = centerOfMass(this.state);
    this.cam = [cx, cy];
    this.trails = Array.from(this.state.px, (x, i) => [{ x, y: this.state.py[i] }]);
  }

  reset() {
    if (this.genome) this.setGenome(this.genome);
  }

  step(speed = 1) {
    if (!this.state) return;
    const sub = Math.max(1, Math.floor(speed));
    for (let k = 0; k < sub; k++) step(this.state, this.dt);

    // mise à jour des trails
    for (let i = 0; i < this.state.N; i++) {
      if (!Array.isArray(this.trails[i])) this.trails[i] = [];
      const arr = this.trails[i];
      arr.push({ x: this.state.px[i], y: this.state.py[i] });
      if (arr.length > this.maxTrail) arr.shift();
    }
    if (this.followCam) {
      const [cx, cy] = centerOfMass(this.state);
      this.cam[0] += (cx - this.cam[0]) * 0.08;
      this.cam[1] += (cy - this.cam[1]) * 0.08;
    }
  }

  worldToScreen(x, y) {
    const W = this.canvas.width, H = this.canvas.height;
    return [
      W / 2 + (x - this.cam[0]) * this.scale,
      H / 2 + (y - this.cam[1]) * this.scale,
    ];
  }

  draw() {
    const ctx = this.ctx;
    const W = this.canvas.width, H = this.canvas.height;

    // fond dégradé "eau"
    const grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, '#0a1a2a');
    grad.addColorStop(1, '#04101c');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // grille subtile pour montrer le déplacement
    this.drawGrid();

    if (!this.state) {
      ctx.fillStyle = 'rgba(255,255,255,0.8)';
      ctx.font = '14px ui-monospace, monospace';
      ctx.fillText('Aucun etat a afficher', 16, 24);
      return;
    }

    // champ de vitesses (particules de traceur)
    if (this.showField) this.drawTracers();

    // trails
    ctx.lineCap = 'round';
    for (let i = 0; i < this.trails.length; i++) {
      const tr = this.trails[i];
      if (tr.length < 2) continue;
      ctx.beginPath();
      const [x0, y0] = this.worldToScreen(tr[0].x, tr[0].y);
      ctx.moveTo(x0, y0);
      for (let k = 1; k < tr.length; k++) {
        const [x, y] = this.worldToScreen(tr[k].x, tr[k].y);
        ctx.lineTo(x, y);
      }
      ctx.strokeStyle = `rgba(120,200,255,${0.18})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // liens
    const s = this.state;
    ctx.lineWidth = 3;
    for (const L of s.links) {
      const [x1, y1] = this.worldToScreen(s.px[L.i], s.py[L.i]);
      const [x2, y2] = this.worldToScreen(s.px[L.j], s.py[L.j]);
      // couleur selon étirement
      const dx = s.px[L.j] - s.px[L.i], dy = s.py[L.j] - s.py[L.i];
      const cur = Math.hypot(dx, dy);
      const stretch = (cur - L.L0) / L.L0;
      const c = stretchColor(stretch);
      ctx.strokeStyle = c;
      ctx.beginPath();
      ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    // muscles (triangles légèrement remplis)
    for (const m of s.muscles) {
      const [a, b, c] = [m.i0, m.i1, m.i2];
      const p1 = this.worldToScreen(s.px[a], s.py[a]);
      const p2 = this.worldToScreen(s.px[b], s.py[b]);
      const p3 = this.worldToScreen(s.px[c], s.py[c]);
      // intensité = écart à l'angle de repos
      ctx.beginPath();
      ctx.moveTo(...p1); ctx.lineTo(...p2); ctx.lineTo(...p3); ctx.closePath();
      ctx.fillStyle = 'rgba(255,140,80,0.10)';
      ctx.fill();
    }

    // points
    for (let i = 0; i < s.N; i++) {
      const [x, y] = this.worldToScreen(s.px[i], s.py[i]);
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fillStyle = '#ffeb88';
      ctx.fill();
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // vecteurs de force
    if (this.showForces) {
      ctx.strokeStyle = 'rgba(255,80,80,0.9)';
      ctx.lineWidth = 1.5;
      for (let i = 0; i < s.N; i++) {
        const [x, y] = this.worldToScreen(s.px[i], s.py[i]);
        const fx = s.fx[i], fy = s.fy[i];
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + fx * 8, y + fy * 8);
        ctx.stroke();
      }
    }

    // HUD : distance, énergie, vitesse
    const [cx, cy] = centerOfMass(s);
    const dist = Math.hypot(cx - s.cx0, cy - s.cy0);
    const fitness = (dist * dist) / (1 + s.energy);
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.font = '13px ui-monospace,monospace';
    ctx.fillText(`t=${s.t.toFixed(2)}s   distance=${dist.toFixed(2)}   E=${s.energy.toFixed(2)}   fit=${fitness.toFixed(3)}`, 12, 20);
  }

  drawGrid() {
    const ctx = this.ctx;
    const W = this.canvas.width, H = this.canvas.height;
    const step = this.scale;
    const ox = ((W / 2 - this.cam[0] * this.scale) % step + step) % step;
    const oy = ((H / 2 - this.cam[1] * this.scale) % step + step) % step;
    ctx.strokeStyle = 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = ox; x < W; x += step) { ctx.moveTo(x, 0); ctx.lineTo(x, H); }
    for (let y = oy; y < H; y += step) { ctx.moveTo(0, y); ctx.lineTo(W, y); }
    ctx.stroke();
  }

  // Particules de traceur déplacées par le champ approximatif
  // (interpolation rapide à partir des vitesses des points)
  drawTracers() {
    if (!this.tracers) {
      this.tracers = [];
      for (let i = 0; i < 200; i++) {
        this.tracers.push({
          x: this.cam[0] + (Math.random() - 0.5) * 30,
          y: this.cam[1] + (Math.random() - 0.5) * 20,
          life: Math.random(),
        });
      }
    }
    const s = this.state;
    const ctx = this.ctx;
    ctx.fillStyle = 'rgba(180,220,255,0.35)';
    for (const t of this.tracers) {
      // approx vitesse = somme pondérée des vitesses des points (kernel inverse-distance)
      let vxSum = 0, vySum = 0, w = 0;
      for (let i = 0; i < s.N; i++) {
        const dx = t.x - s.px[i], dy = t.y - s.py[i];
        const r2 = dx * dx + dy * dy + 0.5;
        const wi = 1 / r2;
        vxSum += s.vx[i] * wi; vySum += s.vy[i] * wi; w += wi;
      }
      t.x += (vxSum / w) * this.dt * 1.2;
      t.y += (vySum / w) * this.dt * 1.2;
      t.life -= 0.005;
      // recyclage
      const dx = t.x - this.cam[0], dy = t.y - this.cam[1];
      if (t.life < 0 || Math.abs(dx) > 25 || Math.abs(dy) > 18) {
        t.x = this.cam[0] + (Math.random() - 0.5) * 30;
        t.y = this.cam[1] + (Math.random() - 0.5) * 20;
        t.life = 1;
      }
      const [sx, sy] = this.worldToScreen(t.x, t.y);
      ctx.fillRect(sx, sy, 1.5, 1.5);
    }
  }
}

function stretchColor(s) {
  // s ∈ [-0.3, 0.3] typiquement
  const v = Math.max(-0.3, Math.min(0.3, s));
  if (v >= 0) {
    // étiré → rouge
    const a = v / 0.3;
    return `rgb(${Math.round(180 + 75 * a)},${Math.round(180 - 130 * a)},${Math.round(180 - 130 * a)})`;
  } else {
    // comprimé → bleu
    const a = -v / 0.3;
    return `rgb(${Math.round(180 - 130 * a)},${Math.round(180 - 30 * a)},${Math.round(180 + 75 * a)})`;
  }
}

// =============================================================
//  Rendu d'une grille de population (mini-vues)
// =============================================================
export class GridRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.cells = []; // [{state, genome}]
    this.dt = 0.02;
  }

  setGenomes(genomes) {
    this.cells = genomes.map((item) => {
      const genome = item && item.genome ? item.genome : item;
      const label = item && item.label ? item.label : null;
      const fitness = item && typeof item.fitness === 'number' ? item.fitness : null;
      return {
        genome,
        label,
        fitness,
        state: buildState(genome),
      };
    });
  }

  step(speed = 1) {
    const sub = Math.max(1, Math.floor(speed));
    for (const c of this.cells) {
      for (let k = 0; k < sub; k++) step(c.state, this.dt);
    }
  }

  draw() {
    const ctx = this.ctx;
    const W = this.canvas.width, H = this.canvas.height;
    ctx.fillStyle = '#04101c';
    ctx.fillRect(0, 0, W, H);
    if (!this.cells.length) return;

    const cols = Math.ceil(Math.sqrt(this.cells.length));
    const rows = Math.ceil(this.cells.length / cols);
    const cw = W / cols, ch = H / rows;

    for (let idx = 0; idx < this.cells.length; idx++) {
      const r = Math.floor(idx / cols), col = idx % cols;
      const x0 = col * cw, y0 = r * ch;
      this.drawCell(this.cells[idx], x0, y0, cw, ch, idx);
    }
  }

  drawCell(cell, x0, y0, w, h, rank) {
    const ctx = this.ctx;
    // cadre selon rang
    const hue = 180 - Math.min(rank, 30) * 4;
    ctx.strokeStyle = `hsla(${hue},70%,60%,0.5)`;
    ctx.lineWidth = 1;
    ctx.strokeRect(x0 + 0.5, y0 + 0.5, w - 1, h - 1);

    const s = cell.state;
    // bbox
    let minx = Infinity, miny = Infinity, maxx = -Infinity, maxy = -Infinity;
    for (let i = 0; i < s.N; i++) {
      if (s.px[i] < minx) minx = s.px[i];
      if (s.px[i] > maxx) maxx = s.px[i];
      if (s.py[i] < miny) miny = s.py[i];
      if (s.py[i] > maxy) maxy = s.py[i];
    }
    const bw = maxx - minx + 1, bh = maxy - miny + 1;
    const sc = 0.7 * Math.min(w / bw, h / bh);
    const cx = (minx + maxx) / 2, cy = (miny + maxy) / 2;
    const toS = (px, py) => [
      x0 + w / 2 + (px - cx) * sc,
      y0 + h / 2 + (py - cy) * sc,
    ];

    ctx.lineWidth = 1.5;
    ctx.strokeStyle = '#7fc8ff';
    for (const L of s.links) {
      const [x1, y1] = toS(s.px[L.i], s.py[L.i]);
      const [x2, y2] = toS(s.px[L.j], s.py[L.j]);
      ctx.beginPath();
      ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
      ctx.stroke();
    }
    ctx.fillStyle = '#ffe070';
    for (let i = 0; i < s.N; i++) {
      const [x, y] = toS(s.px[i], s.py[i]);
      ctx.beginPath();
      ctx.arc(x, y, 1.6, 0, Math.PI * 2);
      ctx.fill();
    }
    // rang
    ctx.fillStyle = 'rgba(255,255,255,0.75)';
    ctx.font = '10px ui-monospace,monospace';
    ctx.fillText(cell.label || `#${rank + 1}`, x0 + 4, y0 + 12);
    if (cell.fitness !== null) {
      ctx.fillStyle = 'rgba(255,210,130,0.92)';
      ctx.fillText(cell.fitness.toFixed(3), x0 + 4, y0 + h - 5);
    }
  }
}

// =============================================================
//  Petit graphe de fitness
// =============================================================
export class FitnessChart {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.history = [];
  }
  setHistory(h) { this.history = h; }
  draw() {
    const ctx = this.ctx;
    const W = this.canvas.width, H = this.canvas.height;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#0a1620';
    ctx.fillRect(0, 0, W, H);
    if (this.history.length < 2) return;
    let mx = 0;
    for (const p of this.history) mx = Math.max(mx, p.best);
    if (mx <= 0) mx = 1;
    const pad = 24;
    const xMap = i => pad + (W - 2 * pad) * (i / Math.max(1, this.history.length - 1));
    const yMap = v => H - pad - (H - 2 * pad) * (v / mx);

    // axes
    ctx.strokeStyle = '#23384a';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pad, pad); ctx.lineTo(pad, H - pad); ctx.lineTo(W - pad, H - pad);
    ctx.stroke();

    // mean
    ctx.strokeStyle = '#88aabb';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    this.history.forEach((p, i) => {
      const x = xMap(i), y = yMap(p.mean);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    });
    ctx.stroke();

    // best
    ctx.strokeStyle = '#ffae5e';
    ctx.lineWidth = 2;
    ctx.beginPath();
    this.history.forEach((p, i) => {
      const x = xMap(i), y = yMap(p.best);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    });
    ctx.stroke();

    ctx.fillStyle = '#ffae5e';
    ctx.font = '11px ui-monospace,monospace';
    ctx.fillText(`best=${this.history[this.history.length - 1].best.toFixed(3)}`, pad + 4, pad + 12);
    ctx.fillStyle = '#88aabb';
    ctx.fillText(`mean=${this.history[this.history.length - 1].mean.toFixed(3)}`, pad + 4, pad + 26);
  }
}
