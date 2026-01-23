#!/usr/bin/env python
"""Workspace management script for SDLC Pod.

Usage:
    uv run wks start    - Start the pod and port forwarding
    uv run wks stop     - Stop port forwarding and the pod
    uv run wks status   - Show pod status
    uv run wks forward  - Start port forwarding only (if pod is running)
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from kubernetes import client, config

DEPLOYMENT_NAME = "sdlc-pod"
SERVICE_NAME = "sdlc-service"
NAMESPACE = "default"
PID_FILE = Path("/tmp/sdlc-port-forward.pid")

PORTS = [
    (8080, "PenPot"),
    (8081, "SysON"),
    (8083, "OpenCode"),
    (8084, "VS Code"),
    (8085, "Web Terminal"),
]


def get_kube_clients():
    """Initialize and return Kubernetes API clients."""
    config.load_kube_config()
    return client.CoreV1Api(), client.AppsV1Api()


def scale_deployment(apps_v1, replicas):
    """Scale the deployment to the specified number of replicas."""
    body = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment_scale(DEPLOYMENT_NAME, NAMESPACE, body)


def wait_for_pod_ready(v1, timeout=300):
    """Wait for the pod to be ready."""
    print("Waiting for pod to be ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        pods = v1.list_namespaced_pod(
            namespace=NAMESPACE, label_selector=f"app={DEPLOYMENT_NAME}"
        )
        if pods.items:
            pod = pods.items[0]
            if pod.status.phase == "Running":
                statuses = pod.status.container_statuses or []
                if statuses and all(cs.ready for cs in statuses):
                    print(f"Pod {pod.metadata.name} is ready")
                    return True
        time.sleep(2)
    print("Timeout waiting for pod to be ready")
    return False


def wait_for_pod_terminated(v1, timeout=60):
    """Wait for the pod to be terminated."""
    print("Waiting for pod to terminate...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        pods = v1.list_namespaced_pod(
            namespace=NAMESPACE, label_selector=f"app={DEPLOYMENT_NAME}"
        )
        if not pods.items:
            print("Pod terminated")
            return True
        time.sleep(2)
    print("Timeout waiting for pod to terminate")
    return False


def find_kubectl():
    """Find kubectl executable path."""
    # Check common locations
    paths_to_check = [
        "kubectl",
        os.path.expanduser("~/bin/kubectl"),
        "/usr/local/bin/kubectl",
        "/usr/bin/kubectl",
        os.path.expanduser("~/.local/bin/kubectl"),
    ]

    # Also check if minikube kubectl works
    for path in paths_to_check:
        try:
            result = subprocess.run(
                [path, "version", "--client"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                return path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    # Try minikube kubectl
    try:
        result = subprocess.run(
            ["minikube", "kubectl", "--", "version", "--client"],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            return "minikube kubectl --"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def start_port_forwarding():
    """Start port forwarding for all services."""
    kubectl = find_kubectl()
    if not kubectl:
        print("Warning: kubectl not found in PATH.")
        print("To enable port forwarding, ensure kubectl is available.")
        print(
            "Manual command: kubectl port-forward svc/sdlc-service 8080:8080 8081:8081 8083:8083 8084:8084 8085:8085"
        )
        return None

    port_args = " ".join(f"{p}:{p}" for p, _ in PORTS)

    if kubectl.startswith("minikube"):
        cmd = f"minikube kubectl -- port-forward svc/{SERVICE_NAME} {port_args}"
    else:
        cmd = f"{kubectl} port-forward svc/{SERVICE_NAME} {port_args}"

    print("Starting port forwarding...")
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )

    # Save PID for later cleanup
    PID_FILE.write_text(str(process.pid))

    # Wait a moment and check if process is still running
    time.sleep(2)
    if process.poll() is not None:
        print("Warning: Port forwarding process exited unexpectedly")
        PID_FILE.unlink(missing_ok=True)
        return None

    print(f"Port forwarding started (PID: {process.pid})")
    return process.pid


def stop_port_forwarding():
    """Stop port forwarding if running."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            # Kill the process group
            os.killpg(pid, signal.SIGTERM)
            print(f"Port forwarding stopped (PID: {pid})")
        except (ProcessLookupError, ValueError, PermissionError):
            pass
        finally:
            PID_FILE.unlink(missing_ok=True)


