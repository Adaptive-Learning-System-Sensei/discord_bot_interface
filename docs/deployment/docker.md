# Infrastructure & Deployment

The application runs seamlessly across virtual infrastructure environments through native **Docker** abstraction.

## Local Container Bootstrapping

Build and launch the background tasks alongside web keep-alive endpoints:

```bash
docker compose up --build -d
```

### Configuration Mapping
* **`Dockerfile`**: Minimal footprint Python container runtime layer.
* **`compose.yaml`**: Multi-tiered environment variable and volume definitions preserving state and `app.log` persistence safely across host processes.
