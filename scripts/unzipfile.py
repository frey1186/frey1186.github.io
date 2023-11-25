#!/usr/bin/env python
#
# version: v0.1
# date: 2023-11-3
#
import zipfile
import threading
import sys
import argparse
import rarfile

def extract(file, passwd):
    try:
        file.extractall(pwd=passwd)
        print(f"password is {passwd}")
        return passwd
    except:
        pass

def unzip_multithreading(zfile_in, pfile_in):
    if rarfile.is_rarfile(zfile_in):
        zfile = rarfile.RarFile(zfile_in)
    elif zipfile.is_zipfile(zfile_in):
        zfile = zipfile.ZipFile(zfile_in)
    else:
        print("unrecogonize file type.")
        sys.exit(1)
    passfile = open(pfile_in,'r')
    for line in passfile.readlines():
        password = line.strip('\n')
        t = threading.Thread(target=extract, args=(zfile, password.encode()))
        t.start()
    passfile.close()

def unzip(file, password):
    zfile = zipfile.ZipFile(file)
    try:
        zfile.extractall(pwd=password.encode())
        print(f"password is {password}")
        return 0
    except Exception as e:
        print(f"password is not {password}, err: {e}")
        sys.exit(1)

if __name__ == '__main__':

    parse = argparse.ArgumentParser()
    parse.add_argument('zipfile', help="zip or rar file")
    group1 = parse.add_mutually_exclusive_group()
    group1.add_argument('-p', '--password', help="the password")
    group1.add_argument('-f', '--pwdfile', help="password list file")
    args = parse.parse_args()

    if args.password:
        unzip(args.zipfile, args.password)
    elif args.pwdfile:
        unzip_multithreading(zfile_in=args.zipfile, pfile_in=args.pwdfile)
    else:
        parse.print_help()