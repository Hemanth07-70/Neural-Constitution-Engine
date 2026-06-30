#!/usr/bin/env python3
"""Phase 11: Performance benchmark – sequential and concurrent requests."""
import asyncio
import statistics
import time

import httpx

BASE = "http://127.0.0.1:8000"


async def single_request(client: httpx.AsyncClient) -> float:
    """Benchmark /health (fast, public, exercises full ASGI stack)."""
    start = time.perf_counter()
    r = await client.get(f"{BASE}/health")
    elapsed = (time.perf_counter() - start) * 1000  # ms
    r.raise_for_status()
    return elapsed


async def single_validate(client: httpx.AsyncClient) -> float:
    """Benchmark /validate with a real constitution file (exercises Engine)."""
    import io

    with open("examples/constitution.yaml", "rb") as f:
        data = f.read()
    start = time.perf_counter()
    r = await client.post(
        f"{BASE}/validate",
        files={"file": ("c.yaml", io.BytesIO(data), "application/x-yaml")},
    )
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed


async def run_sequential(n: int) -> list[float]:
    latencies = []
    async with httpx.AsyncClient(timeout=30) as client:
        for _ in range(n):
            latencies.append(await single_request(client))
    return latencies


async def run_concurrent(n: int) -> list[float]:
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [single_request(client) for _ in range(n)]
        return await asyncio.gather(*tasks)


def stats(latencies: list[float], label: str):
    s = sorted(latencies)
    print(f"\n  {label}:")
    print(f"    Count:      {len(s)}")
    print(f"    Min:        {min(s):.1f} ms")
    print(f"    p50:        {s[len(s)//2]:.1f} ms")
    print(f"    p95:        {s[int(len(s)*0.95)]:.1f} ms")
    print(f"    p99:        {s[int(len(s)*0.99)]:.1f} ms")
    print(f"    Max:        {max(s):.1f} ms")
    print(f"    Mean:       {statistics.mean(s):.1f} ms")
    total_s = sum(s) / 1000
    print(f"    Throughput: {len(s)/total_s:.1f} req/s (wall-clock total {total_s:.2f}s)")


async def main():
    print("=== Phase 11 – Performance Benchmark ===")

    # Warm up
    await run_sequential(5)
    print("  Warm-up complete (5 requests)")

    # 100 sequential
    print("\n  Running 100 sequential requests...")
    seq100 = await run_sequential(100)
    stats(seq100, "100 Sequential")

    # 50 concurrent
    print("\n  Running 50 concurrent requests...")
    conc50 = await run_concurrent(50)
    stats(conc50, "50 Concurrent")

    # 100 concurrent
    print("\n  Running 100 concurrent requests...")
    conc100 = await run_concurrent(100)
    stats(conc100, "100 Concurrent")

    print("\n  Running 20 concurrent /validate (Engine load) requests...")
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = [single_validate(client) for _ in range(20)]
        t0 = time.perf_counter()
        val_latencies = await asyncio.gather(*tasks)
        wall = time.perf_counter() - t0
    sv = sorted(val_latencies)
    print("\n  20 Concurrent /validate (Engine):")
    print(f"    p50:        {sv[len(sv)//2]:.1f} ms")
    print(f"    p99:        {sv[int(len(sv)*0.99)]:.1f} ms")
    print(f"    Wall time:  {wall*1000:.1f} ms")
    print(f"    Throughput: {20/wall:.1f} req/s")

    print("\n  ✅ Benchmark complete — see metrics above (relative mode, no hard SLA)")


asyncio.run(main())
