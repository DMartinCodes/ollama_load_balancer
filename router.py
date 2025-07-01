import httpx
import asyncio
import yaml
import time
from itertools import cycle
from fastapi import Request
from starlette.responses import Response



#config.yaml is loaded when the router starts, make sure your config file is in the same dir as router.py
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)



OLLAMA_NODES = config["ollama_nodes"]
node_pool = cycle(OLLAMA_NODES)
semaphore = asyncio.Semaphore(len(OLLAMA_NODES))

#logging tools for console readouts
request_counts = {node: 0 for node in OLLAMA_NODES}
latency_sums = {node: 0.0 for node in OLLAMA_NODES}
global_request_counter = 0
SUMMARY_EVERY = 10  


async def forward_generic_request(request: Request, path: str) -> Response:
    global global_request_counter

    method = request.method
    headers = dict(request.headers)
    body = await request.body()
    url_path = f"/api/{path}"

    print(f"\n=== Incoming Request #{global_request_counter + 1} ===")
    print(f"Method: {method}")
    print(f"Path: /api/{path}")
    print(f"Headers: {headers}")
    print(f"Body (truncated): {body[:200]}")
    print(f"========================")
    
    for attempt in range(len(OLLAMA_NODES)):
        node = next(node_pool)
        target_url = f"{node}{url_path}"
        print(f"[Attempt {attempt + 1}] Forwarding to: {target_url}")

        try:
            start = time.perf_counter()
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.request(
                    method=method,
                    url=target_url,
                    headers=headers,
                    content=body
                )
            elapsed = (time.perf_counter() - start) * 1000  # ms

            print(f"[SUCCESS] Node: {node} | Status: {response.status_code} | Latency: {elapsed:.2f}ms")

            request_counts[node] += 1
            latency_sums[node] += elapsed
            global_request_counter += 1

            if global_request_counter % SUMMARY_EVERY == 0:
                print_summary()

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )

        except httpx.RequestError as e:
            print(f"[ERROR] Failed to connect to {node}: {e}")
            continue

    print("[FATAL] All nodes failed to respond.")
    return Response(content=b"All Ollama nodes are unavailable.", status_code=502)


def print_summary():
    print("\n === Load Balancer Summary ===")
    for node in OLLAMA_NODES:
        count = request_counts[node]
        avg_latency = (latency_sums[node] / count) if count else 0
        print(f"{node} | Requests: {count} | Avg Latency: {avg_latency:.2f}ms")
    print("================================\n")
