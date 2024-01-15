# Pulumi IaC Mesh Policy as Code

[![License](https://img.shields.io/github/license/usrbinkat/iac-mesh-pac)]() [![Pulumi](https://img.shields.io/badge/pulumi-v3.0.0-blueviolet)](https://www.pulumi.com/docs/get-started/install/) [![Cilium](https://img.shields.io/badge/cilium-v1.14.5-blueviolet)](https://docs.cilium.io/en/v1.9/gettingstarted/kind/) [![Kubectl](https://img.shields.io/badge/kubectl-v1.21.0-blueviolet)](https://kubernetes.io/docs/tasks/tools/install-kubectl/) [![Docker](https://img.shields.io/badge/docker-v20.10.6-blueviolet)](https://docs.docker.com/get-docker/) [![Kind](https://img.shields.io/badge/kind-v0.11.1-blueviolet)](https://kind.sigs.k8s.io/docs/user/quick-start/) [![Helm](https://img.shields.io/badge/helm-v3.6.3-blueviolet)](https://helm.sh/docs/intro/install/)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/usrbinkat/iac-mesh-pac)

## About

This repo is a Pulumi IaC implementation of the [Cilium Network Policy](https://docs.cilium.io/en/v1.9/gettingstarted/kind/#deploy-cilium) demo, with an exercise in network policy as code.

## How To

```bash
# Create Docker Volumes
docker volume create cilium-worker-n01
docker volume create cilium-worker-n02
docker volume create cilium-control-plane-n01

# Create Kind Cluster
kind create --config hack/kind.yaml

# Pulumi Cloud Login
pulumi login

# Grab NPM dependencies
pulumi install

# Pulumi Deploy Stack
pulumi up
```

## Repo Tree

```bash
iac-mesh-pac on <> main via <> v20.11.0 via <> usrbinkat@iac-mesh-pac
🐋❯ tree -a -I .git -I .devcontainer -I node_modules
.
├── README.md                   # Overview and docs for the project
├── LICENSE                     # Project license file
├── .devcontainer.json          # VSCode Dev Container config
├── .gitmodules                 # Git Submodule config
├── .gitignore                  # Lists files Git should ignore
├── .envrc                      # Direnv shell script for environment variables
│
├── Pulumi.yaml                 # Pulumi project config
├── index.ts                    # Pulumi TypeScript IaC program
└── tsconfig.json               # TypeScript config file
├── package-lock.json           # NPM package lock file
├── package.json                # NPM package config file
│
├── hack                        # Utility scripts and configs
│   ├── kind.yaml               # KinD cluster configuration
│   ├── cilium.yaml             # Cilium helm chart values
│   ├── ciliumnetpol.yaml       # Cilium network policies
│   └── cilium.helm.values.yaml # Cilium helm chart reference default values
│
└── .kube                       # Kubernetes config directory
    ├── config                  # Kubernetes credentials file (gitignored)
    └── .gitkeep                # Keeps .kube in version control when empty

2 directories, 16 files
```

## Alternative manual steps

<details>

```bash
########################################################################
# Create Kind Cluster
kind create --config hack/kind.yaml

# Add cilium helm repo
helm repo add cilium https://helm.cilium.io

# Deploy cilium
helm upgrade --install cilium cilium/cilium --namespace kube-system --version 1.14.5 --values hack/cilium.yaml

# cilium status
cilium status --wait --wait-duration 2m0s

########################################################################
# Starwars Empire vs Rebels Demo App
# https://docs.solo.io/gloo-network/main/quickstart/#policy

export CILIUM_VERSION=1.14.5
kubectl create ns starwars
kubectl -n starwars apply -f https://raw.githubusercontent.com/cilium/cilium/$CILIUM_VERSION/examples/minikube/http-sw-app.yaml

# Apply policy
kubectl apply -f hack/ciliumnetpol.yaml
kubectl get ciliumnetworkpolicy

# Curl policy compliant
kubectl exec tiefighter -n starwars -- curl -s -XPOST deathstar.starwars.svc.cluster.local/v1/request-landing

# Curl policy non-compliant
kubectl exec xwing -n starwars -- curl -s -XPOST deathstar.starwars.svc.cluster.local/v1/request-landing

# check labels
kubectl get pods -n starwars --show-labels
```

</details>