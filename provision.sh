#!/bin/bash

HELP="
Generates pilot data and/or reset pilot/example data.

This can be run on the host, without the need of a running app container.

The generated data ends up in this repo and should be symlinked from
the working data of the app in CLARIAH/pure3dx/data.

This script can delete working example data and pilotdata.

When the app starts up and discovers it is missing data, it will import it
from symlinked data directories into the data/working directory.

In test mode, the app can also reset its working data with a fresh copy of the
example data.

NB: None of this provisioning deals with production data!


Tasks
-----

viewers
    Copy the viewer software from pure3d data to the data directory of pure3dx
    Regrettably, we cannot put a symbolic link in pure3dx/data because the docker
    machinery does not follow symlinks out of the parent directory of the repo pure3dx.

pilot
    Generate pilot data from a template.
    By default it generates 4 scratch projects and 25 users with one project
    for each user.
    That can be overridden by:
    --pilot-user n
    --pilot-scratch n

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

Run it from anywhere, but take care that the from and to directories
are configured well in the config section in this script.

./provision.sh [flag or task] [flag or task] ...

Examples
--------

Generate pilot data for 2 scratch projects and 5 users,
but it should not be deployed yet:

./provision.sh pilot --pilot-scratch 2 --pilot-user 5

Same, but with deployment, after restart of the app:

./provision.sh pilot --pilot-scratch 2 --pilot-user 5 --resetpilot
"

### begin values for local development
fromloc_dev=~/github/CLARIAH/pure3d-data
toloc_dev=~/github/CLARIAH/pure3dx/data
### end values for local development

### begin values for production
### !! these values need to be confirmed !!
fromloc_prod="/app/data/pure3d-data"
toloc_prod="/app/data/"
### end values for production

dopilot="x"
doexample="x"
doviewers="x"
resetexample="x"
resetpilot="x"

pilotuser="25"
pilotscratch="4"

isdev="x"
fromloc="$fromloc_prod"
toloc="$toloc_prod"

while [ ! -z "$1" ]; do
    if [[ "$1" == "--help" ]]; then
        printf "$HELP\n"
        exit 0
    fi
    if [[ "$1" == "--dev" ]]; then
        isdev="v"
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

if [[ "$isdev" == "v" ]]; then
    echo "PROVISIONING IN DEV MODE"
else
    echo "PROVISIONING IN PROD MODE"
fi

if [[ "$dopilot" == "v" ]]; then
    python programs/makePilots.py "$fromloc" $pilotscratch $pilotuser
    if [[ "$isdev" == "v" ]]; then
        mkdir -p $toloc
        key=pilotdata
        echo -e "$fromloc/$key ==> $toloc/$key"
        if [[ -d $toloc/$key ]]; then
            rm -rf $toloc/$key
        fi
        cp -r $fromloc/$key $toloc/
    fi
fi

if [[ "$doexample" == "v" ]]; then
    if [[ "$isdev" == "v" ]]; then
        mkdir -p $toloc
        key=exampledata
        echo -e "$fromloc/$key ==> $toloc/$key"
        if [[ -d $toloc/$key ]]; then
            rm -rf $toloc/$key
        fi
        cp -r $fromloc/$key $toloc/
    fi
fi

if [[ "$doviewers" == "v" ]]; then
    if [[ "$isdev" == "v" ]]; then
        mkdir -p $toloc
        key=viewers
        echo -e "$fromloc/$key ==> $toloc/$key"
        if [[ -d $toloc/$key ]]; then
            rm -rf $toloc/$key
        fi
        cp -r $fromloc/$key $toloc/
    else
        echo "Viewer provisioning can only be done in dev mode"
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
