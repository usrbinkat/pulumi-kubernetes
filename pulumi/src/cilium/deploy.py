import pulumi
import pulumi_kubernetes as k8s
from lib.helm_release_latest import get_latest as helm_release_latest

def deploy_cilium(
        k8s_provider,
        kubernetes_distribution: str,
        k8s_endpoint_ip: pulumi.Output,
    ):

    # Fetch the latest version of the Cilium Helm chart
    cilium_chart_name = "cilium"
    cilium_chart_url = "https://raw.githubusercontent.com/cilium/charts/master/index.yaml"
    cilium_latest_version = helm_release_latest.get_latest(cilium_chart_url, cilium_chart_name)

    # Statically limit the Cilium version to 1.14.7 until resolved
    cilium_latest_version = "1.14.7"

    # Determine Helm values based on the Kubernetes distribution
    helm_values = helm_release_latest(kubernetes_distribution, k8s_endpoint_ip)

    # Deploy Helm Chart for Cilium
    cilium_helm_release = k8s.helm.v3.Release(
        "cilium-release",
        chart="cilium",
        values=helm_values,
        version=cilium_latest_version,
        repository_opts={"repo": "https://helm.cilium.io/"},
        namespace="kube-system",
        opts=pulumi.ResourceOptions(
            provider=k8s_provider
        ),
        wait_for_jobs=True,
        skip_await=False,
        skip_crds=False
    )

    return cilium_helm_release

def get_helm_values(
        kubernetes_distribution: str,
        k8s_endpoint_ip: pulumi.Output
    ):

    # Common Cilium Helm Chart Values
    common_values = {
        "routingMode": "tunnel",
        "tunnelProtocol": "vxlan",
        "kubeProxyReplacement": "strict",
        "image": {"pullPolicy": "IfNotPresent"},
        "hostServices": {"enabled": False},
        "cluster": {"name": "pulumi"},
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
        # Kind Kubernetes specific Helm values
        return {
            **common_values,
            "k8sServiceHost": k8s_endpoint_ip,
            "k8sServicePort": 6443,
        }
    elif kubernetes_distribution == 'talos':
        # Talos Kubernetes specific Helm values
        return {
            **common_values,
            "cgroup": {
                "autoMount": {"enabled": False},
                "hostRoot": "/sys/fs/cgroup",
            },
            "k8sServicePort": 7445,
            "k8sServiceHost": "localhost",
            "cni": { "install": True},
            "securityContext": {
                "capabilities": {
                    "ciliumAgent": ["CHOWN", "KILL", "NET_ADMIN", "NET_RAW", "IPC_LOCK", "SYS_ADMIN", "SYS_RESOURCE", "DAC_OVERRIDE", "FOWNER", "SETGID", "SETUID"],
                    "cleanCiliumState": ["NET_ADMIN", "SYS_ADMIN", "SYS_RESOURCE"]
                },
            },
        }
    else:
        raise ValueError(f"Unsupported Kubernetes distribution: {kubernetes_distribution}")
