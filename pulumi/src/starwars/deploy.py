import pulumi
import pulumi_kubernetes as k8s

# Resources Deployment
def deploy_starwars(
        ns: str,
        cilium_policy_strict: bool,
        kubernetes_provider: k8s.Provider
    ):
    # Create a Namespace called "empire"
    namespace = k8s.core.v1.Namespace(
        "starwars_namespace",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=ns
        ),
        opts=pulumi.ResourceOptions(
            provider=kubernetes_provider,
            retain_on_delete=False,
            custom_timeouts=pulumi.CustomTimeouts(
                create="10m",
                update="10m",
                delete="10m"
            )
        )
    )

    starwars_app = k8s.yaml.ConfigFile(
        "starwars",
        file="https://raw.githubusercontent.com/cilium/cilium/HEAD/examples/minikube/http-sw-app.yaml",
        transformations=[lambda obj: obj['metadata'].update({"namespace": ns}) if "metadata" in obj else None],
        opts=pulumi.ResourceOptions(
            provider=kubernetes_provider,
            depends_on=[namespace]
        )
    )

    # Check if the Cilium Network Policy is enabled and deploy if true
    if cilium_policy_strict:
        # Create the CiliumNetworkPolicy using Pulumi
        # TODO
        # pulumi:pulumi:Stack (pulumi-kubernetes-kind):
        # error: Program failed with an unhandled exception:
        # Traceback (most recent call last):
        #   File "/workspaces/pulumi-kubernetes/pulumi/src/./__main__.py", line 136, in <module>
        #     starwars = deploy_starwars(
        #   File "/workspaces/pulumi-kubernetes/pulumi/src/./starwars/deploy.py", line 45, in deploy_starwars
        #     cilium_network_policy = CustomResource(
        # TypeError: 'module' object is not callable
        cilium_network_policy = k8s.apiextensions.CustomResource(
            resource_name="cilium-network-policy-deathstar",
            api_version="cilium.io/v2",
            kind="CiliumNetworkPolicy",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="deathstar-policy",
                namespace=ns
            ),
            spec={
                "description": "L3-L4 policy to restrict Death Star access to Empire ships only",
                "endpointSelector": {
                    "matchLabels": {
                        "org": "empire",
                        "class": "deathstar",
                    },
                },
                "ingress": [
                    {
                        "fromEndpoints": [
                            {
                                "matchLabels": {
                                    "org": "empire",
                                },
                            },
                        ],
                        "toPorts": [
                            {
                                "ports": [
                                    {
                                        "port": "80",
                                        "protocol": "TCP",
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            opts=k8s.ResourceOptions(
                provider=kubernetes_provider,
                depends_on=[namespace]
            )
        )
