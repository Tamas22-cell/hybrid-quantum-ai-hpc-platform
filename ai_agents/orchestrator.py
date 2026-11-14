from scheduler.policy import candidates

def execute(kind, size, gpu=False, distributed=False, handlers=None):
    if handlers is None:
        from cpu_engine.core import benchmark as cpu
        from gpu_engine.core import benchmark as cuda
        from quantum_engine.core import benchmark as quantum
        def ray_run(n):
            from distributed_engine.core import benchmark
            return benchmark(n)
        handlers = {"cpu":cpu,"gpu":cuda,"ray":ray_run,"quantum_simulator":quantum}
    attempts=[]
    for backend in candidates(kind,size,gpu,distributed):
        try:
            result=handlers[backend](size)
        except (RuntimeError, ImportError, OSError) as exc:
            attempts.append({"backend":backend,"status":"failed","error":type(exc).__name__})
            continue
        attempts.append({"backend":backend,"status":"success"})
        return {"selected":backend,"attempts":attempts,"result":result}
    raise RuntimeError("No available backend")
