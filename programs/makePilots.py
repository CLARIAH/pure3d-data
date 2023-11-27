import sys
import os
import yaml

from files import dirExists, dirCopy, dirMake, fileCopy


HELP = """

makePilots.py baseDir numberExample numberScratch numberUser

Makes a number of empty scratch and user projects in directory *baseDir*/`pilotdata`.

A number of example projects will be added as visible projects
with published editions.
"""


EXAMPLE_AMOUNT = 3
MAX_USER = 50
MAX_SCRATCH = 10


def fillinMeta(p, kind, path):
    with open(path) as fh:
        text = fh.read().replace("«num»", f"{p:>02}").replace("«kind»", kind)
    with open(path, "w") as fh:
        fh.write(text)


def makePilotData(baseDir, amountExample, amountScratch, amountUser):
    """Instantiates the pilot data template.

    Creates fresh pilot data based on the template,
    with

    *   *amountUser* projects and one edition per project.
    *   *amountScratch* scratch projects for the admin, also each having one edition

    The amounts should be between 1 and 50, including.

    For every project there is one user, that
    will become the organiser of the project and the editor
    of its edition.

    One admin user will be created.
    That will also be the organiser of the scratch projects.
    """
    templateDir = f"{baseDir}/pilottemplate"
    dataDir = f"{baseDir}/pilotdata"
    iconDir = f"{baseDir}/icons"
    workflowDir = f"{dataDir}/workflow"
    dirMake(dataDir, fresh=True)
    dirMake(workflowDir)
    workflowPath = f"{dataDir}/workflow/init.yml"

    if not dirExists(templateDir):
        print("pilots: Pilot template dir does not exist: {templateDir}")
        return False

    with os.scandir(templateDir) as dh:
        for entry in dh:
            name = entry.name
            if name == "project":
                continue
            (fileCopy if entry.is_file() else dirCopy)(
                f"{templateDir}/{name}", f"{dataDir}/{name}"
            )

    projectSource = f"{templateDir}/project/1"
    exampleSource = f"{baseDir}/exampledata/project"

    exampleProjects = [f"x{i:>02}" for i in range(1, amountExample + 1)]
    scratchProjects = [f"s{i:>02}" for i in range(1, amountScratch + 1)]
    userProjects = [f"p{i:>02}" for i in range(1, amountUser + 1)]

    allProjects = exampleProjects + scratchProjects + userProjects

    a1 = "a1"

    users = {u: "user" for u in allProjects}
    users[a1] = "admin"

    projectWf = {}
    editionWf = {}
    projectStatus = {}
    editionStatus = {}

    for kind, projectBatch in (
        ("x", exampleProjects),
        ("s", scratchProjects),
        ("p", userProjects),
    ):
        kindRep = (
            "of user" if kind == "p" else "(scratch)" if kind == "s" else "(example)"
        )
        print(f"pilots: {len(projectBatch)} projects {kindRep}")

        for p in projectBatch:
            projectSource = (
                f"{exampleSource}/{int(p[1:])}"
                if kind == "x"
                else f"{templateDir}/project/1"
            )
            projectDest = f"{dataDir}/project/{p}"
            dirCopy(projectSource, projectDest)

            projectStatus[p] = kind == "x"

            editionStatus[p] = {}

            if kind == "x":
                with os.scandir(f"{projectDest}/edition") as dh:
                    for entry in dh:
                        e = entry.name
                        if not e.isdigit() or not entry.is_dir():
                            continue
                        editionStatus[p][f"{e}"] = True

            else:
                fileCopy(f"{iconDir}/{p}.png", f"{projectDest}/icon.png")
                metaProject = f"{projectDest}/meta/dc.yml"
                fillinMeta(p, kindRep, metaProject)
                editionDest = f"{projectDest}/edition/1"
                fileCopy(f"{iconDir}/e01.png", f"{editionDest}/icon.png")
                metaEdition = f"{editionDest}/meta/dc.yml"
                fillinMeta(p, kindRep, metaEdition)
                projectWf[p] = {p: "organiser"}
                editionWf[p] = {"1": {p: "editor"}}
                editionStatus[p]["1"] = False

    status = dict(
        project=dict(field="isVisible", values=projectStatus),
        edition=dict(field="isPublished", values=editionStatus),
    )

    workflow = dict(
        userRole=dict(site=users, project=projectWf, edition=editionWf),
        status=status,
    )

    print("pilots: Workflow ...")
    with open(workflowPath, "w") as fh:
        yaml.dump(workflow, fh)


def testNum(n):
    try:
        n = int(n)
    except Exception:
        return None
    return n


def main():
    args = sys.argv[1:]
    if len(args) != 4:
        print(HELP)
        print("pilots: Pass a basedirectory and exactly two numbers as argument")
        return

    (baseDir, amountExample, amountScratch, amountUser) = args[0:4]

    amountE = testNum(amountExample)
    amountS = testNum(amountScratch)
    amountU = testNum(amountUser)

    if amountE is None or amountS is None or amountU is None:
        print(HELP)
        if amountE is None:
            print(f"pilots: `{amountExample}` is not a number.")
        if amountS is None:
            print(f"pilots: `{amountScratch}` is not a number.")
        if amountU is None:
            print(f"pilots: `{amountUser}` is not a number.")
        return

    good = True
    if not (0 <= amountE <= EXAMPLE_AMOUNT):
        print(HELP)
        print(f"pilots: {amountE} is not in 0..{EXAMPLE_AMOUNT}")
        good = False

    if not (0 <= amountS <= MAX_SCRATCH):
        print(HELP)
        print(f"pilots: {amountS} is not in 0..{MAX_SCRATCH}")
        good = False

    if not (1 <= amountU <= MAX_USER):
        print(HELP)
        print(f"pilots: {amountU} is not in 1..{MAX_USER}")
        good = False

    if not good:
        return

    makePilotData(baseDir, amountE, amountS, amountU)


if __name__ == "__main__":
    main()
