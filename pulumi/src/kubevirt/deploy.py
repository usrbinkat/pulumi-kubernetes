import pulumi
import requests
import pulumi_kubernetes as k8s

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
    kubevirt_operator_url = f'https://github.com/kubevirt/kubevirt/releases/download/{version}/kubevirt-operator.yaml'
    kubevirt_operator = k8s.yaml.ConfigFile(
        'kubevirt-operator',
        file=kubevirt_operator_url,
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[depends]
        )
    )

    # Set useEmulation 'True' if kubernetes_distribution is Kind else false.
    use_emulation = kubernetes_distribution == 'kind'

    # CustomResource for KubeVirt
    k8s.apiextensions.CustomResource(
        'kubevirt',
        api_version='kubevirt.io/v1',
        kind='KubeVirt',
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name='kubevirt',
            namespace=namespace
        ),
        spec={
            'customizeComponents': {},
            'workloadUpdateStrategy': {},
            'certificateRotateStrategy': {},
            'imagePullPolicy': 'IfNotPresent',
            'configuration': {
                'smbios': {
                    'sku': 'kargo',
                    'version': version,
                    'manufacturer': 'ContainerCraft',
                    'product': 'Kargo',
                    'family': 'kc2'
                },
                'developerConfiguration': {
                    'useEmulation': use_emulation,
                    'featureGates': [
                        'HostDevices',
                        'AutoResourceLimitsGate'
                    ]
                },
                'permittedHostDevices': {
                    'pciHostDevices': []
                }
            }
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[depends])
    )

    # Return the version used for the deployment
    return (version)
