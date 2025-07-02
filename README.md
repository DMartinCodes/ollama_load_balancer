# ollama_load_balancer
A small tool which distributes Ollama prompt requests across a network of compute servers


~Under Construction!

### Features
- Control Ollama servers on multiple nodes simultaneously
- Distribute prompt queues across a distributed network
- Compatible with mesh VPNs like Tailscale


### What is this tool?
Ollama Load Balancer is a small Python-based application which automatically directs Ollama API traffic between a central server and compute nodes. It helps reduce the load on individual compute nodes in a cluster, and also allows for parallel node management.
