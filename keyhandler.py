#! /usr/bin/env python3

import sys
from os.path import expanduser
import argparse
import boto3
import botocore

def buildArgParser(argv):
    parser = argparse.ArgumentParser(description="Upload, delete, or list SSH key pairs in AWS regions")

    parser.add_argument('action',
                        help="Valid actions are 'upload', 'delete', 'list' and 'nuke' ")

    parser.add_argument('--keyname', '-n',
                        dest="publicKeyName",
                        help="Identifier of the key within AWS. \
                        If uploading, AWS will automatically add '.pem' onto the end in all connection dialogues.\
                        Mandatory if uploading or removing a key. Optional for listing.")

    parser.add_argument('--keyfile', '-f', dest="keyFilePath",
                        default=expanduser("~")+"/.ssh/id_rsa.pub",
                        help="Path to the public key file to upload. Required for uploading, will default to ~/.ssh/id_rsa.pub if not specified")

    parser.add_argument('--regions', '-r', dest="regionList", 
                        default="all", 
                        help="Comma deliminated list of AWS regions to take action against. \
                        Defaults to all regions if not specified. Accepted by all actions.")
     
    parser.add_argument('--profile', '-p', dest="credProfile",
                        default="default",
                        help="The profile specified in ~/.aws/credentials to use for permissions.\
                        Defaults to 'default' profile. Accepted by all actions.")
    
    parser.add_argument('--dryrun', action="store_true",
                        help="Sets the 'DryRun' flag on the upload_key API call. ")
    
    
    return parser.parse_args()


def wipeKeyMeta(publicKeyName, regionList):
    if publicKeyName == None:
        print("argument '--keyname / -n' is required for wiping a key.")
        sys.exit(1)
      
    for region in regionList:
        wipeKeyRegion(publicKeyName, region)

    return 0

def wipeKeyRegion(publicKeyName, region):
    print("Removing key '" + publicKeyName + "' from: " + region + " --- ", end="")
    try:
        botoSession.client("ec2",region_name=region).delete_key_pair(
                                        KeyName=publicKeyName,
                                        DryRun=dryRun)
    except botocore.exceptions.ClientError as error:
        print("Failed.")
        if error.response['Error']['Code'] == "DryRunOperation":
            print("Operation would have succeeded, but was a dry run.\n")
        elif error.response['Error']['Code'] == "UnauthorizedOperation":
            print("Operation failed due to permissions.\n")
        else:
            print(str(error) + "\n")
            sys.exit(1)

    print("Success.\n")


def uploadKeyMeta(publicKeyName, publicKeyText, regionList):
    if publicKeyName == None:
        print("argument '--keyname / -n' is required for uploading a key.")
        sys.exit(1)
    else:
        for region in regionList:
            uploadKeyRegion(publicKeyName, publicKeyText, region)

    return 0

def uploadKeyRegion(publicKeyName, publicKeyText, region):
    print("Importing key to: " + region + " --- ", end="")
    try:
        botoSession.client("ec2",region_name=region).import_key_pair(
                                                                    DryRun=dryRun,
                                                                    KeyName=publicKeyName,
                                                                    PublicKeyMaterial=publicKeyText)
    except botocore.exceptions.ClientError as error:
        print("Failed.")
        if error.response['Error']['Code'] == "DryRunOperation":
            print("Operation would have succeeded, but was a dry run.\n")
        elif error.response['Error']['Code'] == "UnauthorizedOperation":
            print("Operation failed due to permissions.\n")
        else:
            print(str(error) + "\n")
            sys.exit(1)

    print("Success.\n")
    return 0


def listKeysMeta(regionList, publicKeyName=[]):
    for region in regionList:
        listRegionKeys(region, publicKeyName)

    return 0

def listRegionKeys(region, publicKeyName=[]):
    print("======= Public Keys available in: " + region + " =======")
    try:
        keyList = botoSession.client("ec2",region_name=region).describe_key_pairs(
                                        KeyNames=publicKeyName,
                                        DryRun=dryrun)['KeyPairs']
    except botocore.exceptions.ClientError as error:
        print("Failed.")
        if error.response['Error']['Code'] == "DryRunOperation":
            print("Operation would have succeeded, but was a dry run.\n")
        elif error.response['Error']['Code'] == "UnauthorizedOperation":
            print("Operation failed due to permissions.\n")
        else:
            print(str(error) + "\n")
            sys.exit(1)
        
    for index, item in enumerate(keyList):
        print(item['KeyName'] + " - " + item['KeyFingerprint'])

        print("")


def parseRegionInput(regionInput):
    regionInput = regionInput.lower()
    regionInput = regionInput.split(",")

    if regionInput[0] == "all":
        regionInput = boto3.session.Session().get_available_regions("ec2")

    return regionInput

def readKeyFile(keyFilePath):
    try:
        with open(keyFilePath, 'r') as keyFile:
            publicKeyText = keyFile.read()
    except FileNotFoundError:
        print("ERROR: File: " + str(keyFilePath) + "' could not be found. Exiting.")
        sys.exit(1)

    return publicKeyText

def parseAction(argList):
    if argList.action == "upload":
        return 0

    elif argList.action == "delete":
        return 0

    elif argList.action == "list":
        return 0

    else:
        print("Action '" + argList.action + "' not recognized.")
        sys.exit(1)

def setupCredentials(credProfile):
    global botoSession
    if credProfile == None:
        botoSession = boto3.Session()
    else:
        botoSession = boto3.Session(profile_name=credProfile)

def main(argv):
    global dryRun

    argList = buildArgParser(argv)
    setupCredentials(argList.credProfile)
    dryRun = argList.dryrun

    parseAction(argList)

    return 0

 
if __name__ == "__main__":
   main(sys.argv[1:])
