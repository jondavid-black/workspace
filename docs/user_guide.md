# SDLC Pod User Guide

This project provides a Kubernetes Pod containing a suite of containers to support the software development lifecycle.

## Included Tools

- **Systems Engineering:** SysON (Placeholder in prototype)
- **User Experience:** PenPot
- **Software Development:** VS Code (code-server)
- **Integration UI:** OpenCode (Placeholder in prototype)

## Prerequisites

- Minikube
- kubectl
- Python with `uv`

## Deployment

1. Start Minikube:
   ```bash
   minikube start
   ```

2. Apply the Kubernetes manifests:
   ```bash
   kubectl apply -f k8s/pvc.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

3. Wait for the pod to be ready:
   ```bash
   kubectl wait --for=condition=ready pod -l app=sdlc-pod --timeout=300s
   ```

## Accessing the Tools

Since the pod is running in Minikube, you can use port-forwarding to access the tools locally:

- **VS Code:** `kubectl port-forward svc/sdlc-service 8084:8084` -> [http://localhost:8084](http://localhost:8084)
- **SysON:** `kubectl port-forward svc/sdlc-service 8081:8081` -> [http://localhost:8081](http://localhost:8081)
- **PenPot:** `kubectl port-forward svc/sdlc-service 8080:8080` -> [http://localhost:8080](http://localhost:8080)
- **OpenCode:** `kubectl port-forward svc/sdlc-service 8083:8083` -> [http://localhost:8083](http://localhost:8083)

## Scaling to Zero

To save resources when not in use, you can scale the pod to zero:

```bash
uv run python scale_pod.py down
```

To bring it back up:

```bash
uv run python scale_pod.py up
```

## Running Tests

To verify the deployment:

```bash
uv run behave
```
