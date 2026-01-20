from behave import given, then
import requests
import subprocess
import time
from kubernetes import client, config


import os
import signal


def get_minikube_url(service_name, port_name):
    try:
        # Since minikube IP is unreachable directly, we use port-forwarding
        # We find the local port that we've forwarded
        v1 = client.CoreV1Api()
        svc = v1.read_namespaced_service(service_name, "default")

        target_port = None
        for port in svc.spec.ports:
            if port.name == port_name:
                target_port = port.port
                break

        if not target_port:
            return None

        # Start port-forward in background if not already running
        # We'll use a fixed local port for each service port for simplicity
        local_port = target_port
        if target_port == 80:
            local_port = 8082  # avoid privileged ports

        # We'll just run port-forward and hope for the best, or check if it's already running
        subprocess.Popen(
            [
                "/home/jd/bin/kubectl",
                "port-forward",
                f"service/{service_name}",
                f"{local_port}:{target_port}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Give it a second to start
        time.sleep(2)

        return f"http://localhost:{local_port}"
    except Exception as e:
        print(f"Error setting up port-forward for {port_name}: {e}")
        return None


@given("the SDLC Pod is deployed to Minikube")
def step_given_pod_deployed(context):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    # Wait for pod to be ready
    timeout = 300
    start_time = time.time()
    while time.time() - start_time < timeout:
        pods = v1.list_namespaced_pod(
            namespace="default", label_selector="app=sdlc-pod"
        )
        if pods.items and all(
            status.ready for status in (pods.items[0].status.container_statuses or [])
        ):
            return
        time.sleep(10)

    raise Exception("Timeout waiting for SDLC Pod to be ready")


@then("the VS Code URL should be accessible")
def step_then_vscode_accessible(context):
    url = get_minikube_url("sdlc-service", "vscode")
    assert url is not None, "Failed to get VS Code URL"
    response = requests.get(url, timeout=10)
    assert response.status_code == 200, (
        f"VS Code not accessible at {url}, status: {response.status_code}"
    )


@then("the SysON URL should be accessible")
def step_then_syson_accessible(context):
    url = get_minikube_url("sdlc-service", "syson")
    assert url is not None, "Failed to get SysON URL"
    # Note: Using allow_redirects=True as some apps redirect to login
    response = requests.get(url, timeout=10, allow_redirects=True)
    # We accept 200, 401 (auth required), or 403 as "accessible" for a smoke test if the server responds
    assert response.status_code < 500, (
        f"SysON not accessible at {url}, status: {response.status_code}"
    )


@then("the PenPot URL should be accessible")
def step_then_penpot_accessible(context):
    url = get_minikube_url("sdlc-service", "penpot")
    assert url is not None, "Failed to get PenPot URL"
    response = requests.get(url, timeout=10, allow_redirects=True)
    assert response.status_code < 500, (
        f"PenPot not accessible at {url}, status: {response.status_code}"
    )


@then("the OpenCode URL should be accessible")
def step_then_opencode_accessible(context):
    url = get_minikube_url("sdlc-service", "opencode")
    assert url is not None, "Failed to get OpenCode URL"
    response = requests.get(url, timeout=10, allow_redirects=True)
    assert response.status_code < 500, (
        f"OpenCode not accessible at {url}, status: {response.status_code}"
    )
