# Discoverer

## Info

Hosted in Bulgaria.

| [Docs](https://docs.discoverer.bg/index.html)
|

Support email: helpdesk@discoverer.bg

## Access

### Applying for time
Time on the Discoverer cluster can be obtained through [EuroHPC](https://access.eurohpc-ju.europa.eu/).

### Account creation

#### Activate account

https://docs.discoverer.bg/ssh_key_generation.html

Generate an ssh key

```
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_vega
```
To show the public part:
```
cat .ssh/id_ed25519_vega.pub
```

Send the public ssh key in reply to the welcome email from support, together with your name and institutional email address.

#### Install VPN client

https://docs.discoverer.bg/vpn_linux_command_line.html

You need to connect to the local network via VPN before you can access the machine. Follow the instructions to install the VPN client.

```
sudo add-apt-repository ppa:yuezk/globalprotect-openconnect
sudo apt-get update
sudo apt-get install globalprotect-openconnect
```

If you are on a new ubuntu OS, you can run into the problem that some of the required out-dated packages are missing. 
Issue
https://github.com/yuezk/GlobalProtect-openconnect/issues/351
You will need to install them manually before installing GlobalProtect-openconnect:
```
wget http://launchpadlibrarian.net/704701349/libwebkit2gtk-4.0-37_2.43.3-1_amd64.deb
wget http://launchpadlibrarian.net/704701345/libjavascriptcoregtk-4.0-18_2.43.3-1_amd64.deb
sudo dpkg --install libwebkit2gtk-4.0-37_2.43.3-1_amd64.deb
sudo dpkg --install libjavascriptcoregtk-4.0-18_2.43.3-1_amd64.deb
```

Once the client installed, you run it as root:
```
sudo openconnect --protocol=gp --interface=discoverer0 --user=myusername start.discoverer.bg
```
Where myusername should be replaced by the username provided by support. 
Remark that the first password asked is your sudo password of your PC, and the second is that for the VPN that was provided by support.

To check the VPN is working, ping the login node:
```
ping login.discoverer.bg
```

#### Update SSH config
```
Host discoverer
        User myusername
        Hostname login.discoverer.bg
```

### Login procedure

Launch the VPN client (see previous section).
Add the ssh key you generated previously to your ssh agent
```
ssh-add .ssh/id_ecdsa_discoverer
```
You can now login
```
ssh myusername@login.discoverer.bg
```

## Usage

### Getting and compiling the code
You can get the code through the usual way with git clone on the login node.

To compile, there are several option available. However, do not use intel compilers on discoverer, as they do not work properly with MPI on this machine.

For MPI, you can choose either openmpi or mpich. However, mpich does not work for 35 or more nodes due to a bug in mpi_alltoall:
https://github.com/pmodels/mpich/issues/6708

For more info, see
https://docs.discoverer.bg/compilers.html


### Running jobs

The system uses the SLURM job schedular. For more info see:

https://docs.discoverer.bg/writing_slurm_batch.html

Instead of choosing the general CPU partition cn, you can also directly choose the rack or nodes. See:
https://docs.discoverer.bg/resource_overview.html
Note that when choosing 24 nodes or less, the schedular seems to automatically put the job on nodes in the same IB group, if available. 

Be careful: slurmids are recycles quickly.

### Accounting

Info probably somewhere in here:
https://docs.discoverer.bg/computational_resources_allocation.html

