# Pulumi + Kubernetes

[![CI - Cilium on Kind](https://github.com/usrbinkat/cilium-kubernetes/actions/workflows/ci.yaml/badge.svg)](https://github.com/usrbinkat/cilium-kubernetes/actions/workflows/ci.yaml) [![License](https://img.shields.io/github/license/usrbinkat/iac-mesh-pac)]() [![Pulumi](https://img.shields.io/badge/pulumi-v3.101.1-blueviolet)](https://www.pulumi.com/docs/get-started/install/) [![Cilium](https://img.shields.io/badge/cilium-v1.14.5-blueviolet)](https://docs.cilium.io/en/v1.9/gettingstarted/kind/) [![kubectl](https://img.shields.io/badge/kubectl-v1.29.0-blueviolet)](https://kubernetes.io/docs/tasks/tools/install-kubectl/) [![Docker](https://img.shields.io/badge/docker-v24.0.7-blueviolet)](https://docs.docker.com/get-docker/) [![Kind](https://img.shields.io/badge/kind-v0.20.0-blueviolet)](https://kind.sigs.k8s.io/docs/user/quick-start/)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/usrbinkat/pulumi-kubernetes?quickstart=1&devcontainer_path=.devcontainer%2Fdevcontainer.json)

## Index

- [Infrastructure as Code](#infrastructure-as-code)
  - [Overview](#overview)
  - [How To](#how-to)
    - [1. Create Kind Kubernetes Cluster](#1-create-kind-kubernetes-cluster)
    - [2. Deploy Cilium and Cilium Network Policy](#2-deploy-cilium-and-cilium-network-policy)
    - [3. Check pods and labels](#3-check-pods-and-labels)
    - [4. Test Cilium Network Policy](#4-test-cilium-network-policy)
    - [5. Cleanup](#4-cleanup)
  - [Repo Tree](#repo-tree)

## Infrastructure as Code

### Overview

This repository contains a [Python] infrastructure as code (IaC) project that deploys a collection of Kubernetes resources to a local [KinD](https://kind.sigs.k8s.io/) cluster. The project demonstrates a number of features and workflows, including:

- **[Python]**: Python is a popular programming language that is widely used for general purpose scripting and programming. It is known for its simplicity and readability, and is widely used in the AI and DevOps communities.
- **[Pulumi]**: Pulumi is an open-source infrastructure as code tool that allows you to define, deploy, and manage cloud infrastructure using familiar programming languages. It provides a consistent and programmable way to provision and manage resources across different cloud providers.
- **[KinD] (Kubernetes-in-Docker)**: KinD is a tool for running local Kubernetes clusters using Docker container "nodes". It allows you to create and manage Kubernetes clusters for development and testing purposes.
- **[Cilium]**: Cilium is an open-source project that provides networking and security for applications running on Kubernetes. It offers enhanced network visibility, load balancing, and network security features.
- **[Cert-Manager]**: Cert-Manager is a Kubernetes add-on to automate the management and issuance of TLS certificates from various issuing sources.
- **[Kubevirt]**: KubeVirt is a virtualization add-on for Kubernetes that allows you to run virtual machines alongside your container workloads in Kubernetes.
- **[Containerized Data Importer]**: The Containerized Data Importer (CDI) is a Kubernetes add-on that allows you to import and prepare VM images for use with KubeVirt.

[Cilium]: https://cilium.io
[Pulumi]: https://www.pulumi.com
[Kind]: https://kind.sigs.k8s.io
[Kubevirt]: https://kubevirt.io
[Cert-Manager]: https://cert-manager.io
[Containerized Data Importer]: https://kubevirt.io/user-guide/operations/containerized_data_importer
[Python]: https://www.python.org

### How To

To try the Cilium Network Policy demo, follow these steps:

1. [Open this project in GitHub Codespaces](https://codespaces.new/usrbinkat/cilium-kubernetes)
2. Login to Pulumi Cloud
3. Create Pulumi ESC Environment
4. Create Kind Kubernetes Cluster
5. Deploy Pulumi IaC
6. Add VM Count integer config
7. Pulumi UP to build VMs
8. Cleanup

#### 1. Create Kind Kubernetes Cluster

```bash
make kind
```

### 2. Deploy Cilium and Cilium Network Policy

```bash
# Pulumi Login && Install Typescript Dependencies
pulumi login && pulumi install

# Pulumi Create/Select Stack
pulumi stack select --create $GITHUB_USER/pulumi-kubernetes/kind

# Pulumi Deploy Stack
pulumi up
```

#### 3. Cleanup

```bash
# Pulumi Destroy Stack & Delete Kind Cluster
make clean

# Stop Github Codespaces
make stop
```

> After stopping the GH Codespace go to the GH Codespaces dashboard and delete the Codespace
>
> - https://github.com/codespaces

### Repo Tree

> Index of important files in this project.
>
> ```bash
> 🐋 ❯ tree -a -I .git -I .devcontainer -I charts -I hack -I __pycache__ -I venv -I .git -I .pulumi
> .
> ├── README.md                        # Overview and documentation for the project
> ├── requirements.txt                 # Python dependencies for Pulumi and other Python tools used in the project
> ├── Pulumi.yaml                      # Main Pulumi project configuration file
> ├── Pulumi.pulumi-kubernetes.yaml    # Pulumi stack configuration specific to the pulumi-kubernetes plugin
> ├── __main__.py                      # Main Pulumi program file, entry point for Pulumi deployments
> ├── Makefile                         # Makefile for automating common tasks and commands
> ├── src                              # Source directory for the Pulumi components/modules
> │   ├── cdi                          # Component directory for Containerized Data Importer (CDI) deployments
> │   │   ├── deploy.py                # Deployment script for CDI
> │   │   └── __init__.py              # Makes Python treat the directories as containing packages
> │   ├── cert_manager                 # Component directory for Cert-Manager deployments
> │   │   ├── deploy.py                # Deployment script for Cert-Manager
> │   │   └── __init__.py              # Makes Python treat the directories as containing packages
> │   ├── cilium                       # Component directory for Cilium network policies deployments
> │   │   ├── deploy.py                # Deployment script for Cilium
> │   │   └── __init__.py              # Makes Python treat the directories as containing packages
> │   ├── kubevirt                     # Component directory for KubeVirt deployments
> │   │   ├── deploy.py                # Deployment script for KubeVirt
> │   │   └── __init__.py              # Makes Python treat the directories as containing packages
> │   └── lib                          # Library directory for shared scripts and utilities
> │       ├── helm_release_latest.py   # Utility script for deploying the latest Helm releases
> │       └── __init__.py              # Makes Python treat the directories as containing packages
> ├── LICENSE                          # License file for the project
> ├── .envrc                           # Environment configuration, typically for direnv to load environment variables
> ├── .github                          # Contains GitHub related configurations and workflows
> │   ├── assets                       # Assets for GitHub repository, like images for README.md
> │   ├── konductor                    # ghcr.io/pulumi/devcontainer based Devcontainer image for project
> │   └── workflows                    # GitHub Actions workflows
> │       └── ci.yaml                  # Continuous Integration workflow configuration for GitHub Actions
> ├── .gitignore                       # Specifies intentionally untracked files to ignore by Git
> ├── .gitmodules                      # Git Submodules configuration file
> ├── .kube                            # Kubernetes configuration directory
> │   ├── config                       # Kubernetes cluster connection and authentication information
> │   └── .gitkeep                     # Placeholder to keep the .kube directory in Git despite being empty
> └── .talos                           # Directory potentially for Talos OS configuration or related files
>     └── .gitkeep                     # Placeholder to keep the .talos directory in Git despite being empty
>
> 8 directories, 20 files
> ```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
