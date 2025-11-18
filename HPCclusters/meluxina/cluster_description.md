# MeluXina

## Info

Hosted by LuxProvide in Luxemburg.

| [Docs](https://docs.lxp.lu/)
| [User portal](https://servicedesk.lxp.lu/)
| [System status](https://weather.lxp.lu)
| [News & Events](https://luxprovide.lu)
|

Support email: servicedesk@lxp.lu (create ticket on user portal)

## Access

After the project leader creates an account for you, you will receive an email with your username and instructions to login to the user portal. The procedure is also detailed [here](https://docs.lxp.lu/first-steps/connecting/).

In short, first generate an ed25519 ssh key.
```
$ ssh-keygen -o -a 100 -t ed25519 -f ~/.ssh/id_ed25519_MeluXina
$ cat ~/.ssh/id_ed25519_MeluXina.pub
```
Than, on the user portal go to 'Add or update your SSH key' and send the public key.

Once you received confirmation your key has been added, you can login.
Add the information to your ssh config file:
```
Host meluxina
        User yourusername
        Hostname login.lxp.lu
        Port 8822
        IdentityFile ~.ssh/id_ed25519_MeluXina
        IdentitiesOnly yes
        ForwardAgent no
```
Add your ssh key to the ssh agent.
```
ssh-add .ssh/id_ed25519_MeluXina
```
Now you can login:
```
ssh meluxina
```

## Running RAMSES

### Getting and compiling the code
You can get the code with git clone on the login node:
```
git clone https://git-cral.univ-lyon1.fr/hpc/space/ramses.git
```

Login nodes do not have access to the user software environment (it is only present on compute nodes). Compilation/execution tasks must be performed on the compute nodes. More information:
- https://docs.lxp.lu/first-steps/deploying_software/
- https://docs.lxp.lu/hpc/compiling/

You can compile the code either by submitting a batch script or through an interactive allocation. To request an interactive allocation on a computing node:
```
salloc -A COMPUTE_ACCOUNT -p cpu --qos default -N 1 -t 2-0:00:0 srun --mpi=none --pty bash -l
```
You can check your allocation account with the command `myquota`.

Once allocated, you can use the command `module` as usual to see what modules are available.
Since the system has AMD processors, we will use GNU compilers:
```
module load GCC
module load OpenMPI/4.1.5-GCC-12.3.0
```
You can now `make` the code. Once you are done, relinquish the job allocation with ctrl+D.

### Submitting a job

https://docs.lxp.lu/first-steps/handling_jobs/

Example job script `job.slm`:
```
#!/bin/bash -l
#SBATCH --job-name=test
#SBATCH --account=p200525
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1
#SBATCH --exclusive
#SBATCH --time=00:10:00
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

module load GCC
module load OpenMPI/4.1.5-GCC-12.3.0

export DATE=`date +%F_%Hh%M`

srun ./ramses3d sedov3d_2048.nml > run_${DATE}_${SLURM_JOBID}.log
```

Submit your job with
```
$ sbatch job.slm
```
