import pulumi
import pulumi_kubernetes as k8s
from lib.helm_release_latest import get_latest as helm_get_latest

def deploy_cilium(
        ns: str,
        version: str,
        kubernetes_endpoint: pulumi.Output,
        kubernetes_distribution: str,
        kubernetes_provider: k8s.Provider
    ):

    # Check if version is set
    chart_name = "cilium"
    chart_index_url = "https://raw.githubusercontent.com/cilium/charts/master/index.yaml"
    if version is None:
        # Fetch the latest version of the Cilium Helm chart
        version = helm_get_latest(chart_index_url, chart_name)

        # Statically limit the Cilium version to 1.14.7 until resolved
        version = "1.14.7"

    # Assemble Helm Values
    helm_values = get_helm_values(kubernetes_distribution, kubernetes_endpoint)

    # Deploy Helm Chart for Cilium
    helm_release = k8s.helm.v3.Release(
        "cilium-release",
        chart="cilium",
        values=helm_values,
        version=version,
        repository_opts={"repo": "https://helm.cilium.io/"},
        namespace=ns,
        opts=pulumi.ResourceOptions(
            provider=kubernetes_provider
        ),
        wait_for_jobs=True,
        skip_await=False,
        skip_crds=False
    )

    return (version, helm_release)

def get_helm_values(
        kubernetes_distribution: str,
        kubernetes_endpoint: pulumi.Output
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
            "k8sServiceHost": kubernetes_endpoint,
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
