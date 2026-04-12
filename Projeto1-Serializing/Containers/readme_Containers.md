# Containers (Docker Compose)

This runs the same Sender/Receiver XML (JAXB) serialization demo, but in two Docker containers connected by the default Compose network.

## Prerequisites
- Docker Desktop (Windows)
- From the repo root, you can run `docker compose` commands

## How it works
- `receiver` runs `java Receiver` and listens on port `5000`
- `sender` runs `java Sender` and connects to `receiver:5000` using env vars:
  - `RECEIVER_HOST=receiver`
  - `RECEIVER_PORT=5000`

## Run
From `IS/Projeto1-Serializing/Containers/setup`:

1) Start the receiver:
- `docker compose up --build receiver`

2) In another terminal, run the sender once:
- `docker compose run --rm sender`

3) Stop receiver:
- Ctrl+C in the receiver terminal

## Notes
- The Java sources used for containers live in `Containers/src/`.
- Docker/Compose setup files live in `Containers/setup/`.
- `Sender` accepts host/port via args or env vars; by default (in the container version) it connects to `receiver:5000`.

To support connection between two different machines we will use wireguard according to this blog:

https://uncloud.run/blog/connect-docker-containers-across-hosts-wireguard/

# Machine 1
docker network create --subnet 10.200.1.0/24 -o com.docker.network.bridge.trusted_host_interfaces="wg0" multi-host
# Machine 2
docker network create --subnet 10.200.2.0/24 -o com.docker.network.bridge.trusted_host_interfaces="wg0" multi-host

Verify Traffic:

iptables -I INPUT -p udp --dport 51820 -j ACCEPT

Machine 1:

[Interface]
ListenPort = 51820
PrivateKey = <replace with 'privatekey' file content from Machine 1>

[Peer]
PublicKey = <replace with 'publickey' file content from Machine 2>
# IP ranges for which a peer will route traffic: Docker subnet on Machine 2
AllowedIPs = 10.200.2.0/24
# Public IP of Machine 2
Endpoint = 157.180.72.195:51820
# Periodically send keepalive packets to keep NAT/firewall mapping alive
PersistentKeepalive = 25

Machine 2:

[Interface]
ListenPort = 51820
PrivateKey = <replace with 'privatekey' file content from Machine 2>

[Peer]
PublicKey = <replace with 'publickey' file content from Machine 1>
# IP ranges for which a peer will route traffic: Docker subnet on Machine 1
AllowedIPs = 10.200.1.0/24
# Reachable endpoint of Machine 1
# Endpoint =
# Periodically send keepalive packets to keep NAT/firewall mapping alive
PersistentKeepalive = 25