import sys
import os
import yaml

from PIL import Image, ImageDraw, ImageFont

from files import dirExists, dirCopy, dirMake, fileCopy


HELP = """

makePilots.py number

Makes a number of empty pilotprojects in directory `pilotdata`.

A fixed number of example projects will be added as visible projects
with published editions.
"""


EXAMPLE_AMOUNT = 3


def makeIcon(text, color, bgColor, path):
    """Makes png icon with a number in it.

    Parameters
    ----------
    text: str
        The text to display in the image.
    color: RGB-tuple
        Color of the digits
    bgColor: RGB-tuple
        Background color.
    path: string
        Where the created image is to be saved.
    """
    fnt = ImageFont.truetype(font="Helvetica", size=32)
    image = Image.new(mode="RGB", size=(64, 64), color=bgColor)
    draw = ImageDraw.Draw(image)
    draw.text((5, 10), str(text), font=fnt, fill=color)
    image.save(path)


def makeItemIcon(text, kind, path):
    """Makes a project/edition icon with a text.

    Parameters
    ----------
    text: str
        The text to display in the image.
    kind: str
        `project` or `edition`. This determines
        the choice of colors.
    """
    if kind == "project":
        color = (255, 155, 0)
        bgColor = (0, 60, 100)
    elif kind == "edition":
        color = (0, 100, 60)
        bgColor = (255, 200, 225)

    makeIcon(text, color, bgColor, path)


def fillinMeta(p, kind, path):
    with open(path) as fh:
        text = fh.read().replace("«num»", f"{p:>02}").replace("«kind»", kind)
    with open(path, "w") as fh:
        fh.write(text)


def makePilotData(amountScratch, amountUser):
    """Instantitates the pilot data template.

    Creates fresh pilot data based on the template,
    with

    *   *amountUser* projects and one edition per project.
    *   *amountScratch* scratch projects for the admin, also each having one edition

    The amounts should be between 1 and 20, including.

    For every project there is one user, that
    will become the organiser of the project and the editor
    of its edition.

    One admin user will be created.
    That will also be the organiser of the scratch projects.
    """
    baseDir = os.path.abspath("..")
    templateDir = f"{baseDir}/pilottemplate"
    dataDir = f"{baseDir}/pilotdata"
    workflowDir = f"{dataDir}/workflow"
    dirMake(dataDir, fresh=True)
    dirMake(workflowDir)
    workflowPath = f"{dataDir}/workflow/init.yml"

    if not dirExists(templateDir):
        print("Pilot template dir does not exist: {templateDir}")
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

    allProjects = list(range(1, EXAMPLE_AMOUNT + amountScratch + amountUser + 1))
    exampleProjects = list(range(1, EXAMPLE_AMOUNT + 1))
    scratchProjects = list(
        range(EXAMPLE_AMOUNT + 1, EXAMPLE_AMOUNT + amountScratch + 1)
    )
    userProjects = list(range(EXAMPLE_AMOUNT + amountScratch + 1, len(allProjects) + 1))

    a1 = "a1"

    users = {f"u{i + 1:>02}": "user" for (i, p) in enumerate(userProjects)}
    users[a1] = "admin"

    projectWf = {}
    editionWf = {}
    projectStatus = {}
    editionStatus = {}

    for (kind, projectBatch) in (
        ("e", exampleProjects),
        ("s", scratchProjects),
        ("p", userProjects),
    ):
        kindRep = "of user" if kind == "p" else "(scratch)" if kind == "s" else ""

        for (i, p) in enumerate(projectBatch):
            pS = f"{p}"
            i1 = i + 1
            projectSource = (
                f"{exampleSource}/{p}" if kind == "e" else f"{templateDir}/project/1"
            )
            projectDest = f"{dataDir}/project/{p}"
            dirCopy(projectSource, projectDest)

            projectStatus[pS] = kind == "e"

            editionStatus[pS] = {}

            if kind == "e":
                editionStatus
                with os.scandir(f"{projectDest}/edition") as dh:
                    for entry in dh:
                        e = entry.name
                        if not e.isdigit() or not entry.is_dir():
                            continue
                        editionStatus[pS][f"{e}"] = True

            else:
                makeItemIcon(f"{kind}{i1:>02}", "project", f"{projectDest}/icon.png")
                metaProject = f"{projectDest}/meta/dc.yml"
                fillinMeta(i1, kindRep, metaProject)
                editionDest = f"{projectDest}/edition/1"
                makeItemIcon("1", "edition", f"{editionDest}/icon.png")
                metaEdition = f"{editionDest}/meta/dc.yml"
                fillinMeta(i1, kindRep, metaEdition)
                projectWf[pS] = {(f"u{i1:>02}" if kind == "p" else a1): "organiser"}
                editionWf[pS] = {"1": {(f"u{i1:>02}" if kind == "p" else a1): "editor"}}
                editionStatus[pS]["1"] = False

    status = dict(
        project=dict(field="isVisible", values=projectStatus),
        edition=dict(field="isPublished", values=editionStatus),
    )

    workflow = dict(
        userRole=dict(site=users, project=projectWf, edition=editionWf),
        status=status,
    )

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
    if len(args) != 2:
        print(HELP)
        print("Pass exactly two numbers 1..20 as argument")
        return

    (amountScratch, amountUser) = args[0:2]

    amountS = testNum(amountScratch)
    amountU = testNum(amountUser)

    if amountS is None or amountU is None:
        print(HELP)
        if amountS is None:
            print(f"`{amountScratch}` is not a number.")
        if amountU is None:
            print(f"`{amountUser}` is not a number.")
        return

    if not (1 <= amountS <= 20):
        print(HELP)
        print(f"{amountS} is not in 1..20")
        return

    if not (1 <= amountU <= 20):
        print(HELP)
        print(f"{amountU} is not in 1..20")
        return

    makePilotData(amountS, amountU)


if __name__ == "__main__":
    main()
