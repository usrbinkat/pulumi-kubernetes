"""A Kubernetes Python Pulumi program"""
import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes import Provider, helm, core
from src.cilium.deploy import deploy as deploy_cilium

# Load the Pulumi Config
config = pulumi.Config()
kubernetes_distribution = config.getObject("kubernetes_distribution") or "kind"

# Get the kubeconfig context from the Pulumi configuration
context = config.get("kubeconfig.context") or "kind-pulumi"

# Create a Kubernetes provider instance
# using the context from the Pulumi ESC kubeconfig value
k8s_provider = Provider(
    "k8sProvider",
    kubeconfig=config.require("kubeconfig"),
    context=context
)
pulumi.export("kubeconfig", k8s_provider.context)

# Fetch the Kubernetes endpoint for "kubernetes"
k8s_endpoint = core.v1.Endpoints.get(
    "k8s-endpoint",
    "kubernetes",
    opts=pulumi.ResourceOptions(
        provider=k8s_provider
    )
)
pulumi.export("k8s_endpoint", k8s_endpoint)

# Extract and export the clusterIP
k8s_endpoint_ip = pulumi.Output.from_input(k8s_endpoint.subsets[0].addresses[0].ip)
pulumi.export('k8s_endpoint', k8s_endpoint_ip)

# Cilium Helm Chart Values
cilium_helm_values = {
    "namespace": "kube-system",
    "routingMode": "tunnel",
    "k8sServicePort": 6443,
    "tunnelProtocol": "vxlan",
    "k8sServiceHost": cluster_ip,
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

# Deploy Helm Chart for Jobs App
jobs_app_helm_values = {
    "namespace": "jobs-app",
    "networkPolicy": {
        "enabled": True,
        "enableHTTPIngressVisibility": True,
        "enableKafkaIngressVisibility": False,
        "enableHTTPEgressVisibility": False,
        "enableKafkaEgressVisibility": True,
    }
}

jobs_app_helm_release = helm.v3.Release(
    "jobs-app",
    chart="../charts/jobs-app",
    values=jobs_app_helm_values,
    namespace=jobs_app_helm_values["namespace"],
    wait_for_jobs=True,
    skip_await=False,
    create_namespace=True,
    skip_crds=False,
    opts=pulumi.ResourceOptions(
        provider=k8s_provider, depends_on=[cilium_helm_release]
    )
)

# Export the Cilium Helm Release resources
pulumi.export('cilium_resources', cilium_helm_release.resource_names)
pulumi.export('cilium_release_name', cilium_helm_release.status.apply(lambda status: status.name))
