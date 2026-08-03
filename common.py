import re
import os
import csv
from datetime import datetime

#########################################################
# Constants
LETTERS_CASE_TYPE_UPPER = "ABC"
LETTERS_CASE_TYPE_LOWER = "abc"

NAME_CONVERT_ORIGINAL = "Original"
NAME_CONVERT_REPLACED = "Replaced"

WRITE_CSV_CLEAN = "Clean"
WRITE_CSV_ADD = "Add"
WRITE_CSV_UPDATE = "Update"

# CSV encodings to try, in order. cp932(Shift-JIS) is what Excel on
# Windows produces by default; utf-8-sig/utf-8 covers files exported
# from other tools (LibreOffice, text editors, this add-on's own
# export, etc). Blender 4.x itself doesn't change CSV handling, but
# fixing this here avoids UnicodeDecodeError / mojibake regardless of
# which tool produced the convert table.
CSV_READ_ENCODINGS = ("utf-8-sig", "cp932", "utf-8")

#########################################################
# Class
#########################################################


class BoneNameElements:

    bonename = ""
    basename = ""
    numid = ""
    basename_nonLR = ""
    lr_id = ""
    isPrefix = False
    isSuffix = False
    isLeft = False
    isRight = False
    isMirror = False
    lr_id_inv = ""
    mirror_bonename = ""


#########################################################
# Functions
#########################################################
# return BoneNameElements
def getNameElements(bone):

    # nonNumberNm = bone.basename
    nonNumberNm = re.split(r"\.(?=[0-9]+$)", bone.name)[0]
    num = bone.name.replace(nonNumberNm, "")
    baseNm = ""
    mirrBoneNm = None
    chr = ""
    mirrChr = ""
    isPrefix = False
    isSuffix = False
    isLeft = False
    isRight = False
    isMirror = False

    res = re.match(r"^(L[._\- ]|Left)(.+)", nonNumberNm, re.IGNORECASE)
    if res:
        chr = res.group(1)
        baseNm = res.group(2)
        isPrefix = True
        isLeft = True

    res = re.match(r"(.+)(?=([._\- ]L|[._\- ]?Left)$)", nonNumberNm, re.IGNORECASE)
    if res:
        chr = res.group(2)
        baseNm = res.group(1)
        isSuffix = True
        isLeft = True

    res = re.match(r"^(R[._\- ]|Right)(.+)", nonNumberNm, re.IGNORECASE)
    if res:
        chr = res.group(1)
        baseNm = res.group(2)
        isPrefix = True
        isRight = True

    res = re.match(r"(.+)(?=([._\- ]R|[._\- ]?Right)$)", nonNumberNm, re.IGNORECASE)
    if res:
        chr = res.group(2)
        baseNm = res.group(1)
        isSuffix = True
        isRight = True

    if isPrefix or isSuffix:
        isMirror = True

    if isPrefix:

        if isLeft:
            # Left to Right
            if chr == "Left":
                mirrChr = "Right"
            elif chr == "LEFT":
                mirrChr = "RIGHT"
            elif chr == "left":
                mirrChr = "right"
            else:
                res = re.match(r"(L)([._\- ])", chr, re.IGNORECASE)
                if res.group(1) == "l":
                    mirrChr = "r" + res.group(2)
                elif res.group(1) == "L":
                    mirrChr = "R" + res.group(2)

        if isRight:
            # Right to Left
            if chr == "Right":
                mirrChr = "Left"
            elif chr == "RIGHT":
                mirrChr = "LEFT"
            elif chr == "right":
                mirrChr = "left"
            else:
                res = re.match(r"(R)([._\- ])", chr, re.IGNORECASE)
                if res.group(1) == "r":
                    mirrChr = "l" + res.group(2)
                elif res.group(1) == "R":
                    mirrChr = "L" + res.group(2)

        mirrBoneNm = mirrChr + baseNm + num

    if isSuffix:

        if isLeft:
            # Left to Right
            if chr == "Left":
                mirrChr = "Right"
            elif chr == "LEFT":
                mirrChr = "RIGHT"
            elif chr == "left":
                mirrChr = "right"
            else:
                res = re.match(r"([._\- ])(L)", chr, re.IGNORECASE)
                if res.group(2) == "l":
                    mirrChr = res.group(1) + "r"
                elif res.group(2) == "L":
                    mirrChr = res.group(1) + "R"

        if isRight:

            # Right to Left
            if chr == "Right":
                mirrChr = "Left"
            elif chr == "RIGHT":
                mirrChr = "LEFT"
            elif chr == "right":
                mirrChr = "left"
            else:
                res = re.match(r"([._\- ])(R)", chr, re.IGNORECASE)
                if res.group(2) == "r":
                    mirrChr = res.group(1) + "l"
                elif res.group(2) == "R":
                    mirrChr = res.group(1) + "L"

        mirrBoneNm = baseNm + mirrChr + num

    ret = BoneNameElements()
    ret.bonename = bone.name
    ret.basename = nonNumberNm
    ret.numid = num
    ret.basename_nonLR = baseNm
    ret.lr_id = chr
    ret.isPrefix = isPrefix
    ret.isSuffix = isSuffix
    ret.isLeft = isLeft
    ret.isRight = isRight
    ret.isMirror = isMirror
    ret.lr_id_inv = mirrChr
    ret.mirror_bonename = mirrBoneNm

    return ret

