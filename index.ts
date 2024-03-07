// Main Pulumi Typescript Program
import * as pulumi from "@pulumi/pulumi";

// Import the Pulumi Kubernetes Typescript Provider Package
// https://www.pulumi.com/registry/packages/kubernetes/
import * as k8s from '@pulumi/kubernetes';

// Load the Pulumi Config
// This configuration imports config settings from the local Pulumi.$STACK.yaml file and Pulumi ESC sources
const config = new pulumi.Config();

// Get the kubeconfig context from the Pulumi configuration
// If none is specified, use the default "kind-cilium" context
// - pulumi config set kubeconfig.context $KUBECONFIG_CONTEXT_NAME
const context = config.get("kubeconfig.context") || "kind-cilium";

// Create a Kubernetes provider instance that uses the context from the local kubeconfig file.
const k8sProvider = new k8s.Provider("k8sProvider", {
    kubeconfig: pulumi.interpolate`${pulumi.secret(process.env.KUBECONFIG)}`,
    context: context,
});

// Fetch the Kubernetes endpoint for "kubernetes"
const kubernetesEndpoint = k8s.core.v1.Endpoints.get("kubernetes-endpoint", "kubernetes", { provider: k8sProvider });

// Export the IP addresses
export const serverIPs = kubernetesEndpoint.subsets.apply(subsets =>
    subsets.map(subset => subset.addresses.map(address => address.ip)).flat()
);

// Cilium Helm Chart Values
const ciliumHelmValues = {
    namespace: "kube-system",
    routingMode: "tunnel",
    k8sServicePort: 6443,
    tunnelProtocol: "vxlan",
    k8sServiceHost: serverIPs[0],
    kubeProxyReplacement: "strict",
//  This value should be set to the cidr to exclude with nat. the podCidr.
//  Leave this value default unless you know what you are about. 
//  nativeRoutingCIDR: "10.2.0.0/16",
    image: { pullPolicy: "IfNotPresent" },
    hostServices: { enabled: false },
    cluster: { name: "kind-cilium" },
    externalIPs: { enabled: true },
    gatewayAPI: { enabled: false },
    hubble: { 
      enabled: true,
      relay: {
        enabled: true },
      ui: {
        enabled: true },
    },
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
    name: "cilium", // This is the name of the Helm Release and is an arbitrary string
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
// This is the equivalent of returning the output from the following Kubectl command or using `cilium status`:
// - kubectl -n kube-system get deployment cilium-operator -ojsonpath={.status.conditions[0].type}
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
const policyStrict: boolean = true;
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

// Export the name of the CiliumNetworkPolicy
//export const policyName = ciliumNetworkPolicy?.metadata.apply(m => m.name);
//export const appName = demoApp.metadata.apply(m => m.name);

// Export the Cilium Helm Release Resources
export const outputs = {
    ciliumResources: ciliumHelmRelease.resourceNames,
    ciliumReleaseName: ciliumHelmRelease.status.name,
    ciliumReleaseStatus: ciliumOperatorDeploymentStatus,
}
