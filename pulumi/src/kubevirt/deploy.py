import pulumi
import requests
import pulumi_kubernetes as k8s
from pulumi_kubernetes.apiextensions import CustomResource
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs

def deploy_kubevirt(
        namespace: str,
        version: str,
        depends: pulumi.Resource,
        kubernetes_distribution: str,
        k8s_provider: k8s.Provider
    ):

    # Check if version is set
    # If not, fetch the latest stable version from KubeVirt releases
    if version is None:
        url_kubevirt_releases_stable = 'https://storage.googleapis.com/kubevirt-prow/release/kubevirt/kubevirt/stable.txt'
        version = requests.get(url_kubevirt_releases_stable).text.strip()

    # Deploy the KubeVirt operator
    url = f'https://github.com/kubevirt/kubevirt/releases/download/{version}/kubevirt-operator.yaml'
    kubevirt_operator = k8s.yaml.ConfigFile(
        'kubevirt-operator',
        file=url,
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[depends]
        )
    )

    kubevirt_custom_resource_spec = {
        "customizeComponents": {},
        "workloadUpdateStrategy": {},
        "certificateRotateStrategy": {},
        "imagePullPolicy": "IfNotPresent",
        "configuration": {
            "smbios": {
                "sku": "kargo-kc2",
                "version": version,
                "manufacturer": "ContainerCraft",
                "product": "Kargo",
                "family": "CCIO"
            },
            "developerConfiguration": {
                "useEmulation": kubernetes_distribution == "kind",
                "featureGates": [
                    "HostDevices",
                    "AutoResourceLimitsGate"
                ]
            },
            "permittedHostDevices": {
                "pciHostDevices": [
                ]
            }
        }
    }

    kubevirt = CustomResource(
        "kubevirt",
        api_version="kubevirt.io/v1",
        kind="KubeVirt",
        metadata=ObjectMetaArgs(
            name="kubevirt",
            namespace=namespace
        ),
        spec=kubevirt_custom_resource_spec,
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[depends]
        )
    )

    # Return the version used for the deployment
    return version
