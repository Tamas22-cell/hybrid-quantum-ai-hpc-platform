export const metadata = {
  title: "Hybrid Quantum–AI HPC Platform | Public Showcase",
  description: "Public project overview and documented cloud benchmark results for a CPU and quantum simulation platform."
};

const results = [
  ["CPU matrix", "0.735 ms", "256 × 256 NumPy workload"],
  ["CPU throughput", "45.634 GFLOPS", "Estimated from measured compute time"],
  ["Quantum simulator", "0.241 ms", "4-qubit Qiskit GHZ circuit"],
  ["GHZ fidelity", "≈ 1.000", "Simulator result"]
];

export default function Showcase() {
  return (
    <main>
      <header>
        <small>RESEARCH PROJECT · PUBLIC SHOWCASE</small>
        <h1>Hybrid Quantum–AI HPC Platform</h1>
        <p>An engineering project exploring workload orchestration across CPU, GPU and quantum simulation backends.</p>
        <p>
          <a href="https://github.com/Tamas22-cell/hybrid-quantum-ai-hpc-platform" style={{color:"#93c5fd",marginRight:20}}>View source on GitHub →</a>
          <a href="https://github.com/Tamas22-cell/hybrid-quantum-ai-hpc-platform/releases/tag/v12.0.0-rc.1" style={{color:"#93c5fd"}}>Research release notes →</a>
        </p>
      </header>

      <section>
        <h2>Verified cloud measurements</h2>
        <p>Recorded on November 15, 2026. These are separate workloads and do not represent a CPU-versus-quantum speedup comparison.</p>
        <div className="metrics">
          {results.map(([name, value, note]) => (
            <article key={name} style={{background:"#0b1120",border:"1px solid #29374f",borderRadius:12,padding:18}}>
              <small>{name}</small>
              <h2 style={{marginTop:10}}>{value}</h2>
              <small>{note}</small>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2>What is in the project</h2>
        <div className="metrics">
          <p><strong>Compute engines</strong><br/>NumPy CPU baseline, optional GPU paths, Qiskit and CUDA-Q simulation, plus hybrid algorithm experiments.</p>
          <p><strong>Orchestration</strong><br/>A rule-based scheduler, queue-backed API, Redis/RQ workers and PostgreSQL result history.</p>
          <p><strong>Measurement</strong><br/>Repeated timings, numerical checks and benchmark exports, with documented limits on comparisons.</p>
          <p><strong>Web control center</strong><br/>Next.js dashboard for workload submission, status polling, result history and CSV/JSON export.</p>
        </div>
      </section>

      <section>
        <h2>Architecture</h2>
        <p>Next.js dashboard → FastAPI → Redis/RQ → worker → PostgreSQL</p>
        <p>The public showcase is read-only. The operator dashboard and workload API remain authenticated to protect compute services.</p>
      </section>

      <section>
        <h2>Research limits</h2>
        <ul>
          <li>Qiskit and CUDA-Q results are simulator measurements; no physical QPU execution is claimed.</li>
          <li>Cloud GPU and multi-node execution have not been validated.</li>
          <li>Small simulator timings do not demonstrate quantum advantage.</li>
        </ul>
      </section>

      <footer>
        <p>Open source · Python · Next.js · FastAPI · Redis/RQ · PostgreSQL · Vercel</p>
      </footer>
    </main>
  );
}
