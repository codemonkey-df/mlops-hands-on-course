# k3d cluster definition for the whole course (template).
# `make cluster-up` renders it with envsubst (fills ${SERVER_IP}) and creates the cluster.
#
# k3d runs every Kubernetes "node" as a Docker container, so the cluster lives
# entirely inside this LXC and can be deleted/recreated in ~30 seconds.
apiVersion: k3d.io/v1alpha5
kind: Simple
metadata:
  name: mlops                     # cluster name -> kube context is "k3d-mlops"
servers: 1                        # control-plane nodes (1 is plenty for learning)
agents: 2                         # workers; 2 lets you watch pods spread across nodes
image: rancher/k3s:v1.35.5-k3s1   # pinning k3s = pinning the Kubernetes version
ports:
  # k3d puts a small nginx "serverlb" container in front of the nodes.
  # These map LXC ports -> the Traefik ingress controller inside the cluster.
  # Every web UI is reachable as http://<app>.${SERVER_IP}.nip.io:8080
  - port: 8080:80
    nodeFilters: [server:0]
  - port: 8443:443
    nodeFilters: [loadbalancer]
volumes:
  # LXC gotcha: kubelet opens /dev/kmsg (kernel log) to detect OOM kills.
  # Inside a Proxmox LXC the cgroup device policy denies reading the real device
  # ("open /dev/kmsg: operation not permitted"), even for privileged containers.
  # Binding /dev/null over it lets kubelet start; the only loss is that kubelet
  # can't read kernel OOM events (pods are still OOMKilled and reported).
  # Proper host-side fix instead: add `lxc.cgroup2.devices.allow: c 1:11 rwm`
  # to /etc/pve/lxc/<id>.conf and restart the LXC.
  - volume: /dev/null:/dev/kmsg
    nodeFilters: [server:*, agent:*]
hostAliases:
  # Written into /etc/hosts of every node container, so pods/containerd can
  # resolve services that run *outside* the cluster (Harbor, Gitea in Compose).
  - ip: ${SERVER_IP}
    hostnames: [harbor.local, gitea.local]
registries:
  # Harbor (Module 7) speaks plain HTTP. containerd inside each k3s node must be
  # told explicitly, otherwise pulls fail with
  # "http: server gave HTTP response to HTTPS client".
  config: |
    mirrors:
      "harbor.local:8085":
        endpoint:
          - http://harbor.local:8085
options:
  k3s:
    extraArgs:
      # Evict pods before a node runs completely out of RAM/disk (protects the LXC).
      - arg: --kubelet-arg=eviction-hard=memory.available<500Mi,nodefs.available<5%
        nodeFilters: [server:*, agent:*]
  kubeconfig:
    updateDefaultKubeconfig: true   # merges the context into ~/.kube/config
    switchCurrentContext: true      # `kubectl` now talks to this cluster
