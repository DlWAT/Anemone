// editor.js — éditeur manuel de créature, sur le canvas principal
// Modes : "point" (ajouter), "link" (relier 2 points), "muscle" (3 points), "move" (déplacer)
export class Editor {
  constructor(canvas, renderer, onChange) {
    this.canvas = canvas;
    this.renderer = renderer;
    this.onChange = onChange;
    this.mode = 'off';
    this.pending = [];
    this.dragging = -1;
    canvas.addEventListener('mousedown', e => this.onMouseDown(e));
    canvas.addEventListener('mousemove', e => this.onMouseMove(e));
    canvas.addEventListener('mouseup',   e => this.onMouseUp(e));
  }

  setMode(m) {
    this.mode = m;
    this.pending = [];
  }

  screenToWorld(sx, sy) {
    const rect = this.canvas.getBoundingClientRect();
    const x = sx - rect.left, y = sy - rect.top;
    const W = this.canvas.width, H = this.canvas.height;
    return [
      (x - W / 2) / this.renderer.scale + this.renderer.cam[0],
      (y - H / 2) / this.renderer.scale + this.renderer.cam[1],
    ];
  }

  pickPoint(wx, wy) {
    const g = this.renderer.genome;
    if (!g) return -1;
    const r = 0.6;
    let best = -1, bd = r * r;
    for (let i = 0; i < g.points.length; i++) {
      const dx = g.points[i][0] - wx, dy = g.points[i][1] - wy;
      const d2 = dx * dx + dy * dy;
      if (d2 < bd) { bd = d2; best = i; }
    }
    return best;
  }

  onMouseDown(e) {
    if (this.mode === 'off') return;
    const [wx, wy] = this.screenToWorld(e.clientX, e.clientY);
    const g = this.renderer.genome;
    if (!g) return;

    if (this.mode === 'point') {
      g.points.push([wx, wy]);
      this.commit();
    } else if (this.mode === 'move') {
      const i = this.pickPoint(wx, wy);
      if (i >= 0) this.dragging = i;
    } else if (this.mode === 'link') {
      const i = this.pickPoint(wx, wy);
      if (i >= 0) {
        this.pending.push(i);
        if (this.pending.length === 2) {
          const [a, b] = this.pending;
          if (a !== b) {
            const lo = Math.min(a, b), hi = Math.max(a, b);
            if (!g.links.some(([x, y]) => x === lo && y === hi)) {
              g.links.push([lo, hi]);
              this.commit();
            }
          }
          this.pending = [];
        }
      }
    } else if (this.mode === 'muscle') {
      const i = this.pickPoint(wx, wy);
      if (i >= 0) {
        this.pending.push(i);
        if (this.pending.length === 3) {
          const [p0, p1, p2] = this.pending;
          if (new Set([p0, p1, p2]).size === 3) {
            g.muscles.push({
              p0, p1, p2,
              freqs: [1.0], amps: [0.6], phases: [0],
              base: 90, intensite: 10,
            });
            this.commit();
          }
          this.pending = [];
        }
      }
    } else if (this.mode === 'delete') {
      const i = this.pickPoint(wx, wy);
      if (i >= 0) {
        g.points.splice(i, 1);
        // réindexation
        const fix = k => k > i ? k - 1 : k;
        g.links = g.links.filter(([a, b]) => a !== i && b !== i)
          .map(([a, b]) => [fix(a), fix(b)]);
        g.muscles = g.muscles.filter(m => m.p0 !== i && m.p1 !== i && m.p2 !== i)
          .map(m => ({ ...m, p0: fix(m.p0), p1: fix(m.p1), p2: fix(m.p2) }));
        this.commit();
      }
    }
  }

  onMouseMove(e) {
    if (this.dragging < 0) return;
    const [wx, wy] = this.screenToWorld(e.clientX, e.clientY);
    this.renderer.genome.points[this.dragging] = [wx, wy];
    this.commit(false);
  }

  onMouseUp() {
    if (this.dragging >= 0) {
      this.dragging = -1;
      this.commit();
    }
  }

  commit(rebuild = true) {
    if (rebuild) this.renderer.setGenome(this.renderer.genome);
    if (this.onChange) this.onChange(this.renderer.genome);
  }
}
