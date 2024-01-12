# iac-mesh-pac

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/usrbinkat/iac-mesh-pac)

```bash
iac-mesh-pac on  main [!?]
🐋❯ tree -a -I .git -I .devcontainer
.
├── .devcontainer.json
├── .envrc
├── .gitignore
├── .gitmodules
├── hack
│   ├── ciliumnetpol.yaml
│   ├── cilium.yaml
│   └── kind.yaml
├── .kube
│   ├── config
│   └── .gitkeep
├── LICENSE
└── README.md

2 directories, 11 files
```

```bash
# Create Kind Cluster
kind create --config hack/kind.yaml

# Add cilium helm repo
# Deploy cilium
helm repo add cilium https://helm.cilium.io
helm upgrade --install cilium cilium/cilium --namespace kube-system --version 1.14.5 --values hack/cilium.yaml

# cilium status
cilium status --wait --wait-duration 2m0s

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
