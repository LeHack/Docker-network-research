# Docker-network-research from a DevOps point of view

The goal of this project is to understand the concepts behind docker networking and how multi-container networks can be managed.

Index:
1. [Quick introduction to Docker](#quick-introduction-to-docker)
2. [Configuration layer 1](#configuration-layer-1)  
2.1. [Docker networking](#docker-networking)  
3. [Configuration layer 2](#configuration-layer-2)  
3.1. [Docker-compose](#docker-compose)  
3.2. [Ansible-playbook](#ansible-playbook-with-docker-registry) (with Docker Registry)  
4. [Configuration layer 3](#configuration-layer-3)  
4.1. [Docker in swarm mode](#docker-in-swarm-mode)  
4.2. [Ansible-container](#ansible-container)  
4.3. [Openshift](#openshift)  
4.4. [Kubernetes](#kubernetes)  

## Quick introduction to Docker

Docker is a set of tools which allow for easy creation of multiple lightweight virtual machines hosting different parts of an application we want to deploy (like a front-end server, a back-end server and a database).  
The process of encapsulation of every such part is called "building an image" in docker terminology. To create such an image, we have to:
1. start from a basic docker OS image  - such an image consists of a set of libraries and tools - excluding the kernel. Most Linux distributions are supported with various versions to choose from (e.g. Ubuntu, CentOS, RedHat)
2. install our application - copy the code, set paths etc. (like we would do it on a live server)

All of the steps necessary to perform this installation need to be described in a Dockerfile.  

You can build the provided example [Dockerfile](docker-compose/Dockerfile) be running:  
```docker build --rm -t app_example_image docker-compose```

Now if we would want to run this image, we have to start a container which is actually a copy of the created image. Any changes inside the container will live as long as the container does (you can start/pause/stop or remove it at any time). You can also attach [Volumes](https://docs.docker.com/engine/tutorials/dockervolumes/) to share directories between your host and the docker containers.  
Furthermore, we can run multiple containers of the same image at the same time in different arrangements (e.g. attached to different physical networks or with different ports exposed) and we will always get the same base system from the image.  
Finally we can also decide to "commit" a running container to an existing or a completely new image (think of it as: _Save_ vs _Save as_) to create a new snapshot from which you'll be able to create new containers.

## Configuration layer 1

To effectively manage the process of deploying applications (both for testing as for production purposes) we have to be able to automate it in a highly deterministic manner, which will allow us to test and find bugs in the deployment process itself before they hurt our production servers.  
To achieve that, we need to separate all of the tasks into a number of layers. The bigger the application, the more layers may be required to keep maintenance and operation costs at a minimum.  
The first layer is actually a Dockerfile which allows us to encapsulate the application code inside an image. For very small deployments, a single container may prove to be enough. Despite that, it is recommended to separate **different responsibilities** into **different containers** to be able to manage them effectively without bringing down the whole application each time we need to update the code or change configuration of one of the components. At the same time we should avoid logging into any running containers (for reasons other than debugging) and should ensure that we can simply restart them from a newly built image.  
This keeps the update process relatively easy and simple and will allow to spot most issues early on, even allowing for a fast rollback in the event that we encounter any serious issues with the new image.

### Docker networking

The ```docker network create``` command allows us to create a network which can be used by one or more local containers.

There are three types of network drivers supported out-of-the-box:
* **bridge** - allows to create isolated networks shared by all locally run containers.  
In order to provide communication with external hosts at least one port must be published and linked either to a random or specified port on the host machine (via NAT).
* **overlay** - allows to create a network which spans multiple docker hosts (using Virtual Extensible LAN tunnels), which can be only used with services (not ordinary containers). Therefore this only applies to running applications in docker swarm mode ([more on this below](#docker-in-swarm-mode)).
* **macvlan**/**ipvlan** - allows to create a virtual network stacked upon the selected host interface (directly bound to the hardware, thus giving most performance of the three). Multiple VLANs can be created for one physical interface and shared among multiple containers.
    * macvlan allows for multiple VLAN sub-interfaces with distinct mac/ip addresses (on one interface)
    * ipvlan allows for multiple VLAN sub-interfaces with a common mac address (allowing to circumvent hardware sub-interface mac count restrictions) with distinct ip addresses (using external DHCP must be coupled with using unique ClientIDs instead of the mac address)  

Examples:  
```docker network create --driver bridge --subnet 10.1.2.0/24 --gateway=10.1.2.100 test_nw``` - creates a local bridge based network with the given address namespace and gateway (routing)  
```docker run -it --network test_nw dockertest_web_1``` - runs a container from "dockertest_web_1" image using the created network (including correctly setup address and routing) 


From a devops point of view, the above is good and bad at the same time. The good part is that we can provide all application components with a network sufficiently customized to their needs. The bad part is that the appropriate commands need to be executed (with the exception of overlay + swarm) every time we setup a docker host.  
This may become a problem when were dealing with multiple machines and want our configuration to be well defined and reusable without having to rely on manually crafted bash scripts.

## Configuration layer 2

To efficiently manage multi-container and/or multi-instance deployments, we add another layer to our configuration using one of the following (depending on our project needs):
* [Docker-compose](#docker-compose)
* [Ansible-playbook](#ansible-playbook-with-docker-registry) (with Docker Registry)

### Docker-compose

This is a solution devised to allow for specifying how different docker containers work together as a larger application (including a slightly limited possibility to define and create docker networks) via a file called "docker-compose.yml".  
This configuration can then be used to easily manage the whole application.

Example (see full file in [docker-compose/docker-compose.yml](docker-compose/docker-compose.yml)):  
1. Network configuration example (version 3)
```
test_nw:  
  driver: bridge  
  ipam:  
    driver: default  
    config:  
      - subnet: 10.1.0.0/16
```  
2. Run it using ```docker-compose up```  
3. Tests it using:  
```
$ docker exec -it dockertest_nodes_1 ip addr  
...  
inet 10.1.0.3/16 scope global eth0  
...  

$ docker exec -it dockertest_nodes_1 ip route  
default via 10.1.0.1 dev eth0  
10.1.0.0/16 dev eth0  proto kernel  scope link  src 10.1.0.3
```  

:warning: Additional ipam configuration options like "gateway" are currently unavailable in version 3. 

The main drawback of docker-compose is again its scale of operation, as it is mainly designed to work with a single machine hosting multiple docker containers. To quote the official documentation:
> Compose is great for development, testing, and staging environments  

To use the above configuration across a number of machines, one must explicitly run: 
- on host1: ```docker-compose scale web=x```
- on host2: ```docker-compose scale nodes=y```

where **x** and **y** define how many individual containers are to be run for each "service" on the given host (:warning: there is a naming collision between what is considered a service in docker-compose and in docker in swarm mode).  
Also note that the above will not work if the _bridge_ network driver is used, though it could work with _macvlan_/_ipvlan_. 

A possible solution to this could be [Docker Stacks](https://docs.docker.com/compose/bundles/) which is an experimental feature that allows to bundle docker-compose files into a "multi-services distributable image format". But it is also very likely that it will end up obsoleted by Docker Swarm mode. 


### Ansible-playbook (with Docker Registry)

:warning: TODO

## Configuration layer 3

:warning: TODO: Describe need for third layer
* [Docker in swarm mode](#docker-in-swarm-mode)
* [Ansible-container](#ansible-container)


### Docker in swarm mode

Docker Swarm mode was developed to address the multi-host nature of most applications. The core idea is to work with image-based services (instead of containers) which include a lot more configuration, most importantly:
* automated healthchecks
* dns/network configurations
* resource requirements

Now a Swarm is actually a cluster of nodes with one or more nodes designated to be managers. Creating a simple swarm out of a number of machines sharing a common network is a very straightforward task. All you need to do is:
1. run ```docker swarm init``` on the machine designated to be a manager (you will be provided with a join-token)
2. run ```docker swarm join --token $token```  

Having all this information, the swarm manager can run and manage services on itself and its nodes. Here is an example of how to run a two node swarm using the [Dockerfile](docker-compose/Dockerfile):
1. build and tag the image: ```docker build --rm -t swarm_example docker-compose/```
2. create a service out of it: ```docker service create --name app_example swarm_example```

### Ansible-container

:warning: TODO


###  Openshift

:warning: TODO

###  Kubernetes

:warning: TODO