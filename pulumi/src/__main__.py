"""A Kubernetes Python Pulumi program"""
# Import python packages
import os
import pulumi
import pulumi_kubernetes as k8s

# Import python packages from the local src directory
from cilium.deploy import deploy_cilium
from jobs_app.deploy import deploy_jobs_app

##################################################################################
# Load the Pulumi Config
config = pulumi.Config()

# Get the kubeconfig file path from priority order:
# 1. Pulumi configuration value: `pulumi config set kubeconfig <path>`
# 2. KUBECONFIG environment variable
# 3. Default to ~/.kube/config
kubernetes_config = config.get("kubeconfig") or os.getenv("KUBECONFIG") or "~/.kube/config"
# Get the kubeconfig context from the Pulumi configuration
kubernetes_context = config.get("kubeconfig.context") or "kind-pulumi"
# Get the Kubernetes distribution from the Pulumi configuration
kubernetes_distribution = config.get("kubernetes_distribution") or "kind"

# Create a Kubernetes provider instance
kubernetes_provider = k8s.Provider(
    "kubernetes_provider",
    kubeconfig=kubernetes_config,
    context=kubernetes_context
)

# Fetch the Kubernetes endpoint for "kubernetes"
k8s_endpoint = k8s.core.v1.Endpoints.get(
    "k8s-endpoint",
    "kubernetes",
    opts=pulumi.ResourceOptions(
        provider=kubernetes_provider
    )
)

# Extract the Kubernetes Endpoint clusterIP
kubernetes_endpoint = pulumi.Output.from_input(k8s_endpoint.subsets[0].addresses[0].ip)

##################################################################################
## Deploy Kubernetes Resources
##################################################################################

# Cilium Helm Chart
cilium_release = deploy_cilium(
    kubernetes_provider,
    kubernetes_distribution,
    kubernetes_endpoint
)

# Demo Helm Chart "Jobs App"
# Get pulumi config jobs_app.enabled boolian
if config.get_bool("jobs_app.enabled"):
    # If bool true, deploy the Jobs App Helm Chart
    jobs_app = deploy_jobs_app(
        kubernetes_provider,
        cilium_release
    )

##################################################################################
## Export Stack Outputs
##################################################################################

# Export the Kubernetes configuration values
kube = {
    "kubernetes_dist": kubernetes_distribution,
    "kubernetes_config":  kubernetes_config,
    "kubernetes_context": kubernetes_context,
    "kubernetes_endpoint": kubernetes_endpoint
}
pulumi.export("kubernetes", kube)

# Export the kubernetes_provider securely as a secret for use in other stacks
pulumi.export("kubernetes_provider", kubernetes_provider.context)
