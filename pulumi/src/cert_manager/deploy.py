import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.apiextensions.CustomResource import CustomResource
from lib.helm_release_latest import get_latest as get_helm_latest

# Cert Manager Resources Deployment
def deploy_cert_manager(
        ns: str,
        version: str,
        kubernetes_distribution: str,
        kubernetes_provider: k8s.Provider
    ):

    # Create a Namespace
    namespace = k8s.core.v1.Namespace("cert_manager_namespace",
        metadata= k8s.meta.v1.ObjectMetaArgs(
            name=ns
        ),
        opts=pulumi.ResourceOptions(
            provider = kubernetes_provider,
            retain_on_delete=True,
            custom_timeouts=pulumi.CustomTimeouts(
                create="10m",
                update="10m",
                delete="10m"
            )
        )
    )

    # Check if version is set
    # If not, fetch the latest version from the helm chart index
    chart_name = "cert-manager"
    chart_index_path = "index.yaml"
    chart_url = "https://charts.jetstack.io"
    index_url = f"{chart_url}/{chart_index_path}"
    if version is None:
        version = get_helm_latest(index_url, chart_name)

    # Assemble Helm Values
    helm_values = gen_helm_values(kubernetes_distribution)

    # Deploy Cert Manager Helm Chart
    release = k8s.helm.v3.Release(
        ns,
        k8s.helm.v3.ReleaseArgs(
            version=version,
            chart=chart_name,
            values=helm_values,
            namespace=namespace.metadata["name"],
            repository_opts= k8s.helm.v3.RepositoryOptsArgs(
                repo=chart_url
            ),
            skip_await=False,
        ),
        opts=pulumi.ResourceOptions(
            provider = kubernetes_provider,
            depends_on=[namespace],
            custom_timeouts=pulumi.CustomTimeouts(
                create="8m",
                update="10m",
                delete="10m"
            )
        )
    )

    # Create a Local Self Signed ClusterIssuer
    cluster_issuer_root = CustomResource(
        "cluster-selfsigned-issuer-root",
        api_version="cert-manager.io/v1",
        kind="ClusterIssuer",
        metadata={
            "name": "cluster-selfsigned-issuer-root",
            "namespace": namespace.metadata["name"]
        },
        spec={
            "selfSigned": {}
        },
        opts=pulumi.ResourceOptions(
            provider = kubernetes_provider,
            depends_on=[release],
            custom_timeouts=pulumi.CustomTimeouts(
                create="5m",
                update="10m",
                delete="10m"
            )
        )
    )

    # Create a Local Self Signed Certificate
    cluster_issuer_ca_certificate = CustomResource(
        "cluster-selfsigned-issuer-ca",
        api_version="cert-manager.io/v1",
        kind="Certificate",
        metadata={
            "name": "cluster-selfsigned-issuer-ca",
            "namespace": namespace.metadata["name"]
        },
        spec={
            "commonName": "cluster-selfsigned-issuer-ca",
            "duration": "2160h0m0s",
            "issuerRef": {
                "group": "cert-manager.io",
                "kind": "ClusterIssuer",
                "name": cluster_issuer_root.metadata["name"],
            },
            "privateKey": {
                "algorithm": "ECDSA",
                "size": 256
            },
            "isCA": True,
            "renewBefore": "360h0m0s",
            "secretName": "cluster-selfsigned-issuer-ca"
        },
        opts=pulumi.ResourceOptions(
            provider = kubernetes_provider,
            depends_on=[cluster_issuer_root],
            custom_timeouts=pulumi.CustomTimeouts(
                create="5m",
                update="10m",
                delete="10m"
            )
        )
    )

    # Create a Local full chain Self Signed ClusterIssuer
    cluster_issuer = CustomResource(
        "cluster-selfsigned-issuer",
        api_version="cert-manager.io/v1",
        kind="ClusterIssuer",
        metadata={
            "name": "cluster-selfsigned-issuer",
            "namespace": namespace.metadata["name"]
        },
        spec={
            "ca": {
                "secretName": cluster_issuer_ca_certificate.spec["secretName"],
            }
        },
        opts=pulumi.ResourceOptions(
            provider = kubernetes_provider,
            depends_on=[cluster_issuer_ca_certificate],
            custom_timeouts=pulumi.CustomTimeouts(
                create="5m",
                update="10m",
                delete="10m"
            )
        )
    )

    return version, release

def gen_helm_values(kubernetes_distribution: str):

    # Common helm values
    common_values = {
        'replicaCount': 1,
        'installCRDs': True
    }

    # Add distribution specific values
    if kubernetes_distribution == 'kind':
        # Kind Kubernetes specific Helm values
        values = {
            **common_values,
        }
    elif kubernetes_distribution == 'talos':
        # Talos Kubernetes specific Helm values
        values = {
            **common_values,
        }

    # Return assembled values
    return values