def is_port_forwarding_running():
    """Check if port forwarding is running."""
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)  # Check if process exists
        return True
    except (ProcessLookupError, ValueError, PermissionError):
        PID_FILE.unlink(missing_ok=True)
        return False


def get_pod_status(v1, apps_v1):
    """Get detailed pod status."""
    # Get deployment info
    try:
        deployment = apps_v1.read_namespaced_deployment(DEPLOYMENT_NAME, NAMESPACE)
        replicas = deployment.spec.replicas
    except client.ApiException:
        return None, None, None

    if replicas == 0:
        return "Stopped", None, None

    # Get pod info
    pods = v1.list_namespaced_pod(
        namespace=NAMESPACE, label_selector=f"app={DEPLOYMENT_NAME}"
    )
    if not pods.items:
        return "Starting", None, None

    pod = pods.items[0]
    containers = {}
    for cs in pod.status.container_statuses or []:
        containers[cs.name] = {
            "ready": cs.ready,
            "restarts": cs.restart_count,
        }

    all_ready = all(c["ready"] for c in containers.values())
    status = "Running" if all_ready else "Starting"

    return status, pod.metadata.name, containers


def cmd_start():
    """Start the pod and port forwarding."""
    print("Starting SDLC Pod...")
    v1, apps_v1 = get_kube_clients()

    # Scale up
    scale_deployment(apps_v1, 1)

    # Wait for pod to be ready
    if not wait_for_pod_ready(v1):
        print("Failed to start pod")
        return 1

    # Start port forwarding
    start_port_forwarding()

    print()
    print("SDLC Pod is running. Access tools at:")
    for port, name in PORTS:
        print(f"  {name}: http://localhost:{port}")

    return 0


def cmd_stop():
    """Stop port forwarding and the pod."""
    print("Stopping SDLC Pod...")

    # Stop port forwarding first
    stop_port_forwarding()

    # Scale down
    v1, apps_v1 = get_kube_clients()
    scale_deployment(apps_v1, 0)

    # Wait for pod to terminate
    wait_for_pod_terminated(v1)

    print("SDLC Pod stopped")
    return 0


def cmd_status():
    """Show pod status."""
    v1, apps_v1 = get_kube_clients()

    status, pod_name, containers = get_pod_status(v1, apps_v1)

    if status is None:
        print("Deployment not found")
        return 1

    print(f"Pod Status: {status}")

    if pod_name and containers:
        print(f"Pod Name: {pod_name}")
        print()
        print("Containers:")
        for name, info in sorted(containers.items()):
            ready_str = "✓" if info["ready"] else "✗"
            print(f"  {ready_str} {name} (restarts: {info['restarts']})")

    print()
    pf_running = is_port_forwarding_running()
    print(f"Port Forwarding: {'Running' if pf_running else 'Stopped'}")

    if status == "Running":
        print()
        print("Access tools at:")
        for port, name in PORTS:
            print(f"  {name}: http://localhost:{port}")

    return 0


def cmd_forward():
    """Start port forwarding only."""
    v1, apps_v1 = get_kube_clients()
    status, _, _ = get_pod_status(v1, apps_v1)

    if status != "Running":
        print(f"Pod is not running (status: {status})")
        print("Run 'wks start' first")
        return 1

    if is_port_forwarding_running():
        print("Port forwarding is already running")
        return 0

    pid = start_port_forwarding()
    if pid:
        print()
        print("Access tools at:")
        for port, name in PORTS:
            print(f"  {name}: http://localhost:{port}")
        return 0
    return 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1]

    commands = {
        "start": cmd_start,
        "stop": cmd_stop,
        "status": cmd_status,
        "forward": cmd_forward,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(__doc__)
        return 1

    return commands[command]()


if __name__ == "__main__":
    sys.exit(main())
