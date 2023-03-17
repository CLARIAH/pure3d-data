import os
import yaml
import re
from shutil import rmtree, copytree, copy


THREE_EXT = {"glb", "gltf"}
THREE_EXT_PAT = "|".join(THREE_EXT)

IMAGE_RE = re.compile(r"""^.*\.(png|jpg|jpeg)$""", re.I)
THREED_RE = re.compile(fr"""^.*\.({THREE_EXT_PAT})$""", re.I)


class AttrDict(dict):
    """Turn a dict into an object with attributes.

    If non-existing attributes are accessed for reading, `None` is returned.

    See:
    https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute

    And:
    https://stackoverflow.com/questions/16237659/python-how-to-implement-getattr
    (especially the remark that

    > `__getattr__` is only used for missing attribute lookup

    )

    We also need to define the `__missing__` method in case we access the underlying
    dict by means of keys, like `xxx["yyy"]` rather then by attribute like `xxx.yyy`.
    """

    def __init__(self, *args, **kwargs):
        """Create the data structure from incoming data.
        """
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __missing__(self, key, *args, **kwargs):
        """Provide a default when retrieving a non-existent member.

        This method is used when using the `.key` notation for accessing members.
        """
        return None

    def __getattr__(self, key, *args, **kwargs):
        """Provide a default when retrieving a non-existent member.

        This method is used when using the `[key]` notation for accessing members.
        """
        return None


def deepAttrDict(info):
    """Turn a dict into an AttrDict, recursively.

    Parameters
    ----------
    info: any
        The input dictionary. We assume that it is a data structure built by
        tuple, list, set, frozenset, dict and atomic types such as int, str, bool.
        We assume there are no user defined objects in it,
        and no generators and functions.

    Returns
    -------
    AttrDict
        An AttrDict containing the same info as the input dict, but where
        each value of type dict is turned into an AttrDict.
    """
    return (
        AttrDict({k: deepAttrDict(v) for (k, v) in info.items()})
        if type(info) is dict
        else tuple(deepAttrDict(item) for item in info)
        if type(info) is tuple
        else frozenset(deepAttrDict(item) for item in info)
        if type(info) is frozenset
        else [deepAttrDict(item) for item in info]
        if type(info) is list
        else {deepAttrDict(item) for item in info}
        if type(info) is set
        else info
    )


def readPath(filePath):
    """Reads the (textual) contents of a file.

    !!! note "Not for binary files"
        The file will not be opened in binary mode.
        Use this only for files with textual content.

    Parameters
    ----------
    filePath: string
        The path of the file on the file system.

    Returns
    -------
    string
        The contents of the file as unicode.
        If the file does not exist, the empty string is returned.
    """

    if os.path.isfile(filePath):
        with open(filePath) as fh:
            text = fh.read()
        return text
    return ""


def readYaml(path, defaultEmpty=False):
    """Reads a yaml file.

    Parameters
    ----------
    filePath: string
        The path of the file on the file system.
    defaultEmpty: boolean, optional False
        What to do if the file does not exist.
        If True, it returns an empty AttrDict
        otherwise False.

    Returns
    -------
    AttrDict | void
        The data content of the yaml file if it exists.
    """
    if not os.path.isfile(path):
        return None
    with open(path) as fh:
        data = yaml.load(fh, Loader=yaml.FullLoader)
    return deepAttrDict(data)


def fileExists(path):
    """Whether a path exists as file on the file system.
    """
    return os.path.isfile(path)


def fileRemove(path):
    """Removes a file if it exists as file.
    """
    if fileExists(path):
        os.remove(path)


def fileCopy(pathSrc, pathDst):
    """Copies a file if it exists as file.

    Wipes the destination file, if it exists.
    """
    if fileExists(pathSrc):
        fileRemove(pathDst)
        copy(pathSrc, pathDst)


def dirExists(path):
    """Whether a path exists as directory on the file system.
    """
    return os.path.isdir(path)


def dirRemove(path):
    """Removes a directory if it exists as directory.
    """
    if dirExists(path):
        rmtree(path)


def dirCopy(pathSrc, pathDst):
    """Copies a directory if it exists as directory.

    Wipes the destination directory, if it exists.
    """
    if dirExists(pathSrc):
        dirRemove(pathDst)
        copytree(pathSrc, pathDst)


def dirMake(path, fresh=True):
    """Creates a directory if it does not already exist as directory.

    If `fresh`, it will clear the directory first, if it exists.
    """
    if dirExists(path):
        if fresh:
            dirRemove(path)

    if not dirExists(path):
        os.makedirs(path, exist_ok=True)


def listDirs(path):
    """The list of all subdirectories in a directory.

    If the directory does not exist, the empty list is returned.
    """
    if not dirExists(path):
        return []

    subdirs = []

    with os.scandir(path) as dh:
        for entry in dh:
            if entry.is_dir():
                name = entry.name
                subdirs.append(name)

    return subdirs


def listFiles(path, ext):
    """The list of all files in a directory with a certain extension.

    If the directory does not exist, the empty list is returned.
    """
    if not dirExists(path):
        return []

    files = []

    nExt = len(ext)
    with os.scandir(path) as dh:
        for entry in dh:
            name = entry.name
            if name.endswith(ext) and entry.is_file():
                files.append(name[0:-nExt])

    return files


def listFilesAccepted(path, accept, withExt=True):
    """The list of all files in a directory that match a certain accepted header.

    If the directory does not exist, the empty list is returned.
    """
    if not dirExists(path):
        return []

    files = []

    exts = [ext.strip() for ext in accept.split(",")]

    with os.scandir(path) as dh:
        for entry in dh:
            name = entry.name
            for ext in exts:
                nExt = len(ext)
                if name.endswith(ext) and entry.is_file():
                    fileName = name if withExt else name[0:-nExt]
                    files.append(fileName)

    return files


def listImages(path):
    """The list of all image files in a directory.

    If the directory does not exist, the empty list is returned.

    An image is a file with extension .png, .jpg, .jpeg or any of its
    case variants.
    """
    if not dirExists(path):
        return []

    files = []

    with os.scandir(path) as dh:
        for entry in dh:
            name = entry.name
            if IMAGE_RE.match(name) and entry.is_file():
                files.append(name)

    return files


def list3d(path):
    """The list of all 3D files in a directory.

    If the directory does not exist, the empty list is returned.

    An image is a file with extension .gltf, .glb or any of its
    case variants.
    """
    if not dirExists(path):
        return []

    files = []

    with os.scandir(path) as dh:
        for entry in dh:
            name = entry.name
            if THREED_RE.match(name) and entry.is_file():
                files.append(name)

    return files
