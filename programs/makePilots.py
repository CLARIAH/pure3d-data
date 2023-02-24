import sys
import os
import yaml

from PIL import Image, ImageDraw, ImageFont

from files import dirExists, dirCopy


HELP = """

makePilots.py number

Makes a number of empty pilotprojects in directory `pilotdata`.

"""


def makeIcon(number, color, bgColor, path):
    """Makes png icon with a number in it.

    Parameters
    ----------
    number: int | str
        The number to display in the image.
    color: RGB-tuple
        Color of the digits
    bgColor: RGB-tuple
        Background color.
    path: string
        Where the created image is to be saved.
    """
    fnt = ImageFont.truetype(font="Helvetica", size=48)
    image = Image.new(mode="RGB", size=(64, 64), color=bgColor)
    draw = ImageDraw.Draw(image)
    draw.text((5, 10), str(number), font=fnt, fill=color)
    image.save(path)


def makeItemIcon(number, kind, path):
    """Makes a project/edition icon with a number.

    Parameters
    ----------
    number: int | str
        The number to display in the image.
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

    makeIcon(number, color, bgColor, path)


def fillinMeta(p, path):
    with open(path) as fh:
        text = fh.read().replace("«num»", str(p))
    with open(path, "w") as fh:
        fh.write(text)


def makePilotData(amount):
    """Instantitates the pilot data template.

    Creates fresh pilot data based on the template,
    with *amount* projects and one edition per project.

    The amount should be between 1 and 20, including.

    For every project there is one user, that
    will become the organiser of the project and the editor
    of its edition.

    One admin user will be created.
    """
    baseDir = os.path.abspath("..")
    templateDir = f"{baseDir}/pilottemplate"
    dataDir = f"{baseDir}/pilotdata"
    workflowPath = f"{dataDir}/workflow/init.yml"

    if not dirExists(templateDir):
        print("Pilot template dir does not exist: {templateDir}")
        return False

    projectSource = f"{templateDir}/project/1"

    projects = list(range(1, amount + 1))

    for p in projects:
        projectDest = f"{dataDir}/project/{p}"
        dirCopy(projectSource, projectDest)
        makeItemIcon(p, "project", f"{projectDest}/icon.png")
        metaProject = f"{projectDest}/meta/dc.yml"
        fillinMeta(p, metaProject)
        editionDest = f"{projectDest}/edition/1"
        makeItemIcon(1, "edition", f"{editionDest}/icon.png")
        metaEdition = f"{editionDest}/meta/dc.yml"
        fillinMeta(p, metaEdition)

    users = {f"u{p:>02}": "user" for p in projects}
    users["a1"] = "admin"
    project = {f"{p}": {f"u{p:>02}": "organiser"} for p in projects}
    edition = {f"{p}": {"1": {f"u{p:>02}": "editor"}} for p in projects}
    projectStatus = {f"{p}": False for p in projects}
    editionStatus = {f"{p}": {"1": False} for p in projects}
    status = dict(
        project=dict(field="isVisible", values=projectStatus),
        edition=dict(field="isPublished", values=editionStatus),
    )

    workflow = dict(
        userRole=dict(site=users, project=project, edition=edition),
        status=status,
    )

    with open(workflowPath, "w") as fh:
        yaml.dump(workflow, fh)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print(HELP)
        print("Pass exactly one number 1..20 as argument")
        return

    number = args[0]

    try:
        number = int(number)
    except Exception:
        print(HELP)
        print(f"`{number}` is not a number.")
        print("Pass exactly one number 1..20 as argument")
        return

    if not (1 <= number <= 20):
        print(HELP)
        print(f"{number} is not in 1..20")
        return

    makePilotData(number)


if __name__ == "__main__":
    main()

# makeItemIcon(18, "project")
# makeItemIcon(2, "edition")
