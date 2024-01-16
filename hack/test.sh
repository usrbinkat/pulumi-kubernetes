
/usr/bin/docker create \
    --name magic \
    --label magics \
    --workdir /__w/iac-mesh-pac/iac-mesh-pac \
    --network=host \
    --user vscode \
    --privileged \
    --cpus 4 \
    --memory 8g \
    --workdir /home/runner/work/iac-mesh-pac/iac-mesh-pac \
    --user  \
    -e "HOME=/github/home" \
    -e GITHUB_ACTIONS=true \
    -e CI=true -v "/var/run/docker.sock":"/var/run/docker.sock" \
    -v "/home/runner/work":"/__w" \
    -v "/home/runner/runners/2.311.0/externals":"/__e":ro \
    -v "/home/runner/work/_temp":"/__w/_temp" \
    -v "/home/runner/work/_actions":"/__w/_actions" \
    -v "/opt/hostedtoolcache":"/__t" \
    -v "/home/runner/work/_temp/_github_home":"/github/home" \
    -v "/home/runner/work/_temp/_github_workflow":"/github/workflow"
    --entrypoint "tail" \
    ghcr.io/containercraft/konductor:latest "-f" "/dev/null"'^