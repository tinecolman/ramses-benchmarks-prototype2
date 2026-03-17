# Lumi

## Info

Hosted at CSC data center in Kajaani, Finland

| [Docs](https://docs.lumi-supercomputer.eu/)
| [User portal](https://my.lumi-supercomputer.eu/login/)
| [General website](https://lumi-supercomputer.eu/)
| [Status](https://lumi-supercomputer.eu/lumi-service-status/)
|

Support: https://lumi-supercomputer.eu/user-support/need-help/ (submit a ticket through the forms )


## Access

### Applying for time
Time on the Discoverer cluster can be obtained through [EuroHPC](https://access.eurohpc-ju.europa.eu/).

### Account creation

#### Get LUMI account
Ask the PI of the project to invite you to the project. You will receive an email with a link to sign up. You need to sign in using MyAccessID, which is linked to your home institution or organisation. Select your institution, for example CNRS. Create your MyAccessID account if not done so yet. Then follow the link again to accept the invitation to the LUMI project.

After this you will receive an email with your LUMI username, and another one with the project number needed for submitting jobs. The project will now be listed in the user dashboard on
https://my.lumi-supercomputer.eu/login/

#### Add your ssh public key in MyAccessId

Generate an ssh key following the instructions:
https://docs.lumi-supercomputer.eu/firststeps/SSH-keys/

The public key needs to be uploaded to your MyAccessID account. Go to
https://mms.myaccessid.org/fed-apps/profile/#settings_sshkeys
and choose 'settings' > 'SSH keys' > '+ New key'.

It takes a few hours before the key information is synchronized with LUMI.

You can now log in using the username you received in the email:
```
ssh myusername@lumi.csc.fi
```

#### Update SSH config

Ssh config example:
```
Host lumi
        User myusername
        Hostname lumi.csc.fi
        IdentityFile ~/.ssh/id_ed25519_lumi
```


### Login procedure

Optionally add your key to the ssh key manager:
```
ssh-add .ssh/id_ed25519_lumi
```
You can now login with ssh
```
ssh lumi
```

## Usage

### Getting and compiling the code
You can get the code through the usual way with git clone on the login node.



LUMI is a Cray system, so if we load the correct modules and use the cray wrappers, the system will automatically find the right compiler versions and libraries. See
https://docs.lumi-supercomputer.eu/development/compiling/prgenv/

By default, the Cray programming environment and mpi are already loaded. To switch for the CPU partition target architecture:
```
module swap craype-x86-rome craype-x86-milan
```

The fortran compiler wrapper is called `ftn`. 
Only mpich mpi is available.

Remark: I had trouble making it work with the Cray compiler. I get a runtime error. It worked with gnu.

### Running jobs

The system uses the SLURM job schedular.

Tests with 128 nodes and above crash in mpi with following error:
```
libfabric:177010:1728372637::cxi:core:cxip_ux_onload_cb():2659<warn> nid001056: RXC (0x3892:79) PtlTE 375:[Fatal] LE resources not recovered during flow control. FI_CXI_RX_MATCH_MODE=[hybrid|software] is required
```
Apparently the volume of mpi communications is too high for the network hardware configuration.
A solution is to add this line to the job script:
```
export FI_CXI_RX_MATCH_MODE=hybrid
```
Explanation of what this does:
https://cpe.ext.hpe.com/docs/latest/mpt/mpich/intro_mpi.html


### Accounting

To see how much of your allocation time you have consumed:
```
$ lumi-allocations
```

To see to which project(s) you belong to:
```
$ groups
```

To check disk and allocation quota:
```
$ lumi-workspaces
```

