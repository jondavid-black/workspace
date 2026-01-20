from behave import given, then
import requests
import subprocess
import time
import socket
from kubernetes import client, config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def get_session():
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_minikube_url(service_name, port_name):
    try:
        v1 = client.CoreV1Api()
        svc = v1.read_namespaced_service(service_name, "default")

        target_port = None
        for port in svc.spec.ports:
            if port.name == port_name:
                target_port = port.port
                break

        if not target_port:
            print(f"Port {port_name} not found in service {service_name}")
            return None

        local_port = target_port
        if target_port == 80:
            local_port = 8082

        if not is_port_open(local_port):
            print(
                f"Starting port-forward for {port_name} on local port {local_port}..."
            )
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
            # Wait for port to open
            for _ in range(10):
                if is_port_open(local_port):
                    break
                time.sleep(1)

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
        time.sleep(5)

    raise Exception("Timeout waiting for SDLC Pod to be ready")


@then("the VS Code URL should be accessible")
def step_then_vscode_accessible(context):
    url = get_minikube_url("sdlc-service", "vscode")
    assert url is not None, "Failed to get VS Code URL"
    session = get_session()
    response = session.get(url, timeout=15)
    assert response.status_code == 200, (
        f"VS Code not accessible at {url}, status: {response.status_code}"
    )


@then("the SysON URL should be accessible")
def step_then_syson_accessible(context):
    url = get_minikube_url("sdlc-service", "syson")
    assert url is not None, "Failed to get SysON URL"
    session = get_session()
    # Accept 200-499 as "accessible" for smoke test
    response = session.get(url, timeout=15, allow_redirects=True)
    assert response.status_code < 500, (
        f"SysON not accessible at {url}, status: {response.status_code}"
    )


@then("the PenPot URL should be accessible")
def step_then_penpot_accessible(context):
    url = get_minikube_url("sdlc-service", "penpot")
    assert url is not None, "Failed to get PenPot URL"
    session = get_session()
    response = session.get(url, timeout=15, allow_redirects=True)
    assert response.status_code < 500, (
        f"PenPot not accessible at {url}, status: {response.status_code}"
    )


@then("the OpenCode URL should be accessible")
def step_then_opencode_accessible(context):
    url = get_minikube_url("sdlc-service", "opencode")
    assert url is not None, "Failed to get OpenCode URL"
    session = get_session()
    response = session.get(url, timeout=15, allow_redirects=True)
    assert response.status_code < 500, (
        f"OpenCode not accessible at {url}, status: {response.status_code}"
    )
