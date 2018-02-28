Simple python3 script to handle uploading, deleting, and listing of keys within AWS, making use of boto3.

## Arguments ##
keyhandler.py accepts a variety of arguments and flags depending on the action being taken. The only mandatory

Actions: 

"list" --> List the keys, their names and fingerprints, within the regions specified. --keyname can be specified to only look for a single key.

"delete" --> Delete a specific key from the regions specified. --keyname is mandatory.

"upload" --> Uploads a key to the regions specified. --keyfile will default to ~/.ssh/id_rsa unless otherwise specified, --keyname is mandatory for this command.

Additionally there are optional arguments for each command.

"--regions" / "-r" --> A comma delimited list of AWS region endpoints that the given action should be done against. Defaults to all regions if not specified.

"--profile" / "-p" --> The name of the profile to use from a user's ~/.aws/credential file for permissions. If your profile name includes a space, put this argument in quotes. Defaults to 'default' if not specified.

"--dryrun" --> Sets the DryRun flag on the API call. This is useful for testing IAM permissions without actually executing the call.

## Examples ##

[user@localhost ~/bin/AWSKeyHandler]$ ./keyhandler.py list -r us-east-1,us-west-2  
======= Public Keys available in: us-east-1 =======  
id_rsa - 22:a0:b0:19:16:73:29:65:c6:c0:1d:10:42:b1:b6:c2  
   
======= Public Keys available in: us-east-2 =======   
id_rsa - 22:a0:b0:19:16:73:29:65:c6:c0:1d:10:42:b1:b6:c2   
   
   
   
   
   
   
[user@localhost ~/bin/AWSKeyHandler]$ ./keyhandler.py delete -n id_rsa -r us-east-1  
Removing key 'id_rsa' from: us-east-1 --- Success.   
   
   
   
   
   
   
[user@localhost ~/bin/AWSKeyHandler]$ ./keyhandler.py list -r us-east-1,us-west-2  
======= Public Keys available in: us-east-1 =======   

======= Public Keys available in: us-east-2 =======   
id_rsa - 22:a0:b0:19:16:73:29:65:c6:c0:1d:10:42:b1:b6:c2    
   
   
   
   
   
   
[user@localhost ~/bin/AWSKeyHandler]$ ./keyhandler.py upload --keyname id_rsa_replacement --keyfile ~/.ssh/id_rsa.pub --region us-east-1   
Importing key to: us-east-1 --- Success.   
   
   
   
   
   
   
[user@localhost ~/bin/AWSKeyHandler]$ ./keyhandler.py list -r us-east-1,us-east-2   
======= Public Keys available in: us-east-1 =======   
id_rsa_replacement - 22:a0:b0:19:16:73:29:65:c6:c0:1d:10:42:b1:b6:c2   

======= Public Keys available in: us-east-2 =======   
id_rsa - 22:a0:b0:19:16:73:29:65:c6:c0:1d:10:42:b1:b6:c2   
   
   
   
   
   
   
[user@localhost ~/bin/AWSKeyHandler]$ ./keyhandler.py upload --keyname id_rsa_replacement --keyfile ~/.ssh/id_rsa.pub --region us-east-1 --dryrun   

Importing key to: us-east-1 --- Failed.   
Operation would have succeeded, but was a dry run.   
   
   
   
   
   
```[user@localhost ~/bin/AWSKeyHandler]$ ./keyhandler.py -h   
usage: keyhandler.py [-h] [--keyName PUBLICKEYNAME] [--keyfile KEYFILEPATH]   
                     [--regions REGIONLIST] [--profile CREDPROFILE] [--dryrun]   
                     action   
   
Upload, delete, or list SSH key pairs in AWS regions   
   
positional arguments:   
  action                Valid actions are 'upload', 'delete', and 'list'   

optional arguments:   
  -h, --help            show this help message and exit   
  --keyName PUBLICKEYNAME, -n PUBLICKEYNAME   
                        Identifier of the key within AWS. If uploading, AWS   
                        will automatically add '.pem' onto the end in all   
                        connection dialogues. Mandatory if uploading or   
                        removing a key. Optional for listing.   
  --keyfile KEYFILEPATH, -f KEYFILEPATH   
                        Path to the public key file to upload. Required for   
                        uploading, will default to ~/.ssh/id_rsa.pub if not   
                        specified   
  --regions REGIONLIST, -r REGIONLIST   
                        Comma deliminated list of AWS regions to take action   
                        against. Defaults to all regions if not specified.   
                        Accepted by all actions.   
  --profile CREDPROFILE, -p CREDPROFILE   
                        The profile specified in ~/.aws/credentials to use for   
                        permissions. Defaults to 'default' profile. Accepted   
                        by all actions.   
  --dryrun              Sets the 'DryRun' flag on the upload_key API call.   ```
