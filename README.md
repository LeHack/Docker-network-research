# Docker-network-research from a DevOps point of view

The goal of this project was to understand the concepts behind docker networking and how multi-container, multi-host application can be managed using Docker and Ansible tools.

## Index:
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

You can build the provided example [Dockerfile](docker-compose/Dockerfile) by running:  
```docker build --rm -t app_example_image docker-compose```

Now if we would want to run this image, we have to start a container which is actually a copy of the created image. Any changes inside the container will live as long as the container does (you can start/pause/stop or remove it at any time).  
It is common to create one image and then run it in a number of containers (usually dispersed among a number of physical hosts) which allows for easy scaling of an application. Furthermore, each container can easily be run with different parameters, expose different ports or be attached to a different network.  
Finally we can also decide to "commit" a running container to an existing or a completely new image (think of it as: _Save_ vs _Save as_) to create a new snapshot from which you'll be able to create other containers (see ```docker commit --help```).  

## Configuration layer 1

To effectively manage the process of deploying applications (both for testing and production purposes) we have to be able to automate it in a highly deterministic manner, which will allow us to test and find bugs in the deployment process itself before they hurt our production servers.  
To achieve that, we need to separate all of the deployment tasks into a number of layers. The bigger the application, the more layers may be required to keep maintenance and operation costs at a minimum.  
The first layer is actually the already mentioned Dockerfile which allows us to encapsulate the application code inside an image. For very small deployments, a single container may prove to be enough. It is however recommended to separate **different responsibilities** into **different containers** to be able to manage them effectively without bringing down the whole application each time we need to update the code or change configuration of one of the components. At the same time we should avoid logging into any running containers (for reasons other than debugging) and should ensure that we can simply restart them from a newly built image.  
This keeps the update process relatively easy and simple and will allow to spot most issues early on. It might even allow for a quick rollback in the event that we encounter any serious issues after releasing a new version of our application.

### Docker networking

The ```docker network create``` command allows us to create a network which can be used by one or more local containers.

