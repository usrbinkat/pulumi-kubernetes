"""A Kubernetes Python Pulumi program"""
# Import python packages
import os
import json
import pulumi
import pulumi_kubernetes as k8s

# Import python packages from the local src directory
from cilium.deploy import deploy_cilium
from jobs_app.deploy import deploy_jobs_app
from cert_manager.deploy import deploy_cert_manager
from kubevirt.deploy import deploy_kubevirt
from starwars.deploy import deploy_starwars

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

# Cilium CNI
# Check pulumi config 'cilium.enable' and deploy if true
# Disable Cilium with the following command:
#   ~$ pulumi config set cilium.enable false
# Set Cilium version override with the following command:
#   ~$ pulumi config set cilium.version v1.14.7
enable = config.get_bool('cilium.enable') or True
version = config.get('cilium.version') or None
namespace = "kube-system"
if enable:
    # Deploy Cilium
    cilium = deploy_cilium(
        namespace,
        version,
        kubernetes_endpoint,
        kubernetes_distribution,
        kubernetes_provider
    )
else:
    cilium = (None, None)

# Cert Manager
# Check pulumi config 'cert_manager.enable' and deploy if true
# Enable cert-manager with the following command:
#   ~$ pulumi config set cert_manager.enable true
# Set cert-manager version override with the following command:
#   ~$ pulumi config set cert_manager.version v1.5.3
enable = config.get_bool('cert_manager.enable') or False
version = config.get('cert_manager.version') or None
namespace = "cert-manager"
if enable:
    # Deploy cert-manager
    cert_manager = deploy_cert_manager(
        namespace,
        version,
        kubernetes_distribution,
        kubernetes_provider
    )
else:
    cert_manager = (None, None)

# Kubevirt
# Check pulumi config 'kubevirt.enable' and deploy if true
# Enable Kubevirt with the following command:
#   ~$ pulumi config set kubevirt.enable true
# Set Kubevirt version override with the following command:
#   ~$ pulumi config set kubevirt.version v0.46.0
enable = config.get_bool('kubevirt.enable') or False
version = config.get('kubevirt.version') or None
namespace = "kubevirt"
depends = cert_manager[1]
if enable:
    # Deploy KubeVirt
    kubevirt = deploy_kubevirt(
        namespace,
        version,
        depends,
        kubernetes_distribution,
        kubernetes_provider
    )
    pulumi.export('KubeVirt_version', kubevirt)
else:
    kubevirt = (None)

# Demo Helm Chart "Jobs App"
# Get pulumi config jobs_app.enable boolian
# ~$ pulumi config set jobs_app.enable true
enable = config.get_bool('jobs_app.enable') or False
if enable:
    # If bool true, deploy the Jobs App Helm Chart
    jobs_app = deploy_jobs_app(
        kubernetes_provider,
        cilium[1]
    )

# If starwars.enable is true, deploy the Star Wars app
# Enable the Star Wars app with the following command:
#   ~$ pulumi config set starwars.enable true
# Set the Cilium Network Policy with the following command:
#   ~$ pulumi config set cilium.strict true
starwars_enable = config.get_bool("starwars.enable") or False
cilium_policy_strict = config.get_bool("cilium.strict") or False
namespace = "empire"
if starwars_enable:
    starwars = deploy_starwars(
        namespace,
        cilium_policy_strict,
        kubernetes_provider
    )


##################################################################################
## Export Stack Outputs
##################################################################################

# Export the kubernetes_provider securely as a secret for use in other stacks
pulumi.export("kubernetes_provider", kubernetes_provider)

# Use pulumi.Output.all() to aggregate all Output values and then construct the dictionary
kube_json = pulumi.Output.all(
    kubernetes_distribution,
    kubernetes_config,
    kubernetes_context,
    kubernetes_endpoint
).apply(lambda args: json.dumps({"kubernetes": {
    "dist": args[0],
    "config": args[1],
    "context": args[2],
    "endpoint": args[3]
}}, default=str))

# Export the 'kube' dictionary as a stack output in json format
pulumi.export("kube", kube_json)

# Create a dictionary of deployed resource versions
version_json = pulumi.Output.all(
    cilium[0] or None,
    cert_manager[0] or None,
    kubevirt or None
).apply(lambda args: json.dumps({
    "cilium": args[0],
    "cert_manager": args[1],
    "kubevirt": args[2]
}, default=str))

# Export the 'version' dictionary as a stack output in json format
pulumi.export("version", version_json)
