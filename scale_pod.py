import sys
from kubernetes import client, config


def scale_deployment(name, replicas, namespace="default"):
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()

    body = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment_scale(name, namespace, body)
    print(f"Deployment {name} scaled to {replicas}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scale_to_zero.py [up|down]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "up":
        scale_deployment("sdlc-pod", 1)
    elif action == "down":
        scale_deployment("sdlc-pod", 0)
    else:
        print("Invalid action. Use 'up' or 'down'.")
