# SDLC Pod Design Documentation

## Architecture Overview

The SDLC Pod is a Kubernetes-based development environment designed to support a single user with a suite of integrated tools.

### Components

- **VS Code (code-server):** Provides a web-based IDE for software development, configured to open the `/workspace` directory by default.
- **SysON:** Supports SysML v2 engineering baseline development.
- **PenPot:** An open-source design and prototyping platform.
- **OpenCode:** A unified interface for the SDLC toolset, serving the project context from `/workspace`.
- **Collabora CODE:** Provides web-based office document editing, integrated with the shared storage.
- **Web Terminal (ttyd):** Provides a web-based command-line interface for shell access, with the working directory set to `/workspace`.
- **Shared Persistent Storage:** A common PersistentVolumeClaim (PVC) mounted by all containers to share code and design assets. All development-focused containers are configured to launch within the shared project directory context.

## Systems Engineering Baseline

The system is defined using SysML v2 in `mbse/sdlc_pod.sysml`. This model captures the core requirements and the logical decomposition of the pod into its constituent parts and their shared storage connections.

## Kubernetes Design

### Pod Structure

All containers run within a single Kubernetes Pod to ensure they share the same network namespace and can easily access the shared volume.

- **Storage:** A 10Gi PVC `sdlc-shared-data` is used for persistent storage.
- **Networking:** Each container is assigned a unique port within the pod. A NodePort Service `sdlc-service` exposes these ports to the outside world. All containers are configured to bind to `0.0.0.0` to ensure accessibility via the pod IP when using port-forwarding or ingress.

### Scale to Zero

Scale-to-zero is implemented via a Python control script `scale_pod.py` that interacts with the Kubernetes API to adjust the deployment's replica count. This allows the entire suite to be shut down when not in use, conserving cluster resources.

## Verification Strategy

Automated verification is performed using the **Behave** BDD framework. Smoke tests verify the accessibility of each tool's web interface. To handle the networking complexities of Minikube in a nested environment, the test steps dynamically manage `kubectl port-forward` processes.

## Future Enhancements

- **Knative Integration:** For more seamless scale-to-zero based on traffic.
- **Authentication:** Unified SSO for all tools.
- **Resource Limits:** Fine-tuned CPU and memory limits for each container.
