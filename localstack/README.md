# Pulumi IaC + Localstack | EKS Fargate Cluster

## NOTICE: Testing codebase independently before writing a new conditional localstack module

Sample code to run a Localstack provisioned "EKS Fargate" cluster in Github Codespaces or Devcontainers.

Current testing informed from https://github.com/lakkeger/localstack-sample-pulumi-eks.git

## Requirements
Accounts:
- Github
- Pulumi Cloud
- Localstack Pro

## Instructions

### To spin it up
0. Export environment variables
```
direnv allow
```
1. Run Localstack
```
localstack start --host
```
2. Run pulumi
```
pulumi login
pulumi install
pip install pulumi-local
pulumilocal init
pulumi stack select --create localstack
pulumi up
```
3. Visit `http://localhost:8081`
4. Profit 💵

## Notes

- Run with `pulumi` and not `pulumilocal` due to performance degradation in this version of AWS package with increasing number of custom endpoints (adding all 2xx endpoints with `pulumilocal` would make this sample run 20-30 mins)
- for `NodePort` services one must expose the server port manually with:
```
k3d cluster edit <CLUSTER_NAME> --port-add <HOST_PORT>:<NODE_PORT>@server:0
```
- `LoadBalancer` type services currently are not supported
