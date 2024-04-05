import pulumi
from pulumi_kubernetes import helm

def deploy_jobs_app(k8s_provider, cilium_release):
    # Deploy Helm Chart for Jobs App
    jobs_app_helm_values = {
        "namespace": "jobs-app",
        "networkPolicy": {
            "enabled": True,
            "enableHTTPIngressVisibility": True,
            "enableKafkaIngressVisibility": False,
            "enableHTTPEgressVisibility": False,
            "enableKafkaEgressVisibility": True,
        }
    }

    jobs_app_helm_release = helm.v3.Release(
        "jobs-app",
        chart="jobs_app/charts/jobs-app",
        values=jobs_app_helm_values,
        namespace=jobs_app_helm_values["namespace"],
        wait_for_jobs=True,
        skip_await=False,
        create_namespace=True,
        skip_crds=False,
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[cilium_release]
        )
    )

    return jobs_app_helm_release
