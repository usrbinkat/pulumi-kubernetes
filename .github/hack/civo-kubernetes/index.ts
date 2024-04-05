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

