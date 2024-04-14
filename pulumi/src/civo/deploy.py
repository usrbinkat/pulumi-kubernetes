import json
import pulumi
from pulumi_kubernetes import Provider, yaml
from pulumi_civo import FireWall, KubernetesCluster, Provider

config = pulumi.Config()
civo_token = config.require_secret("civo_token")

civo_provider = Provider("civo-provider", token=civo_token)

firewall = FireWall(
    "firewall",
    name="fw1",
    region="NYC1",
    create_default_rules=True,
    opts=pulumi.ResourceOptions(
        provider=civo_provider
    )
)

cluster = KubernetesCluster(
    "cluster",
    name="cluster",
    firewall_id=firewall.id,
    pools=[{
        "nodeCount": 3,
        "size": "g4s.kube.medium"
    }],
    region="NYC1",
    cluster_type="k3s",
    cni="cilium",
    opts=pulumi.ResourceOptions(
        provider=civo_provider
    )
)

k8s_provider = Provider("k8s-provider", kubeconfig=cluster.kubeconfig)
