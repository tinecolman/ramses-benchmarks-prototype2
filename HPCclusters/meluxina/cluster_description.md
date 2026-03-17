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

### Applying for time
Time on the MeluXina cluster can be obtained through [EuroHPC](https://access.eurohpc-ju.europa.eu/).

### Account creation

After the project leader creates an account for you, you will receive an email with your username and instructions to login to the user portal. The procedure is also detailed [here](https://docs.lxp.lu/first-steps/connecting/).

In short, first generate an ed25519 ssh key.
```
$ ssh-keygen -o -a 100 -t ed25519 -f ~/.ssh/id_ed25519_MeluXina
$ cat ~/.ssh/id_ed25519_MeluXina.pub
```
Than, on the user portal go to 'Add or update your SSH key' and send the public key.

Once you received confirmation your key has been added, you can login. For convenience, add the information to your ssh config file:
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

### Login procedure

Simply login with ssh (if config setup as in the previous section):
```
ssh meluxina
```

## Usage

### Getting and compiling the code
You can get the code through the usual way with git clone on the login node.

Login nodes do not have access to the user software environment (it is only present on compute nodes). Compilation/execution tasks must be performed on the compute nodes. More information:
- https://docs.lxp.lu/first-steps/deploying_software/
- https://docs.lxp.lu/hpc/compiling/

You can compile the code either by submitting a batch script or through an interactive allocation. To request an interactive allocation on a computing node:
```
salloc -A COMPUTE_ACCOUNT -p cpu --qos default -N 1 -t 2-0:00:0 srun --mpi=none --pty bash -l
```
You can check your allocation account with the command `myquota`.

Once allocated, you can use the command `module` as usual to see what modules are available.
Once you are done compiling, relinquish the job allocation with ctrl+D.


### Running jobs

The system uses the SLURM job schedular. For more info see:

https://docs.lxp.lu/first-steps/handling_jobs/

### Accounting

How to see how much time is left on your allocation, use the command `myquota`.