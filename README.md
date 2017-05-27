# Docker-network-research

The goal of this project is to understand the concepts behind docker networking and how multi-container networks are managed.

## Docker

To start off we need a docker image (build from a Dockerfile) and we run it as a simple container.
The ```docker network create``` command allows us to create a network which can be used by one or more local containers.
    
There are three types of network drivers supported out-of-the-box:
* bridge - allows to create isolated networks shared by all locally run containers. 
In order to provide communication with external hosts at least one port must be published and linked either to a random or specified port on the host machine (via NAT).
* overlay - allows to create a network which spans multiple docker hosts (using Virtual Extensible LAN tunnels), which can be only used with services
(not ordinary containers). Therefore this only applies to running applications in docker swarm mode (more on this below).
* macvlan/ipvlan - allows to create a virtual network stacked upon the selected host interface (directly bound to the hardware, thus giving most performance of the three). 
Multiple VLANs can be created for one physical interface and shared among multiple containers. 
** macvlan allows for multiple VLAN sub-interfaces with distinct mac/ip addresses (on one interface)
** ipvlan allows for multiple VLAN sub-interfaces with a common mac address (allowing to circumvent hardware sub-interface mac count restrictions) with distinct ip addresses (using external DHCP must be coupled with using unique ClientIDs instead of the mac address)  

Examples:
```docker network create --driver bridge --subnet 10.1.2.0/24 --gateway=10.1.2.100 test_nw``` - creates a local bridge based network with the given address namespace and gateway (routing)
```docker run -it --network test_nw dockertest_web_1``` - runs a container from "dockertest_web_1" image using the created network (including correctly setup address and routing) 

From a devops point of view, the above is good and bad at the same time. The good part is that we can provide all application components with a network sufficiently customized to their needs. 
The bad part is that the appropriate commands need to be executed (with the exception of overlay + swarm) every time we setup a docker host. 
This may become a problem when were dealing with multiple machines and want our configuration to be well defined and reusable without having to rely on manually crafted bash scripts.

To overcome this we can add another layer to our configuration using one of the following (depending on our project needs):
* Docker-compose
* Docker in swarm mode
* Ansible-playbook


## Docker-compose

This is a solution devised to allow for specifying how different docker containers work together as a larger application (including the possibility to define docker networks) via a file called "docker-compose.yml". 
This configuration can then be used to easily manage the whole application.

Example (see full file in examples/docker-compose/docker-compose.yml):
1. Network configuration example
>  test_nw:
>    driver: bridge
>    ipam:
>      driver: default
>      config:
>        - subnet: 10.1.0.0/16

2. Running: ```docker-compose up```

3. Testing:
```docker exec -it dockertest_nodes_1 ip addr```
>  ...
>  inet 10.1.0.3/16 scope global eth0
>  ...

```docker exec -it dockertest_nodes_1 ip route```
>  default via 10.1.0.1 dev eth0 
>  10.1.0.0/16 dev eth0  proto kernel  scope link  src 10.1.0.3 


