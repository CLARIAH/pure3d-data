import os
from PIL import Image, ImageDraw, ImageFont

from files import dirMake


HELP = """

makeIcons.py

Makes a number of empty scratch and user projects icons
in directory *baseDir*/`icons`.
"""


N_SCRATCH = 99
N_USER = 99
N_EDITION = 99


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


def makeIcons():
    baseDir = os.path.abspath(".") + "/.."
    iconDir = f"{baseDir}/icons"
    dirMake(iconDir, fresh=True)

    for (kind, tp, amount) in (
        ("s", "project", N_SCRATCH),
        ("p", "project", N_USER),
        ("e", "edition", N_EDITION),
    ):
        for i in range(1, amount + 1):
            makeItemIcon(f"{kind}{i:>02}", tp, f"{iconDir}/{kind}{i:>02}.png")


def main():
    makeIcons()


if __name__ == "__main__":
    main()
