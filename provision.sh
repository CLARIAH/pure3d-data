#!/bin/bash

HELP="
Put additional data within reach of the container.

This can be run on the host, without the need of a running app container.

The data comes from this repo and is placed in CLARIAH/pure3dx/data,

The pure3dx app has working data in CLARIAH/pure3dx/data/working directory.

So the app can access the provisioned data, but the data is not directly
provisioned to the working data of the app.

When the app starts up and discovers it is missing data, it will import it
from the data directory into the data/working directory.

In test mode, the app can also reset its working data with a fresh copy of the
provisioned data.

NB: None of this provisioning deals with production data!


Exactly what data is provisioned is steered by tasks and flags.


Tasks
-----

example
    Example data. Example data is a directory with data and additional
    yaml files.

pilot
    Generate pilot data from a template.
    By default it generates 4 scratch projects and 25 users with one project
    for each user.
    That can be overridden by:
    --pilot-user n
    --pilot-scratch n

viewers
    Client-side code of 3d viewers. This is a directory
    that needs no further processing within the container.

There are also flag arguments:

--dev
    Adapt source and destination of data transfer to the development environment.
    If not present, these will be set to production values.

--resetexample
    Will delete the the working example data

--resetpilot
    Will delete the the working pilot data

--pilot-user n
    Number of pilot users to generate.

--pilot-scratch n
    Number of scratch users to generate.

Usage
-----

Run it from the toplevel directory in the repo.

./provision.sh [flag or task] [flag or task] ...

Examples
--------

Generate pilot data for 2 scratch projects and 5 users,
but it should not be deployed yet:

./provision.sh pilot --pilot-scratch 2 --pilot-user 5

Same, but with deployment, after restart of the app:

./provision.sh pilot --pilot-scratch 2 --pilot-user 5 --resetpilot

Generate example data, without deployment:

./provision.sh example

Same, but with deployment, after restart of the app:

./provision.sh example --resetexample

To refresh the viewers, and they are immediately visible to the app

./provision.sh viewers

To do everything, with default settings

./provision.sh all

is equivalent to

./provision.sh viewers example pilot
"

### begin values for local development
fromloc_dev="."
toloc_dev="../pure3dx/data"
### end values for local development

### begin values for production
### !! these values need to be confirmed !!
fromloc_prod="/app/data/pure3d/data"
toloc_prod="/app/data/"
### end values for production

dopilot="x"
doexample="x"
doviewers="x"
resetexample="x"
resetpilot="x"

pilotuser="25"
pilotscratch="4"

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
    elif [[ "$1" == "pilot" ]]; then
        dopilot="v"
        shift
    elif [[ "$1" == "example" ]]; then
        doexample="v"
        shift
    elif [[ "$1" == "viewers" ]]; then
        doviewers="v"
        shift
    elif [[ "$1" == "all" ]]; then
        dopilot="v"
        doexample="v"
        doviewers="v"
        shift
    elif [[ "$1" == "--resetexample" ]]; then
        doresetexample="v"
        shift
    elif [[ "$1" == "--resetpilot" ]]; then
        doresetpilot="v"
        shift
    elif [[ "$1" == "--pilot-user" ]]; then
        shift
        pilotuser=$1
        shift
    elif [[ "$1" == "--pilot-scratch" ]]; then
        shift
        pilotscratch=$1
        shift
    else
        echo "unrecognized argument '$1'"
        shift
    fi
done

if [[ "$doexample" == "v" ]]; then
    if [[ "x" == "" ]]; then
        mkdir -p $toloc
        key=exampledata
        echo -e "$fromloc/$key ==> $toloc/$key"
        if [[ -d $toloc/$key ]]; then
            rm -rf $toloc/$key
        fi
        cp -r $fromloc/$key $toloc/
    fi
fi

if [[ "$dopilot" == "v" ]]; then
    python programs/makePilots.py $pilotscratch $pilotuser
    if [[ "x" == "" ]]; then
        mkdir -p $toloc
        key=pilotdata
        echo -e "$fromloc/$key ==> $toloc/$key"
        if [[ -d $toloc/$key ]]; then
            rm -rf $toloc/$key
        fi
        cp -r $fromloc/$key $toloc/
    fi
fi

if [[ "$doviewers" == "v" ]]; then
    if [[ "x" == "" ]]; then
        mkdir -p data
        echo -e "$fromloc/viewers ==> $toloc/viewers"
        if [[ -d $toloc/viewers ]]; then
            rm -rf $toloc/viewers
        fi
        cp -r $fromloc/viewers $toloc/
    fi
fi

if [[ "$doresetexample" == "v" ]]; then
    workingdir="$toloc/working/test"
    echo -e "removing working example data: $workingdir"
    if [[ -e "$workingdir" ]]; then
        rm -rf "$workingdir"
    fi
fi

if [[ "$doresetpilot" == "v" ]]; then
    workingdir="$toloc/working/pilot"
    echo -e "removing working pilot data: $workingdir"
    if [[ -e "$workingdir" ]]; then
        rm -rf "$workingdir"
    fi
fi
