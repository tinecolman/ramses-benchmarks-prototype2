# Vega Usage

## Info

Hosted at IZUM, Maribor, Slovenia

Docs: https://doc.vega.izum.si/

Support email: support@sling.si

## Access

### Account creation

To obtain an account, you need to send an email to support with attached the filled and signed PDA form and a public ssh key.

The form can be found here:
https://doc.vega.izum.si/dpa/
Fill in your contact details and your HPC project.
In the case of ramses simulations, the user data will usually consist of the ramses source code, which does not contain personal data.

Instruction for the ssh key can be found here:
https://en-vegadocs.vega.izum.si/ssh/

Generate the key:
```
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_vega
```
Show the the public part to add to your email:
```
cat .ssh/id_ed25519_vega.pub
```
To add your key to the ssh agent:
```
ssh-add .ssh/id_ed25519_vega
```

### Setup two-factor authentication

Follow the instructions in the email send by support.
Install the authenticator app mentioned in the email on your phone.
To get the QR code that is needes as input, on your computer, ssh to 
```
ssh <username>@otp.vega.izum.si
```
Scan the QR code in the authenticator app on your phone. Confirm the link by inputting the code now displayed on your phone. 
Write down the secret key outputted in the OTP ssh terminal. You can use the key later to configure the OTP generator on other devices.

### Login to cluster

Add your key to the ssh agent:
```
ssh-add .ssh/id_ed25519_vega
```
You can now connect
```
ssh <username>@login.vega.izum.si
```
It will ask for the 6 digit code displayed on the authenticator app on your phone.

SSH config:
```
# Vega at IZUM, Slovenia
Host vega
        User <username>
        Hostname login.vega.izum.si            
```

## Running RAMSES

### Getting and compiling the code

You can get the code with git clone:
```
git clone https://git-cral.univ-lyon1.fr/hpc/space/ramses.git
```

There are several compilers and mpi versions available as loadable modules, see:
- https://doc.vega.izum.si/compilers/
- https://doc.vega.izum.si/mpi/

Since the machine is made up of AMD processors, the following modules are a good start:
```
module load GCC
module load openmpi/gnu/4.1.2.1
```

### Submitting a job

Use `sbatch`. Example job script:
```
#!/bin/bash
#SBATCH --job-name=sedov16
#SBATCH --partition=cpu
#SBATCH --nodes=16
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1
#SBATCH --exclusive
#SBATCH --time=00:10:00
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

module load GCC
module load openmpi/gnu/4.1.2.1

export DATE=`date +%F_%Hh%M`

srun ./ramses3d sedov3d_2048.nml > run_${DATE}_${SLURM_JOBID}.log
```

## Specifications CPU partition

### Processor

- Type: AMD Epyc 7H12
- 64 cores or 128 threads
- Cache:
    - L1: 	 96 KB (per core)
    - L2: 	512 KB (per core)
    - L3: 	256 MB (shared)

### Architecture

- Each computing node has 2 processors, equalling 128 cores per node.
- A total of 960 compute nodes divided into standard (8 racks) and large memory nodes (2 racks).
- Each rack has 96 nodes, divided into 32 blades of 3 nodes.

Standard nodes:
- total of 768 nodes
- 256 GB of RAM per node

High memory nodes:
- total of 192 nodes
- 1 TB of RAM per node

## SPACE notes
minimum number of nodes for the sedov 2048 test is more then 12???