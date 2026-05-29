# Karolina Usage

## Info

Hosted by IT4Innovations in Czech Republic

Docs: https://docs.it4i.cz/

Support email: support@it4i.cz

IT4I profile settings: https://docs.it4i.cz/general/management/it4i-profile/


## Access

### Generate an SSH key

If not already done so, generate an ssh key:
```
ssh-keygen -t rsa
```

### Obtain a certificate to be able to send a digitally signed email

https://docs.it4i.cz/general/obtaining-login-credentials/obtaining-login-credentials/

You will need to request your account by sending a digitally signed email.
There are multiple options to obtain a certificate to be able to send such a signed email.

If you are part of CNRS you can generate a CNRS certificate, as explained here:
https://support.dr7.cnrs.fr/pages/exec.php/object/view/FAQ/25?exec_module=itop-portal-base&exec_page=index.php&portal_id=itop-portal
- Make sure the email you use to login to Janus is your CNRS email. If this is not the case, ask RH to change it.
- Go to https://sesame.cnrs.fr/ -> "Manage my certificates" and select CNRS
- Next, click on "Demander un nouveau certificat personel". Once generated, the certificate will be downloaded.

Alternatively, you can request a free Actalis S/MIME certificate:
https://www.actalis.com/request-s-mime-certificate
In this case, you will need to add a copy of an identification document such as a passport or drivers license to the email.

### Setup certificate into mail client

Once you have obtained the certificate, import it into your mail client (it will not work with webmail).
https://services.renater.fr/tcs/faq/tcs_personnes/utiliser#securiser_les_courriers_electroniques_a_l_aide_d_une_signature_numerique
On Linux, you can use Thunderbird:
- Settings -> Account settings (at the bottom) -> End-to-end encryption
- Scroll to the S/MIME section and click "manage certificates"
- Under "your certificates", press import and select the certificate you obtained in the previous step. Click ok.
- You can now set the certificate for digital signing.
- When writing an email, you will now have a menu S/MIME were you can mark that the email should be digitally signed.

### Request your IT4I account

You will need to request your account by sending a digitally signed email containing the information listed here:
https://docs.it4i.cz/general/obtaining-login-credentials/obtaining-login-credentials/
Once approved, you will receive an email with your username and a password for updating your profile settings.
You can now set your ssh key through the portal, and also change the password of the portal:
https://docs.it4i.cz/general/management/it4i-profile/

You will need to wait for a second email to confirm access to the different clusters, once your participation to the project has been approved by the project PI.

### Login to cluster

Add your ssh key to the key manager
```
$ ssh-add .ssh/id_ed25519_karolina
```
You can now connect to the cluster through ssh:
```
$ ssh myusername@karolina.it4i.cz
```

For convenience, you can add this information to your ssh config file:
```
Host karolina
        User it4i-tcolman
        Hostname karolina.it4i.cz
```
and simply use
```
ssh karolina
```

### Send a digitally sign email
- generate a cnrs certificate
  - ask RH to set your cnrs email in Réséda -> Liens aux implantations
  - https://support.dr7.cnrs.fr/pages/exec.php/object/view/FAQ/25?exec_module=itop-portal-base&exec_page=index.php&portal_id=itop-portal
  - https://sesame.cnrs.fr/ -> Manage my certificates
- import your cnrs email account into an email client
  - https://aide.core-cloud.net/si/messagerie/Documents/Configuration_logiciels_messagerie-Utilisateur%20avec%20messagerie%20v1.2%20Signets.pdf#page=27
- setup the certificate into the email client
  - https://services.renater.fr/tcs/faq/tcs_personnes/utiliser#securiser_les_courriers_electroniques_a_l_aide_d_une_signature_numerique
- send email
  - https://www.space-coe.eu/wiki/index.php?title=NCC_Access
  - https://docs.it4i.cz/general/obtaining-login-credentials/obtaining-login-credentials/
  - to : support@it4i.cz + petr.strakos@vsb.cz + lubomir.riha@vsb.cz
  - for project : OPEN-30-28 (previously DD-23-44, DD-23-100, FTA-23-25)
  - attach : public ssh key


### Create file ~/.ssh/config
```
Host *.karolina.it4i.cz
  ServerAliveInterval 60
  ForwardX11Timeout 1d
  TCPKeepAlive yes
  ForwardAgent yes
  ForwardX11 yes        # for Linux
# ForwardX11Trusted yes # for MacOSX
  Compression yes
  StrictHostKeyChecking no
  HashKnownHosts no

Host karolina
  User login
  HostName karolina.it4i.cz

Host karolina-*
  User login
  ProxyCommand ssh karolina nc `echo %h|sed -e 's/karolina-//g'` 22
```


## Running RAMSES

### Getting and compiling the code
You can get the code with git clone on the login node:
```
git clone https://git-cral.univ-lyon1.fr/hpc/space/ramses.git
```

A list of available compiler and mpi modules can be found here:
- https://docs.it4i.cz/software/compilers/
- https://docs.it4i.cz/software/mpi/mpi/


GNU:
Load the latest GCC compiler module and matching OpenMPI module
```
module load GCC/13.2.0
module load OpenMPI/4.1.6-GCC-13.2.0
```
To check what are versions are available, use 
```
module avail OpenMPI
```
In the Makefile, use compiler=GNU, mpif90
COMPILER = GNU
MPI = 1
MPIF90 = mpif90

INTEL:

### Submitting a job

- see example script: job_script.sh
- update the account with your project id (get it with command "groups $USER")
- for large output, the script has to be adapted:
```
SCRATCH_PATH=/scratch/project/my_project/my_login/my_job
mkdir -p ${SCRATCH_PATH}
cp ${EXEC} ${SCRATCH_PATH}/.
cp ${INPUT} ${SCRATCH_PATH}/.
cd ${SCRATCH_PATH} || exit
```

https://docs.it4i.cz/general/job-submission-and-execution/



Example job script `job.slm`:
```
#!/bin/bash -l
#SBATCH --job-name=test
#SBATCH --account=open-30-28
#SBATCH --partition=qcpu
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1
#SBATCH --time=00:10:00
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

module purge
module load GCC/13.2.0
module load OpenMPI/4.1.6-GCC-13.2.0

export DATE=`date +%F_%Hh%M`

srun ./ramses3d sedov3d_2048.nml > run_${DATE}_${SLURM_JOBID}.log
```

Submit your job with
```
$ sbatch job.slm
```

System alwas qllocates full nodes on cpu partition

## Machine specifications

https://docs.it4i.cz/karolina/compute-nodes/

### Processor

- Type: AMD Zen 2 EPYC 7H12
- 64 cores or 128 threads
- Cache:
    - L1i:	32 KB (per core)
    - L1d:	32 KB (per core)
    - L2:  512 KB (per core)
    - L3: 	16 MB (shared per 4 cores)
- clock speed: 2.1 GHz

### Architecture

- Each computing node has 2 processors, equalling 128 cores per node.
- 720 CPU nodes in total
- 256 GB of RAM per node
