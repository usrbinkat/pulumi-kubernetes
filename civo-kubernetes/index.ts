import * as pulumi from "@pulumi/pulumi";
import * as civo from "@pulumi/civo";
import * as k8s from "@pulumi/kubernetes";

// Initialize a Pulumi configuration to access the secret Civo API token
const config = new pulumi.Config();

// Pull civo PAT from pulumi config
// - ~$ pulumi config set civo:token AdFXXXXXXXXXXXXXXXXXxiV --secret
const civoToken = config.requireSecret("token");

// Custom provider for Civo API authentication
const civoProvider = new civo.Provider("civoProvider", {
  token: civoToken,
});

// CIVO Network Firewall
const firewall = new civo.Firewall(
  "civo-policy-as-code",
  {
    name: "fw1",
    region: "NYC1",
    createDefaultRules: true,
  }, {
    provider: civoProvider,
  }
);

//// CIVO Firewall Rule to allow port 6443
//new civo.FirewallRule("6443", {
//  action: "allow",
//  firewallId: firewall.id,
//  protocol: "tcp",
//  startPort: "6443",
//  endPort: "6443",
//  cidrs: ["0.0.0.0/0"],
//  direction: "ingress",
//}, {
//  provider: civoProvider,
//});

// CIVO Kubernetes
// - Talos k8s
// - cilium CNI
const cluster = new civo.KubernetesCluster("davenull-kubernetes", {
  name: "davenull-kubernetes",
  pools: {
    nodeCount: 3,
    size: "g4s.kube.medium",
  },
  region: "NYC1",
  firewallId: firewall.id,
  clusterType: "talos",
  cni: "cilium",
  }, {
    provider: civoProvider,
  }
);

export const clusterName = cluster.name;

// CIVO Kubernetes Provider instance
// Pull kubeconfig from the cluster resource outputs
const k8sProvider = new k8s.Provider("civo-kubernetes", {
  kubeconfig: cluster.kubeconfig.apply(JSON.stringify),
});

// pulumi output kubernetes kubeconfig as json string
export const kubeconfig = cluster.kubeconfig.apply(JSON.stringify);

// Deploy the Cilium demo application using the YAML file from GitHub.
const demoApp = new k8s.yaml.ConfigFile("http-sw-app", {
    // deploy this app into the namespace `default`
    transformations: [
        (obj: any) => {
            if (obj.metadata) {
                obj.metadata.namespace = "default";
            }
        },
    ],
    file: "https://raw.githubusercontent.com/cilium/cilium/HEAD/examples/minikube/http-sw-app.yaml",
    resourcePrefix: "deathstar",
});

// A variable indicating whether the policy should be strict
// retrieve bool condition from pulumi config to enable/disable policyStrict
const policyStrict = config.getBoolean("policyStrict") || false;

let ciliumNetworkPolicy: k8s.apiextensions.CustomResource | undefined;

if (policyStrict) {
    // Define the CiliumNetworkPolicy
    const ciliumNetworkPolicy = new k8s.apiextensions.CustomResource("rule1", {
        apiVersion: "cilium.io/v2",
        kind: "CiliumNetworkPolicy",
        metadata: {
            name: "rule1",
            namespace: "default",
        },
        spec: {
            description: "L3-L4 policy to restrict deathstar access to empire ships only",
            endpointSelector: {
                matchLabels: {
                    org: "empire",
                    class: "deathstar",
                },
            },
            ingress: [
                {
                    fromEndpoints: [
                        {
                            matchLabels: {
                                org: "empire",
                            },
                        },
                    ],
                    toPorts: [
                        {
                            ports: [
                                {
                                    port: "80",
                                    protocol: "TCP",
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    });
}