There are three types of network drivers supported out-of-the-box:
* **bridge** - allows to create isolated networks shared by all locally run containers.  
In order to provide communication with external hosts at least one port must be published and linked either to a random or specified port on the host machine (via NAT).
* **overlay** - allows to create a network which spans multiple docker hosts (using Virtual Extensible LAN tunnels), which can be only used with services (not ordinary containers). Therefore this _mostly_ applies to running applications in docker swarm mode ([more on this below](#docker-in-swarm-mode)).
* **macvlan**/**ipvlan** - allows to create a virtual network stacked upon the selected host interface (directly bound to the hardware, thus giving most performance of the three). Multiple VLANs can be created for one physical interface and shared among multiple containers.
    * macvlan allows for multiple VLAN sub-interfaces with distinct mac/ip addresses (on one interface)
    * ipvlan allows for multiple VLAN sub-interfaces with a common mac address (allowing to circumvent hardware sub-interface mac count restrictions) with distinct IP addresses (in the case of an external DHCP you must switch to using unique ClientIDs instead of the mac address)  

Examples:  
```docker network create --driver bridge --subnet 10.1.4.0/24 --gateway=10.1.4.100 test_nw``` - creates a local bridge based network with the given address namespace and gateway (routing)  
```docker run -it --network test_nw app_example_image``` - runs a container from the "app\_example\_image" using the created network (including correctly setup address and routing)  


From a DevOps point of view, the above is good and bad at the same time. The good part is that we can provide all application components with a network sufficiently customized to their needs. The bad part is that the appropriate commands need to be executed (with the exception of overlay + swarm) every time we setup a docker host.  
This may become a problem when were dealing with multiple machines as we should aim to keep our configuration simple, well defined and reusable without having to rely on manually crafted scripts and solutions.

## Configuration layer 2

To efficiently manage multi-container and/or multi-instance deployments, we can add another layer to our configuration using one of the following (depending on our project needs):
* [Docker-compose](#docker-compose)
* [Ansible-playbook](#ansible-playbook-with-docker-registry) (with Docker Registry)

### Docker-compose

This is a solution devised to allow for specifying how different docker containers work together as a larger application (including a slightly limited possibility to define and create docker networks) via a file called "docker-compose.yml".  
This configuration can then be used to easily manage the whole application.

#### Docker-compose example
See full file in [docker-compose/docker-compose.yml](docker-compose/docker-compose.yml):  
1. Network configuration example (version 3)
```
test_nw:  
  driver: bridge  
  ipam:  
    driver: default  
    config:  
      - subnet: 10.1.4.0/24
```  
2. Run it using ```docker-compose up``` (from within the docker-compose directory)  
3. Note that the container names are generated automatically from project directory, service name and instance number:  
```
$ docker container ls --format "table {{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Networks}}"  
CONTAINER ID        IMAGE                 NAMES                   NETWORKS  
cf1c4e51ab0b        dockercompose_nodes   dockercompose_nodes_1   dockercompose_test_nw,dockercompose_test_nw2  
a9f9361f75b1        dockercompose_web     dockercompose_web_1     dockercompose_test_nw  
```  
4. Check dockercompose\_nodes\_1, which is now attached to both configured networks:  
```
$ docker exec -it dockercompose_nodes_1 ip addr | grep -E "inet.+eth"  
    inet 10.1.4.3/24 scope global eth0  
    inet 10.2.3.2/24 scope global eth1  

$ docker exec -it dockercompose_nodes_1 ip route  
default via 10.1.4.1 dev eth0  
10.1.4.0/24 dev eth0  proto kernel  scope link  src 10.1.4.3   
10.2.3.0/24 dev eth1  proto kernel  scope link  src 10.2.3.2  

$ docker exec -it dockercompose_nodes_1 ping -c 1 10.1.4.2  
PING 10.1.4.2 (10.1.4.2): 56 data bytes  
64 bytes from 10.1.4.2: icmp_seq=0 ttl=64 time=0.270 ms  

$ docker exec -it dockercompose_nodes_1 ping -c 1 10.2.3.1  
PING 10.2.3.1 (10.2.3.1): 56 data bytes  
64 bytes from 10.2.3.1: icmp_seq=0 ttl=64 time=0.172 ms  
```  

:warning: Additional ipam configuration options like "gateway" are currently unavailable in version 3. Thus to get the same network as in the previous example, we need to set it manually inside each container, e.g.:  
```docker container ls --format "{{.Names}}" | xargs -n 1 -iCNT docker exec --privileged CNT su -c "ip route del default && ip route add default via 10.1.4.100"```  
Also note the _--privileged_ flag when running _docker exec_. You must grant extra permissions to the _exec_ command, otherwise routing cannot be altered from a container (which is actually a good thing).

:warning: If you modify your [docker-compose.yml](docker-compose/docker-compose.yml) network configuration and try to run ```docker-compose up``` again, it will use the already existing networks (built during the first launch). In order to update the new configuration, you have to remove the existing networks using (in this example): ```docker network rm dockercompose_test_nw dockercompose_test_nw2```  


#### Summary
The main drawback of docker-compose is its scale of operation, as it is mainly designed to work with a single machine hosting multiple docker containers. To quote the official documentation:
> Compose is great for development, testing, and staging environments  

To use the above configuration across a number of machines, one must explicitly run: 
- on host1: ```docker-compose scale web=x```
- on host2: ```docker-compose scale nodes=y```

where **x** and **y** define how many individual containers are to be run for each "service" on the given host (:warning: there is a naming collision between what is considered a service in docker-compose and in docker in swarm mode).  
Also note that the above will not work if the _bridge_ network driver is used, though it could work with _macvlan_/_ipvlan_. 

A possible solution to this could be [Docker Stacks](https://docs.docker.com/compose/bundles/) which is an experimental feature that allows to bundle docker-compose files into a "multi-services distributable image format". But it is also very likely that it will end up obsoleted by Docker Swarm mode. 


### Ansible-playbook (with Docker Registry)

[Ansible](https://docs.ansible.com/ansible/index.html) is basically a supercharged SSH client with loads of modules that can be used to perform and assert certain configuration tasks like creating users and paths, ensuring correct permissions and configurations, sending notifications via a plethora of messaging solutions (e-mail, sms, slack etc.) ...and handling docker.

Thus an even better approach is to take advantage of an Ansible playbook, which is a group of tasks (also called a scenario) that can be run using Ansible on a set of machines in parallel.  
An example of how this could be achieved can be found in the [ansible-playbook](ansible-playbook/) directory.  
This example is composed of:  
- [deploy.yml](ansible-playbook/deploy.yml) - the playbook (scenario)
- [testing/inventory](ansible-playbook/testing/inventory) - list of staging hosts that we want to deploy to
- [testing/group_vars/all](ansible-playbook/testing/group_vars/all) - common settings for testing machines
- [production/inventory](ansible-playbook/production/inventory) - list of production hosts that we want to deploy to
- [production/group_vars/all](ansible-playbook/production/group_vars/all) - common settings for production machines
- [production/host_vars/web-back2.prod](ansible-playbook/production/host_vars/web-back2.prod) - some very specific settings override for the web-back2.prod and web-back3.prod machines (note that [host_vars/web-back3.prod](ansible-playbook/production/host_vars/web-back3.prod) can be a symlink)

Now in order to run a playbook deployment, you need to follow these steps:
1. [Prepare at least one virtual machine](#virtual-machine) with host connectivity and docker installed.
2. [Setup a docker registry on your host](#docker-registry)
3. Update the host names (in the inventory files) in the above example to point to correct host names (make sure your virtual machine has a **resolvable** hostname assigned and that you can ping it from your host).
4. [Perform the deployment using ansible-playbook](#deployment).

#### Virtual Machine
There are [plenty](http://www.itworld.com/article/2919329/virtualization/how-to-setup-and-create-your-own-virtualbox-linux-machines.html) of [guides](http://www.brianlinkletter.com/how-to-use-virtualbox-to-emulate-a-network/) on how to setup up a simple virtual machine, so I won't be covering that part here. From my own experience I can recommend using VirtualBox with a bridged network and a very basic Ubuntu server (make sure to install "python-pip").

#### Docker registry
This part is actually [pretty well explained here](https://docs.docker.com/registry/deploying/) with the only exception, that we want to have the registry to be reachable from within our VBox host-only network. The simplest way to achieve this is to change dockerd run params (DOCKER_OPTS in /etc/default/docker on Ubuntu) to contain the following two params:  
```-H 10.0.0.1 --insecure-registry 10.0.0.1:5000```  
and restart the docker service.  

:warning: Of course "10.0.0.1" is only an example and you should replace this with the IP of the interface to which your Virtual machines are bridged. The important part is to make sure that the docker registry and the deployment nodes can reach each other.

:warning: The same **insecure-registry** option must be also set in the Virtual machine docker. Be aware that this is only acceptable for learning purposes. For any kind of real-world usage you **must** generate some SSL certificates and set it up with HTTPS enabled.

:warning: From this moment, docker will be only available via the specified IP (not via sock), so you must make sure that you set the environment variable DOCKER_HOST to the appropriate IP, e.g.:  
```export DOCKER_HOST=10.0.0.1:2375```


Finally we can fire up the registry container as described in the tutorial:  
```docker run -d -p 5000:5000 --restart=always --name registry registry:2```  
**or** leave it to our deployment playbook below...

#### Deployment
Now before we actually deploy anything, we need to have something to deploy. If you followed the steps in [the docker introduction](#quick-introduction-to-docker) you should have an "app\_example\_image" image ready.  
To push it to our local registry, we _could_ run:
* ```docker tag app_example_image 10.0.0.1:5000/app_example_image``` - to properly tag the existing image for use via the registry  
* ```docker push 10.0.0.1:5000/app_example_image``` - to push the image layers into the registry   
* ```docker pull 10.0.0.1:5000/app_example_image``` - to fetch the image from the registry on each deployment machine   
* and finally [a variation of the commands from docker-compose example](docker-compose-example) to setup the network

But where's the fun in that?  
After all we have Ansible modules which can do all of it for us, in parallel, on all configured hosts and then automatically run the image as containers.  
Inspect the [deploy.yml](ansible-playbook/deploy.yml) and the [testing/group_vars/all](ansible-playbook/testing/group_vars/all) (remember to update the IP address). If everything looks right, just run and enjoy:  
```ansible-playbook -i testing deploy.yml```  

:arrow_right: You can run the above command multiple times, correcting any issues as you go. Most of the modules used in the playbook can verify their current state before taking any action. Thus if a tasks goal is already met, you'll see a green "[ok]" next to it's hostname.  

When it's done, go to port 80 of the deployment host and verify that you see the testing page.  
You can verify the settings using... you guessed it, Ansible!
```
$ ansible back -i testing -m shell -a "docker container ls --format 'table {%raw%}{{.Image}}\t{{.Names}}\t{{.Ports}}\t{{.Networks}}{%endraw%}' && docker exec app_example_nodes ip route"  
web-back1.testing | SUCCESS | rc=0 >>  
IMAGE                                    NAMES               PORTS                         NETWORKS  
10.0.0.1:5000/app_example_image:v3       app_example_nodes   239.255.0.42:8000->8000/tcp   test_nw,test_nw2  
10.0.0.1:5000/app_example_image:v3       app_example_web     0.0.0.0:80->8000/tcp          test_nw  
default via 10.1.4.100 dev eth0  
10.1.4.0/24 dev eth0  proto kernel  scope link  src 10.1.4.2  
10.2.3.0/24 dev eth1  proto kernel  scope link  src 10.2.3.2  

web-back2.testing | SUCCESS | rc=0 >>  
IMAGE                                    NAMES               PORTS                         NETWORKS  
10.0.0.1:5000/app_example_image:v3       app_example_nodes   239.255.0.42:8000->8000/tcp   test_nw,test_nw2  
10.0.0.1:5000/app_example_image:v3       app_example_web     0.0.0.0:80->8000/tcp          test_nw  
default via 10.1.4.100 dev eth0  
10.1.4.0/24 dev eth0  proto kernel  scope link  src 10.1.4.2  
10.2.3.0/24 dev eth1  proto kernel  scope link  src 10.2.3.2  

web-back3.testing | SUCCESS | rc=0 >>  
IMAGE                                    NAMES               PORTS                         NETWORKS  
10.0.0.1:5000/app_example_image:v3       app_example_nodes   239.255.0.42:8000->8000/tcp   test_nw2,test_nw  
10.0.0.1:5000/app_example_image:v3       app_example_web     0.0.0.0:80->8000/tcp          test_nw  
default via 10.1.4.100 dev eth0  
10.1.4.0/24 dev eth0  proto kernel  scope link  src 10.1.4.2  
10.2.3.0/24 dev eth1  proto kernel  scope link  src 10.2.3.2  
```

#### Multiple host spanning network

Now lets make things really interesting and get all of those containers share a single common network. For this we will need to utilize the _Overlay_ network driver. Here's how to do it in three _easy_ steps:

1. First we need to select some key-value store, which will allow the _Overlay_ driver to exchange data between hosts.  
We get to choose from the following options:
    * Consul  
    * Etcd  
    * Apache ZooKeeper
  
   The following example uses a Consul image from Docker Hub, so you don't have to install anything.  

2. Next we have to update the way our docker engine is started ([same place we changed when setting up the registry](#docker-registry)) by adding the following two options to our own docker:  
```
--cluster-store=consul://127.0.0.1:8500 --cluster-advertise=10.0.0.1:2375
```  
and on each Virtual machine with:  
```
--cluster-store=consul://127.0.0.1:8500 --cluster-advertise=EXT_IF:2375
```  
and remember to *restart the dockers*.  
:warning: EXT_IF may be _eth0_, _enp0s3_ or something else. It all depends on your virtual machine configuration/OS.
  
3. Inspect and run the [deploy-overlay.yml](ansible-playbook/deploy-overlay.yml) playbook:  
```ansible-playbook -i testing deploy-overlay.yml```  

When all is set we can inspect the newly created network:  
```
$ ansible all -i testing -m shell -a 'docker container ls --format "table {%raw%}{{.Image}}\t{{.Names}}\t{{.Ports}}\t{{.Networks}}{%endraw%}" && export hostname=`hostname -s` && docker exec app_example_nodes-$hostname ip addr | grep -E "inet.+eth"'  
web-back1.testing | SUCCESS | rc=0 >>  
IMAGE                                    NAMES                         PORTS                         NETWORKS  
10.0.0.1:5000/app_example_image:v3       app_example_nodes-web-back1   239.255.0.42:8000->8000/tcp   test_overlay  
10.0.0.1:5000/app_example_image:v3       app_example_web-web-back1     0.0.0.0:80->8000/tcp          test_overlay  
consul                                   consul-client                                               host  
    inet 10.10.10.7/24 scope global eth0  
    inet 172.18.0.3/16 scope global eth1  

web-back2.testing | SUCCESS | rc=0 >>  
IMAGE                                    NAMES                         PORTS                         NETWORKS  
10.0.0.1:5000/app_example_image:v3       app_example_nodes-web-back2   239.255.0.42:8000->8000/tcp   test_overlay  
10.0.0.1:5000/app_example_image:v3       app_example_web-web-back2     0.0.0.0:80->8000/tcp          test_overlay  
consul                                   consul-client                                               host  
    inet 10.10.10.6/24 scope global eth0  
    inet 172.18.0.3/16 scope global eth1  

web-back3.testing | SUCCESS | rc=0 >>  
IMAGE                                    NAMES                         PORTS                         NETWORKS  
10.0.0.1:5000/app_example_image:v3       app_example_nodes-web-back3   239.255.0.42:8000->8000/tcp   test_overlay  
10.0.0.1:5000/app_example_image:v3       app_example_web-web-back3     0.0.0.0:80->8000/tcp          test_overlay  
consul                                   consul-client                                               host  
    inet 10.10.10.5/24 scope global eth0  
    inet 172.18.0.3/16 scope global eth1  
```  
:arrow_right: Note that the container names had to be altered (postfixed with the domain name), because now they need to be unique in the network scope. You can see why by running [nmap](https://nmap.org) from one of the running containers:  
```
root@446d7f20203b:/project# nmap -sP 10.10.10.0/24  

Starting Nmap 6.47 ( http://nmap.org ) at 2017-05-31 22:23 UTC  
Nmap scan report for 10.10.10.1  
Host is up (0.000082s latency).  
MAC Address: 02:EB:59:31:28:E7 (Unknown)  
Nmap scan report for app_example_web-web-back1.test_overlay (10.10.10.2)  
Host is up (0.000012s latency).  
MAC Address: 02:42:0A:0A:0A:02 (Unknown)  
Nmap scan report for app_example_web-web-back2.test_overlay (10.10.10.3)  
Host is up (0.000018s latency).  
MAC Address: 02:42:0A:0A:0A:03 (Unknown)  
Nmap scan report for app_example_web-web-back3.test_overlay (10.10.10.4)  
Host is up (0.000010s latency).  
MAC Address: 02:42:0A:0A:0A:04 (Unknown)  
Nmap scan report for app_example_nodes-web-back3.test_overlay (10.10.10.5)  
Host is up (0.000010s latency).  
MAC Address: 02:42:0A:0A:0A:05 (Unknown)  
Nmap scan report for app_example_nodes-web-back1.test_overlay (10.10.10.7)  
Host is up (0.000016s latency).  
MAC Address: 02:42:0A:0A:0A:07 (Unknown)  
Nmap scan report for 446d7f20203b (10.10.10.6)  
Host is up.  
Nmap done: 256 IP addresses (7 hosts up) scanned in 3.50 seconds  
```  
As you can see, the container names are now *fully resolvable container hostnames* (the final host is shown as "446d7f20203b" because that's where nmap was run from, hence it returned the /etc/hosts match instead. But of course you can also reach it via _app\_example\_nodes-web-back2.test\_overlay_).  

:warning: Contrary to the previous example, here you need to have a "master" host, which hosts the _Consul cluster leader_:  
```
$ docker exec -it dev-consul consul members  
Node               Address        Status  Type    Build  Protocol  DC  
docker-host        10.0.0.1:8301  alive   server  0.8.3  2         dc1  
web-back1.testing  10.0.0.2:8301  alive   client  0.8.3  2         dc1  
web-back2.testing  10.0.0.3:8301  alive   client  0.8.3  2         dc1  
web-back3.testing  10.0.0.4:8301  alive   client  0.8.3  2         dc1  
```  
Of course you could also set it up on one of the deployment hosts.

:warning: Be sure to consult [Consul documentation](https://www.consul.io/docs/guides/index.html) before using this example beyond your devel environment because it is simplified and therefore not safe for production use.

## Configuration layer 3

So far so good, but what if we don't really want to have to care about which service is run on which server? What if all we care for are service instance counts and resource utilization?  
Have no fear, that's exactly where the third configuration layer comes in to take us even further:
* [Docker in swarm mode](#docker-in-swarm-mode)
* [Ansible-container](#ansible-container)


### Docker in swarm mode

Docker Swarm mode was developed to address the multi-host nature of most large applications. The core idea is to work with image-based services which replace the use of containers and include a lot more configuration, most importantly:
* automated health checks
* dns/network configurations
* resource requirements

A swarm is actually a cluster of nodes with one or more nodes designated to be managers. Creating a simple swarm out of a number of machines sharing a common network is a very straightforward task. All you need to do is:
1. run ```docker swarm init``` on the machine designated to be a manager
2. run ```docker swarm join --token $TOKEN $MANAGER_IP:2377``` (you will be provided with the join command when running init)  

Having all this information, the swarm manager can run and manage services on itself and its nodes. Here is an example of how to run a two node swarm using the [Dockerfile](docker-compose/Dockerfile):
1. [build and tag the image](#quick-introduction-to-docker)
2. create a service out of it: ```docker service create --name service_example app_example_image```
...

:warning: Important quote from the docs: "For testing purposes it is OK to run a swarm with a single manager. If the manager in a single-manager swarm fails, your services will continue to run, but you will need to create a new cluster to recover."

### Ansible-container

:warning: TODO


###  Openshift

:warning: TODO

###  Kubernetes

:warning: TODO