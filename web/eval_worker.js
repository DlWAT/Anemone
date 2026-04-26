// eval_worker.js — evaluation physique d'un batch de genomes
import { buildState, step, evaluate } from './physics.js';

function evalGenome(genome, steps, dt) {
  const s = buildState(genome);
  for (let i = 0; i < steps; i++) step(s, dt);
  return evaluate(s);
}

onmessage = (e) => {
  const msg = e.data || {};
  if (msg.type !== 'eval_batch') return;
  const jobs = Array.isArray(msg.jobs) ? msg.jobs : [];
  const steps = Math.max(1, Math.floor(msg.steps || 1));
  const dt = Number(msg.dt) || 0.02;
  const results = new Array(jobs.length);

  for (let i = 0; i < jobs.length; i++) {
    const job = jobs[i];
    results[i] = {
      idx: job.idx,
      fitness: evalGenome(job.genome, steps, dt),
    };
  }

  postMessage({ type: 'eval_batch_done', reqId: msg.reqId, results });
};
