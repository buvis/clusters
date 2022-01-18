## Fix client connectivity
1. Shell into wireguard pod
2. Activate packet forwarding when server starts: `sed -i /config/wg0.conf 's/PostUp = iptables/PostUp = sysctl net.ipv4.ip_forward=1; iptables/; sed -i /config/templates/server.conf 's/PostUp = iptables/PostUp = sysctl net.ipv4.ip_forward=1; iptables/'`
3. Restart the pod

## Add new peer
1. Add peer name to configmap.yaml, PEERS key
2. Restart wireguard server: `kubectl delete pod wireguard-0 -n network`

## Get peer configuration file
1. Make local copy of config directory: `kubectl cp -n network wireguard-0:config config`
2. Directory `config\peer_<name>` contains plain conf to use with wireguard client, but also QR code to connect mobile devices
3. Delete the local copy immediately as it contains secrets

## References
- [Docker image](https://github.com/linuxserver/docker-wireguard)
- [Manifests inspiration](https://github.com/ivanmorenoj/k3s-pihole-wireguard/blob/main/k8s/05-wireguard.yaml)
- [Issue with routing](https://github.com/linuxserver/docker-wireguard/issues/78#issuecomment-739321794)
