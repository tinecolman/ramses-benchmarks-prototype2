# Leonardo Usage

## Info

Hosted by CINECA in Italy

| [Docs](https://docs.hpc.cineca.it/)
|

Support email: superc@cineca.it

## Access

### Applying for time
Time on the Leonardo cluster can be obtained through [EuroHPC](https://access.eurohpc-ju.europa.eu/).

### Account creation

Follow the guides here:
* https://docs.hpc.cineca.it/general/users_account.html
* https://docs.hpc.cineca.it/general/access.html

#### Register as a user

Register on the [user database](https://userdb.hpc.cineca.it), by clicking on the button "Create a New User". Fill in the form and upload your ID. You will receive an email with your username and a link to configure two-factor authentication which will expire in 12 hours.

Follow the link in the email to setup the OTP. In case the link expirated, write to superc@cineca.it to request a new one.

Once you've setup your account, ask the PI of the project to add you by providing your username.


#### Setup smallstep client

Install the smallstep client:
https://smallstep.com/docs/step-cli/installation/index.html


Configure:
https://docs.hpc.cineca.it/general/access.html#how-to-configure-smallstep-client

https://smallstep.com/docs/step-cli/installation/index.html

(Tristan notes, not sure these are up-to-date)
- download temporary certificate
- execute these commands
```
$ step ca bootstrap --ca-url=https://sshproxy.hpc.cineca.it --fingerprint 2ae1543202304d3f434bdc1a2c92eff2cd2b02110206ef06317e70c1c1735ecd
$ eval $(ssh-agent)
```

#### Update SSH config
```
Host leonardo
        User myusername
        Hostname login.leonardo.cineca.it
```

### Login procedure

First, a certificate needs to be generated, which will be valid for 12 hours:
```
step ssh login '<user_email>' --provisioner cineca-hpc
step ssh list --raw  '<user_email>'  | step ssh inspect
```
This will send you to the CINECA HPC portal where you configured the OTP. Login and enter the OTP code.

After that you can login with ssh:
```
ssh leonardo
```

If this is not the first time you try to connect, ssh will complain that the remote host identification has changed. Execute
```
ssh-keygen -f '/<user_path>/.ssh/known_hosts' -R 'login.leonardo.cineca.it'
```
and try again.


## Usage

### Getting and compiling the code
You can get the code through the usual way with git clone on the login node.

Since the system is made up of intel processors, it is adviced to use intel compilers:
```
module load intel-oneapi-compilers/
module load intel-oneapi-mpi/
```
The fortran compiler wrapper is called `mpiifort`.

GNU alterative:
```
$ module --force purge
$ module load gcc/11.3.0
$ module load openmpi/4.1.4--gcc--11.3.0-cuda-11.8
$ (module list)
```

### Running jobs

The system uses the SLURM job schedular.

The scratch directory can be accessed with `cd $SCRATCH`.

The CPU partition is called `dcgp_usr_prod`. There are different QOS, with different limits. Upto 16 nodes you can use the `normal` queue. For larger jobs, use `dcgp_qos_bprod`. The node limit is 128.

### Accounting

Command: `saldo -b`
