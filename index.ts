import * as pulumi from "@pulumi/pulumi";
import * as k8s from '@pulumi/kubernetes';

// Load the Pulumi Config
const config = new pulumi.Config();

// Get the kubeconfig context from the Pulumi configuration
// If none is specified, use the default "kind-cilium" context
const context = config.get("kubeconfig.context") || "kind-cilium";

// Create a Kubernetes provider instance that uses the context from the local kubeconfig file.
const k8sProvider = new k8s.Provider("k8sProvider", {
    kubeconfig: pulumi.interpolate`${pulumi.secret(process.env.KUBECONFIG)}`,
    context: context,
});

// Cilium Helm Chart Values
const ciliumHelmValues = {
    namespace: "kube-system",
    routingMode: "tunnel",
    k8sServicePort: 6443,
    tunnelProtocol: "vxlan",
//  k8sServiceHost: "172.18.0.3",
    kubeProxyReplacement: "strict",
    nativeRoutingCIDR: "10.2.0.0/16",
    image: { pullPolicy: "IfNotPresent" },
    hostServices: { enabled: false },
    cluster: { name: "kind-cilium" },
    externalIPs: { enabled: true },
    gatewayAPI: { enabled: true },
    ipam: { mode: "kubernetes" },
    nodePort: { enabled: true },
    hostPort: { enabled: true },
    operator: { replicas: 1 },
    serviceAccounts: {
        cilium: { name: "cilium" },
        operator: { name: "cilium-operator" },
    },
};

// Deploy Helm Chart for Cilium
const ciliumHelmRelease = new k8s.helm.v3.Release("cilium-release", {
    chart: "cilium",
    name: "cilium",
    repositoryOpts: {repo: "https://helm.cilium.io/"},
    version: "1.14.5",
    values: ciliumHelmValues,
    namespace: ciliumHelmValues.namespace,
    waitForJobs: true,
    skipAwait: false,
    skipCrds: false,
    lint: true,
}, { provider: k8sProvider });

// Fetch the Cilium Operator Deployment after the Helm release has been deployed
const ciliumOperatorDeployment = pulumi.all([ciliumHelmRelease.status]).apply(([status]) => {
    return k8s.apps.v1.Deployment.get("cilium-operator-deployment", pulumi.interpolate`${status.namespace}/cilium-operator`, {
        provider: k8sProvider,
    });
});

// Extract and Export the First Condition Type from the Deployment Status
const ciliumOperatorDeploymentStatus = ciliumOperatorDeployment.status.apply(status => {
    if (status && status.conditions && status.conditions.length > 0) {
        return status.conditions[0].type;
    } else {
        return "Unknown";
    }
});

// Export the Cilium Helm Release Resources
export const outputs = {
    ciliumResources: ciliumHelmRelease.resourceNames,
    ciliumReleaseName: ciliumHelmRelease.status.name,
    ciliumReleaseStatus: ciliumOperatorDeploymentStatus,
}
