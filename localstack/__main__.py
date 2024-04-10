import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as kubernetes

# Constants for the deployment configuration
DEPLOYMENT_NAME = "httpd-deployment"
CONTAINER_IMAGE = "httpd"
SERVICE_NAME = "httpd-service"
INGRESS_NAME = "httpd-ingress"
CONTAINER_PORT = 80
HTTP_PORT = 80

# Centralized resource options with custom timeout option
common_timeout_options = pulumi.ResourceOptions(
    custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="10m")
)

# Function to create metadata with optional additional labels
def create_metadata_with_labels(name, additional_labels=None):
    labels = {"appClass": name}
    if additional_labels:
        labels.update(additional_labels)
    return kubernetes.meta.v1.ObjectMetaArgs(labels=labels)

# Create an EKS cluster with Fargate profile
cluster = eks.Cluster(
    "kubernetes-cluster",
    fargate=True,
    opts=pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create="20m"))
)

# Kubernetes provider instance using the EKS cluster kubeconfig
eks_provider = kubernetes.Provider(
    "kubernetes-provider",
    kubeconfig=cluster.kubeconfig.apply(lambda kc: kc),
    opts=common_timeout_options
)

## Kubernetes deployment configuration
#app_labels = create_metadata_with_labels(DEPLOYMENT_NAME)
#
## Create the Kubernetes Deployment using the EKS Provider
#app_deployment = kubernetes.apps.v1.Deployment(
#    DEPLOYMENT_NAME,
#    metadata=kubernetes.meta.v1.ObjectMetaArgs(name=DEPLOYMENT_NAME),
#    spec=kubernetes.apps.v1.DeploymentSpecArgs(
#        selector=kubernetes.meta.v1.LabelSelectorArgs(match_labels=app_labels.labels),
#        replicas=2,
#        template=kubernetes.core.v1.PodTemplateSpecArgs(
#            metadata=app_labels,
#            spec=kubernetes.core.v1.PodSpecArgs(
#                containers=[kubernetes.core.v1.ContainerArgs(
#                    name=DEPLOYMENT_NAME,
#                    image=CONTAINER_IMAGE,
#                    ports=[kubernetes.core.v1.ContainerPortArgs(container_port=CONTAINER_PORT)]
#                )]
#            )
#        )
#    ),
#    opts=pulumi.ResourceOptions(provider=eks_provider)
#)

## Create the Kubernetes Service
#app_service = kubernetes.core.v1.Service(
#    SERVICE_NAME,
#    metadata=kubernetes.meta.v1.ObjectMetaArgs(name=SERVICE_NAME),
#    spec=kubernetes.core.v1.ServiceSpecArgs(
#        selector=app_labels.labels,
#        ports=[kubernetes.core.v1.ServicePortArgs(
#            port=HTTP_PORT,
#            target_port=CONTAINER_PORT
#        )],
#        type="ClusterIP",
#    ),
#    opts=pulumi.ResourceOptions(provider=eks_provider)  # Associate this service with the EKS provider
#)

## Create the Kubernetes Ingress
#app_ingress = kubernetes.networking.v1.Ingress(
#    INGRESS_NAME,
#    metadata=kubernetes.meta.v1.ObjectMetaArgs(name=INGRESS_NAME),
#    spec=kubernetes.networking.v1.IngressSpecArgs(
#        rules=[kubernetes.networking.v1.IngressRuleArgs(
#            http=kubernetes.networking.v1.HTTPIngressRuleValueArgs(
#                paths=[kubernetes.networking.v1.HTTPIngressPathArgs(
#                    path="/",
#                    path_type="Prefix",
#                    backend=kubernetes.networking.v1.IngressBackendArgs(
#                        service=kubernetes.networking.v1.IngressServiceBackendArgs(
#                            name=SERVICE_NAME,
#                            port=kubernetes.networking.v1.ServiceBackendPortArgs(number=HTTP_PORT)
#                        )
#                    )
#                )]
#            )
#        )]
#    ),
#    opts=pulumi.ResourceOptions(provider=eks_provider)  # Associate this ingress with the EKS provider
#)

# Export the Kubeconfig and Deployment name
pulumi.export('kubeconfig', cluster.kubeconfig)

# App deployment stack outputs
#pulumi.export('deployment_name', app_deployment.metadata.apply(lambda meta: meta.name))
#pulumi.export("service_name", app_service.metadata.apply(lambda meta: meta.name))
#pulumi.export("ingress_name", app_ingress.metadata.apply(lambda meta: meta.name))
#pulumi.export("ingress_url", app_ingress.status.cluster_ip.ingress[0].hostname)

## Export configurations
#pulumi.export("update-cmd", cluster.name.apply(
#    lambda cluster_name: f"awslocal eks update-kubeconfig --name {cluster_name} && kubectl config use-context arn:aws:eks:{aws.get_region().name}:{aws.get_caller_identity().account_id}:cluster/{cluster_name}"
#))
#pulumi.export("url", pulumi.Output.from_input("http://localhost:8081/"))