#     return (bone.name, nonNumberNm, num, baseNm, chr, isPrefix, isSuffix, isLeft, isRight, isMirror, mirrChr, mirrBoneNm)


def constructBoneName(baseNm, chr, num, isPrefix, isSuffix):

    if isPrefix:

        return chr + baseNm + num

    elif isSuffix:

        return baseNm + chr + num

    else:

        return baseNm + num


def getPaddingStringByDigit(num, padding):

    fPtn = "{0:0" + str(padding) + "d}"

    return fPtn.format(num)


# idx is 0-origin
def getAlphabetByNumber(idx, type):

    stChr = _alphaBetStartChrNum(type)
    ret = []

    mod = idx % 26
    i = mod + stChr
    ret.append(chr(i))
    next = (idx - mod) / 26

    while next != 0:
        mod = (next - 1) % 26
        i = mod + stChr
        ret.append(chr(int(i)))
        next = (next - 1 - mod) / 26

    ret.reverse()
    return "".join(ret)


def _alphaBetStartChrNum(type):

    if type == LETTERS_CASE_TYPE_UPPER:
        return 65
    else:
        return 97


def isEmptyStr(str):

    if str == "" or str is None:
        return True
    else:
        return False


#########################################################
# CSV helpers
#########################################################
def openCsvReader(path):
    """
    Open a CSV file for reading, auto-detecting the text encoding.
    Returns (file_handle, csv.reader). Caller is responsible for
    closing file_handle (or use it as a context manager).

    This replaces the old hard-coded encoding='cp932' open() calls,
    which fail (UnicodeDecodeError) or silently mojibake on CSV files
    that were saved as UTF-8 (e.g. by LibreOffice, text editors, or
    this add-on's own "Export CSV" button on non-Windows systems).
    """

    last_err = None
    for enc in CSV_READ_ENCODINGS:
        try:
            f = open(path, newline='', encoding=enc)
            # Force-read once to validate the encoding before handing
            # back a reader positioned at the start of the file.
            f.read()
            f.seek(0)
            return f, csv.reader(f)
        except UnicodeDecodeError as e:
            last_err = e
            try:
                f.close()
            except Exception:
                pass
            continue

    # Fall back to cp932 with errors replaced, rather than crashing
    # outright, so the user at least gets a readable error/result.
    f = open(path, newline='', encoding='cp932', errors='replace')
    return f, csv.reader(f)


#########################################################
# Bone visibility (Bone Collections, Blender 4.0+)
#########################################################
# NOTE: These two helpers are not currently called anywhere in the
# add-on (they were already unused in the original 0.2 release), but
# they used the bone-layers API (Bone.layers / Armature.layers /
# EditBone.layers) which was removed in Blender 4.0 in favor of Bone
# Collections. They are rewritten here so they don't raise
# AttributeError if anything starts calling them again.
def isVisiblePoseBone(bone):

    if not bone:
        return False

    if bone.bone.hide:
        return False

    return _isBoneInVisibleCollection(bone.bone)


def isVisibleBone(bone):

    if not bone:
        return False

    if bone.hide:
        return False

    return _isBoneInVisibleCollection(bone)


def _isBoneInVisibleCollection(bone):
    """
    bone: bpy.types.Bone or bpy.types.EditBone
    Works with Blender 4.0+ Bone Collections. Falls back to the old
    Bone.layers list for Blender <= 3.6, so the add-on keeps working
    on either API without a hard version check.
    """

    collections = getattr(bone, "collections", None)
    if collections is not None:
        # Blender 4.0+: no collection assigned == always visible.
        if len(collections) == 0:
            return True
        return any(col.is_visible for col in collections)

    # Blender <= 3.6 fallback (old 20-slot bone layers).
    layers = getattr(bone, "layers", None)
    if layers is None:
        return True

    armature_data = bone.id_data
    arm_layers = getattr(armature_data, "layers", None)
    if arm_layers is None:
        return True

    for idx, isLayer in enumerate(layers):
        if isLayer and arm_layers[idx]:
            return True

    return False


def getBackupFileNameByDate(orgNm, dt):

    base, ext = os.path.splitext(orgNm)

    return base + "_bkup" + dt.strftime("%Y%m%d%H%M%S") + ext


def getBackupFileName(orgNm):

    return getBackupFileNameByDate(orgNm, datetime.today())
