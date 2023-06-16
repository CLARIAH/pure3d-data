import sys

from files import fileExists, dirExists, dirCopy, dirMake, fileCopy, collectFiles


HELP = """

makeCustom.py sourceDir baseDir

Copies custom projects from a source directory to directory *baseDir*/`customdata`.
"""


def makeCustomData(sourceDir, baseDir):
    templateDir = f"{baseDir}/customdatatemplate"
    dataDir = f"{baseDir}/customdata"

    if not dirExists(sourceDir):
        print(f"custom: Custom source dir does not exist: {sourceDir}")
        return False

    if not dirExists(templateDir):
        print(f"custom: Custom template dir does not exist: {templateDir}")
        return False

    dirMake(dataDir, fresh=True)
    dirCopy(sourceDir, dataDir)

    for path in collectFiles(templateDir):
        templateFile = f"{templateDir}/{path}"
        dataFile = f"{dataDir}/{path}"
        if not fileExists(dataFile):
            fileCopy(templateFile, dataFile)


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print(HELP)
        print("custom: Pass a source and base directory")
        return

    (sourceDir, baseDir) = args[0:2]

    if not dirExists(sourceDir):
        print(f"custom: `{sourceDir}` does not exist")
        return

    makeCustomData(sourceDir, baseDir)


if __name__ == "__main__":
    main()
