# Deucalion

## Info

Hosted by LuxProvide in Luxemburg.

| [Docs](https://docs.macc.fccn.pt/)
| [User portal](https://portal.deucalion.macc.fccn.pt/user/login/)
|

Support email: 

## Access

### Applying for time
Time on the Deucalion cluster can be obtained through [EuroHPC](https://access.eurohpc-ju.europa.eu/).

### Account creation
Follow the guide:
https://docs.macc.fccn.pt/start/

```
Host deucalion
        User myusername
        Hostname login.deucalion.macc.fccn.pt
        IdentityFile ~/.ssh/id_ed25519
        ForwardAgent no
```

### Login procedure

Simply login with ssh (if config setup as in the previous section):
```
ssh deucalion
```

## Usage

### Getting and compiling the code
You can get the code through the usual way with git clone on the login node.

I have not tried compiling yet.
https://docs.macc.fccn.pt/compilation/


### Running jobs

The system uses the SLURM job schedular.

https://docs.macc.fccn.pt/jobs/

### Accounting

How to see how much time is left on your allocation, use the command `billing`.