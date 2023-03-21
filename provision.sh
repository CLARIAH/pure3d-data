#!/bin/bash

HELP="
Put additional data within reach of the container.

This can be run on the host, without the need of a running container.

It can provision the following kinds of data, steered by a list of
task arguments:

content
    Example data. Example data is a directory with data and additional
    yaml files.

viewers
    Client-side code of 3d viewers. This is a directory
    that needs no further processing within the container.

There are also flag arguments:

--dev
    Adapt source and destination of data transfer to
    the development environment
    If not present, these will be set to production values.

--resetexample
    Will delete the the working example data

--resetpilot
    Will delete the the working pilot data

When the pure3d app starts with non-existing pilot or empty data,
it will collect the data from the provisioned directory and initialize
the relevant MongoDb database accordingly.

Usage

Run it from the toplevel directory in the repo.

./provision.sh [flag or task] [flag or task] ...
"

### begin values for local development
fromloc_dev="."
toloc_dev="../pure3dx/data"
### end values for local development

### begin values for production
### !! these values need to be confirmed !!
fromloc_prod="."
toloc_prod="../pure3dx/data"
### end values for production

docontent="x"
doviewers="x"
resetexample="x"
resetpilot="x"

fromloc="$fromloc_prod"
toloc="$toloc_prod"

while [ ! -z "$1" ]; do
    if [[ "$1" == "--help" ]]; then
        printf "$HELP\n"
        exit 0
    fi
    if [[ "$1" == "--dev" ]]; then
        fromloc="$fromloc_dev"
        toloc="$toloc_dev"
        shift
    elif [[ "$1" == "content" ]]; then
        docontent="v"
        shift
    elif [[ "$1" == "viewers" ]]; then
        doviewers="v"
        shift
    elif [[ "$1" == "--resetexample" ]]; then
        doresetexample="v"
        shift
    elif [[ "$1" == "--resetpilot" ]]; then
        doresetpilot="v"
        shift
    else
        echo "unrecognized argument '$1'"
        shift
    fi
done

if [[ "$docontent" == "v" ]]; then
    echo -e "\tprovisioning example and pilot data"
    mkdir -p $toloc
    for key in exampledata pilotdata
    do
        echo -e "\t\t$fromloc/$key ==> $toloc/$key"
        if [[ -d $toloc/$key ]]; then
            rm -rf $toloc/$key
        fi
        cp -r $fromloc/$key $toloc/
    done
fi

if [[ "$doviewers" == "v" ]]; then
    echo -e "\tprovisioning client code of 3d viewers ..."
    mkdir -p data
    echo -e "\t\t$fromloc/viewers ==> $toloc/viewers"
    if [[ -d $toloc/viewers ]]; then
        rm -rf $toloc/viewers
    fi
    cp -r $fromloc/viewers $toloc/
fi

if [[ "$doresetexample" == "v" ]]; then
    workingdir="$toloc/working/test"
    echo -e "\tremoving working example data: $workingdir"
    if [[ -e "$workingdir" ]]; then
        rm -rf "$workingdir"
    fi
fi

if [[ "$doresetpilot" == "v" ]]; then
    workingdir=$toloc/working/pilot
    echo -e "\tremoving working pilot data: $workingdir"
    if [[ -e "$workingdir" ]]; then
        rm -rf "$workingdir"
    fi
fi
