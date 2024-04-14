import pulumi
import pulumi_kubernetes as k8s

def deploy_starwars(ns: str, cilium_policy_strict: bool, k8s_provider: k8s.Provider):

    namespace = k8s.core.v1.Namespace(
        "starwars_namespace",
        metadata=k8s.meta.v1.ObjectMetaArgs(name=ns),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="10m")
        )
    )

    def set_namespace(obj):
        if 'metadata' in obj:
            obj['metadata']['namespace'] = ns

    starwars_demo_app = k8s.yaml.ConfigFile(
        "starwars",
        file="https://raw.githubusercontent.com/cilium/cilium/HEAD/examples/minikube/http-sw-app.yaml",
        transformations=[set_namespace],
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[namespace]
        )
    )

    if cilium_policy_strict:
        cilium_network_policy = k8s.apiextensions.CustomResource(
            "cilium_network_policy_deathstar",
            api_version="cilium.io/v2",
            kind="CiliumNetworkPolicy",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="deathstar-policy",
                namespace=ns
            ),
            spec={
                "description": "L3-L4 policy to restrict Death Star access to Empire ships only",
                "endpointSelector": {"matchLabels": {"org": "empire", "class": "deathstar"}},
                "ingress": [{
                    "fromEndpoints": [{"matchLabels": {"org": "empire"}}],
                    "toPorts": [{"ports": [{"port": "80", "protocol": "TCP"}]}]
                }],
            },
            opts=pulumi.ResourceOptions(
                provider=k8s_provider,
                depends_on=[namespace]
            )
        )
    else:
        cilium_network_policy = None

    return namespace, starwars_demo_app, cilium_network_policy
