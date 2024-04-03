import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes import Provider, helm, core
from lib import helm_release_latest

def get_helm_values(kubernetes_distribution: str, k8s_endpoint_ip: pulumi.Output):
    # Cilium Helm Chart Values
    common_values = {
        "routingMode": "tunnel",
        "k8sServicePort": 6443,
        "tunnelProtocol": "vxlan",
        "k8sServiceHost": k8s_endpoint_ip,
        "kubeProxyReplacement": "strict",
        "image": {"pullPolicy": "IfNotPresent"},
        "hostServices": {"enabled": False},
        "cluster": {"name": "kind-pulumi"},
        "externalIPs": {"enabled": True},
        "gatewayAPI": {"enabled": False},
        "hubble": {
            "enabled": True,
            "relay": {"enabled": True},
            "ui": {"enabled": True},
        },
        "ipam": {"mode": "kubernetes"},
        "nodePort": {"enabled": True},
        "hostPort": {"enabled": True},
        "operator": {"replicas": 1},
        "serviceAccounts": {
            "cilium": {"name": "cilium"},
            "operator": {"name": "cilium-operator"},
        },
    }
    if kubernetes_distribution == 'kind':
        return {
            **common_values,
            "k8sServiceHost": k8s_endpoint_ip,
            "k8sServicePort": 6443,
            "kubeProxyReplacement": "strict",
            "operator": {"replicas": 1},
            "routingMode": "tunnel",
        }
    elif kubernetes_distribution == 'talos':
        # Talos-specific Helm values per the Talos Cilium Docs
        return {
            **common_values,
            "cgroup": {
                "autoMount": {"enabled": False},
                "hostRoot": "/sys/fs/cgroup",
            },
            "routingMode": "tunnel",
            "k8sServicePort": 7445,
            "tunnelProtocol": "vxlan",
            "k8sServiceHost": "localhost",
            "kubeProxyReplacement": "strict",
            "image": {"pullPolicy": "IfNotPresent"},
            "hostServices": {"enabled": False},
            "externalIPs": {"enabled": True},
            "gatewayAPI": {"enabled": False},
            "nodePort": {"enabled": True},
            "hostPort": {"enabled": True},
            "operator": {"replicas": 1},
            "cni": { "install": True},
            "securityContext": {
                "capabilities": {
                    "ciliumAgent": [
                        "CHOWN", "KILL", "NET_ADMIN", "NET_RAW", "IPC_LOCK",
                        "SYS_ADMIN", "SYS_RESOURCE", "DAC_OVERRIDE", "FOWNER",
                        "SETGID", "SETUID"
                    ],
                    "cleanCiliumState": ["NET_ADMIN", "SYS_ADMIN", "SYS_RESOURCE"],
                },
            },
        }
    else:
        raise ValueError(f"Unsupported Kubernetes distribution: {kubernetes_distribution}")
    return cilium_helm_values

def deploy_cilium(
        k8s_provider,
        kubernetes_distribution: str,
        k8s_endpoint_ip: pulumi.Output,
    ):

    # Determine Helm values based on the Kubernetes distribution
    helm_values = get_helm_values(kubernetes_distribution, k8s_endpoint_ip)

    # Fetch the latest version of the Cilium Helm chart
    cilium_chart_url = "https://raw.githubusercontent.com/cilium/charts/master/index.yaml"
    cilium_chart_name = "cilium"
    cilium_latest_version = helm_release_latest.get_latest(cilium_chart_url, cilium_chart_name)

    # Statically limit the Cilium version to 1.14.7 until resolved
    cilium_latest_version = "1.14.7"

    # Deploy Helm Chart for Cilium
    cilium_helm_release = helm.v3.Release(
        "cilium-release",
        chart="cilium",
        repository_opts={"repo": "https://helm.cilium.io/"},
        version=cilium_latest_version,
        values=helm_values,
        namespace="kube-system",
        wait_for_jobs=True,
        skip_await=False,
        skip_crds=False,
        opts=pulumi.ResourceOptions(
            provider=k8s_provider
        )
    )

    return cilium_helm_release
