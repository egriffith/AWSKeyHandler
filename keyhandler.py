#! /usr/bin/env python3

import sys
from os.path import expanduser
import argparse
import boto3
import botocore

def printDebug(action, publicKeyName, publicKeyText, regionList, debug, dryRun, credProfile):
    return 0


def buildArgParser(argv):
    parser = argparse.ArgumentParser(description="Upload, delete, or list SSH key pairs in AWS regions")

    parser.add_argument('action',
                        help="Valid actions are 'upload', 'delete', and 'list' ")

    parser.add_argument('--keyName', '-n',
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

    #parser.add_argument('--debug', action="store_true",
    #                    help="Debug flag. If set, the script will output what the script -would- do without doing it.")
    
    parser.add_argument('--dryrun', action="store_true",
                        help="Sets the 'DryRun' flag on the upload_key API call. ")
    
    return parser.parse_args()


def wipeKey(publicKeyName, regionList, credProfile, dryrun):
    if publicKeyName == None:
        print("argument '--keyname / -n' is required for wiping a key.")
        sys.exit(1)

    session = boto3.Session(profile_name=credProfile)
    for region in regionList:
        print("Removing key '" + publicKeyName + "' from: " + region + " --- ", end="")
        try:
            session.client("ec2",region_name=region).delete_key_pair(
                                        KeyName=publicKeyName,
                                        DryRun=dryrun)
        except botocore.exceptions.ClientError as error:
            print("Failed.")
            if error.response['Error']['Code'] == "DryRunOperation":
                print("Operation would have succeeded, but was a dry run.\n")
                continue
            elif error.response['Error']['Code'] == "UnauthorizedOperation":
                print("Operation failed due to permissions.\n")
                continue
            else:
                print(str(error) + "\n")
                sys.exit(1)

        print("Success.\n")

    return 0


def uploadKey(publicKeyName, publicKeyText, regionList, dryRun, credProfile):
    if publicKeyName == None:
        print("argument '--keyname / -n' is required for uploading a key.")
        sys.exit(1)
    else:
        session = boto3.Session(profile_name=credProfile)
        for region in regionList:
            print("Importing key to: " + region + " --- ", end="")
            try:
                session.client("ec2",region_name=region).import_key_pair(
                                                                        DryRun=dryRun,
                                                                        KeyName=publicKeyName,
                                                                        PublicKeyMaterial=publicKeyText)
            except botocore.exceptions.ClientError as error:
                print("Failed.")
                if error.response['Error']['Code'] == "DryRunOperation":
                    print("Operation would have succeeded, but was a dry run.\n")
                    continue
                elif error.response['Error']['Code'] == "UnauthorizedOperation":
                    print("Operation failed due to permissions.\n")
                    continue
                else:
                    print(str(error) + "\n")
                    sys.exit(1)

            print("Success.\n")

    return 0


def listKeys(regionList, credProfile, dryrun, publicKeyName=[]):
    session = boto3.Session(profile_name=credProfile)
    for region in regionList:
        print("======= Public Keys available in: " + region + " =======")
        try:
            keyList = session.client("ec2",region_name=region).describe_key_pairs(
                                        KeyNames=publicKeyName,
                                        DryRun=dryrun)['KeyPairs']
        except botocore.exceptions.ClientError as error:
            print("Failed.")
            if error.response['Error']['Code'] == "DryRunOperation":
                print("Operation would have succeeded, but was a dry run.\n")
                continue
            elif error.response['Error']['Code'] == "UnauthorizedOperation":
                print("Operation failed due to permissions.\n")
                continue
            else:
                print(str(error) + "\n")
                sys.exit(1)
        
        for index, item in enumerate(keyList):
            print(item['KeyName'] + " - " + item['KeyFingerprint'])

        print("")

    return 0


def manipRegionInput(regionInput):
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


def main(argv):                        
    arglist = buildArgParser(argv)

    if arglist.action == "upload":
        uploadKey(arglist.publicKeyName, 
                readKeyFile(arglist.keyFilePath), 
                manipRegionInput(arglist.regionList), 
                arglist.dryrun,
                arglist.credProfile)

    elif arglist.action == "delete":
        wipeKey(arglist.publicKeyName,
                manipRegionInput(arglist.regionList),
                arglist.credProfile,
                arglist.dryrun)

    elif arglist.action == "list":
        listKeys(manipRegionInput(arglist.regionList), arglist.credProfile, arglist.dryrun)

    else:
        print("Action '" + arglist.action + "' not recognized.")
        sys.exit(1)

 
if __name__ == "__main__":
   main(sys.argv[1:])