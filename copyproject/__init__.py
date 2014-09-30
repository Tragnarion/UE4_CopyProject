#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UE4 project creator.

Copyright Tragnarion Studios - by Moritz Wundke
"""
import os
import sys
import getopt
import argparse
import shutil
import fileinput

__version__ = '0.1'
__author__ = 'Moritz Wundke'

# Source files
SOURCE_FILES = ['.cs','.cpp','.h','.xml','.csproj','.ini','.txt','.bat','.cmd','.plist','.json','.uproject','.rc']

def print_error_ext(src, dst, msg):
    print("ERROR: %s -> %s: %s" % (src, dst, msg))

def print_error(msg):
    print("ERROR: %s" % msg)

def get_extension(path_name):
    """
    Get the file extension with the dot of the given path. Returns
    None if something failed or no extension could be found
    """
    try:
        if os.path.isfile(path_name):
            return os.path.splitext(os.path.basename(path_name))[1]
        return None
    except:
        return None

def copytree(src, dst, template_base, target_base, replace_map):
    """
    Copy tree based on: http://stackoverflow.com/questions/12683834/how-to-copy-directory-recursively-in-python-and-overwrite-all
    """
    names = os.listdir(src)
    if not os.path.isdir(dst): # This one line does the trick
        os.makedirs(dst)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name).replace(template_base, target_base)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, template_base, target_base, replace_map)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
                extension = get_extension(dstname)
                if extension in SOURCE_FILES:
                    for line in fileinput.input(dstname, inplace=True):
                        new_line = line
                        for key, value in replace_map.items():
                            new_line = new_line.replace(key, value)
                        print(new_line),
                elif extension == ".uasset" or extension == ".umap":
                    s=None
                    try:
                        f=open(dstname,"rb")
                        s=f.read()
                    finally:
                        f.close()
                    if s:
                        try:
                            s=s.replace(bytes(template_base),bytes(target_base))
                            f=open(dstname,"wb")
                            f.write(s)
                            f.close()
                        finally:
                            f.close()

        except Exception as why:
            print_error_ext(srcname, dstname, str(why))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            print_error_ext(srcname, dstname, str(why))

def create_project(template, target, copyright):
    """
    Create a project based on template project.
    """
    # Copy the entire directory tree
    if os.path.exists(target):
        print("Purging target folder")
        shutil.rmtree(target)

    # Create target tree and replace
    print("Copying template project to target folder")

    template_base = os.path.basename(template).replace('Game','')
    target_base = os.path.basename(target).replace('Game','')

    replace_map = {
        template_base:target_base
        , template_base.lower():target_base.lower()
        , template_base.upper():target_base.upper()
    }

    # Check that we have copyright text
    if copyright:
        replace_map['// Copyright 1998-2014 Epic Games, Inc. All Rights Reserved.'] = copyright
    copytree(template, target, template_base, target_base, replace_map)

def main():
    parser = argparse.ArgumentParser(description='UE4 project creator (%s). Tragnarion Studios - by %s' % (__version__, __author__))

    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-f', help='Will overwrite target project if exists', action="store_true")
    parser.add_argument('-s','--source', help='Source project absolute path, such as ShooterGame. Game part is important!',required=True)
    parser.add_argument('-t','--target', help='Target project absolute path, such as MyGame. Game part is important!', required=True)
    parser.add_argument('-c','--copyright', help='Copyright to be used to replaced with', default='// Copyright 2014 <CopyrightHolderHere> All Rights Reserved.')
    args = parser.parse_args()

    if not os.path.isdir(args.source) or not os.path.exists(os.path.join(args.source, "%s.uproject" % os.path.basename(args.source))):
        print_error("Source path must be avalid UE4 project!")
        parser.print_help()
        sys.exit(2)

    if os.path.exists(args.target) and not args.f:
        print_error("Target path is not empty or does already exist!")
        parser.print_help()
        sys.exit(2)

    # Create the project now
    create_project(args.source, args.target, args.copyright)

if __name__ == "__main__":
    main()
