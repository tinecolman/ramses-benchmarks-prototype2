# MareNostrum

## Info

Hosted at Barcelona Supercomputing Center (BSC) in Spain

| [Docs](https://www.bsc.es/supportkc/docs/intro)
| [User portal](https://hpcaccounts.bsc.es/)
|

Support email: support@bsc.es

Partitions: 
- MareNostrum 5 GPP (General Purpose Partition, i.e. CPUs)
- MareNostrum 5 ACC (Accelerated Partition, i.e. GPUs)


## Access

### Applying for time
Time on the MareNostrum cluster can be obtained through [EuroHPC](https://access.eurohpc-ju.europa.eu/).


### Account creation
#### Activate BSC account

Once you are added to the project by the project leader, you receive an email to confirm your registration.
Click on the link to go to the  authentication portal at 
https://hpcportal.bsc.es/
You need to reset the password.
Click on 'recover it now', to set the password. An email with a link will be send to set the password. 

Once logged into the portal, you and the project leader need to agree with the "User Respondibilities". Follow the link and instructions in the email. A confirmation will be send by email once this step is complete.

#### Setting password

Once the previous step is complete, a username will be assigned and another email gives instructions on how to login to the cluster. A second email will be send with the password. Change it upon first login (on transfer1 only).

https://www.bsc.es/supportkc/docs/MareNostrum5/logins/#password-change

#### Setup SSH key

Since the access is through a password, the generation of an ssh key is not needed. You can use your regular ssh key for convenience.

SSH config:
```
Host marenostrum
        User myusername
        Hostname glogin1.bsc.es

Host marenostrum-acc
        User myusername
        Hostname alogin1.bsc.es

Host bscTransfer1
        User myusername
        Hostname transfer1.bsc.es

```

### Login procedure

Simply login with ssh (if config setup as in the previous section):
```
ssh marenostrum
```

## Usage

### Getting and compiling the code

No connections are allowed from inside the cluster to the outside world, so all scp and sftp commands have to be executed from your local machines and never from the cluster. This means git clone also does not work from within the machine. Instead, use sshfs as described here, 
https://www.bsc.es/supportkc/docs/dtmachines
, to create a directory inside your local machine that will be used as a mount point:
```
sshfs -o workaround=rename <yourHPCUser>@transfer1.bsc.es: <localDirectory>
```

By default, intel compilers and intel MPI modules are loaded.

### Running jobs

The system uses the SLURM job schedular. Details on how to run jobs:
https://www.bsc.es/supportkc/docs/MareNostrum5/slurm


### Accounting

To check on which account you can run:
```
$ bsc_project list
```

To check the time left on your allocation, use the command `bsc_acct`.
