#!/usr/bin/python

"""
This is really just set of simple functions that could be quite useful
in various situation when you want to "parse" e.g. configuration files.
Now it contains function that removes comments and function that finds
equivalent closing element (bracket, quotes, ...) to the first character
of the given string. - It's usable for me in some cases but it is far away
from real parsing.
"""

###########################################################
### functions that helps with pseudo parsing of config file
###########################################################
def get_end_of_comment(istr, index=0):
    """
    Returns index where the comment ends.

    :param istr: input string
    :param index: begin search from the index - from the start by default

    Support usual comments till the end of line (//, #) and block comment
    like (/* comment */). In case that index is outside of the string or end
    of the comment is not found, return -1.
    """
    isBlockComment = False
    length = len(istr)

    if index > length or index < 0:
        return -1

    if istr[index] == "#" or istr[index:].startswith("//"):
        return istr.find("\n", index)

    if index+2 < length and istr[index:index+2] == "/*":
        return istr.find("/*", index+2)

    return -1


def find_closing_char(istr, index=0):
    """
    Returns index of equivalent closing character.

    :param istr: input string

    It's similar to the "find" method that returns index of the first character
    of the searched character or -1. But in this function the corresponding
    closing character is looked up, ignoring characters inside strings
    and comments. E.g. for
        "(hello (world) /* ) */ ), he would say"
    index of the third ")" is returned.
    """
    isCommented = False
    isBlockComment = False
    important_chars = {
        "{" : "}",
        "(" : ")",
        "[" : "]",
        "\"" : "\"",
        "'" : "'",
        }
    opening_char = important_chars.keys()
    length = len(istr)

    if length < 2:
        return -1

    if index > length or index < 0:
        return -1

    closing_char = important_chars.get(istr[index], None)
    if closing_char is None:
        return -1

    isString = istr[index] in "\"'"
    index += 1
    curr_c = ""
    while index < length:
        curr_c = istr[index]
        if isCommented:
            if curr_c == "\n" and not isBlockComment:
                isCommented = False
            elif isBlockComment and (index + 1) < length \
                                and istr[index:index+2] == "*/":
                isBlockComment = False
                isCommented = False
                index += 1
        elif curr_c == "\\":
            index += 1
        elif not isString and curr_c == "#":
            isCommented = True
        elif not isString and curr_c == "/":
            if index + 1 < length:
                if istr[index + 1] == "*":
                    isBlockComment = True
                    index += 1
                elif istr[index + 1] == "/":
                    index += 1
        elif not isString and curr_c in opening_char:
            deep_close = find_closing_char(istr[index:])
            if deep_close == -1:
                break
            index += deep_close
        elif curr_c == closing_char:
            return index
        index += 1

    return -1

def remove_comments(istr):
    """
    Removes all comments from the given string.

    :param istr: input string
    :return: return
    """

    isCommented = False
    isBlockComment = False
    str_open = "\"'"
    ostr = ""

    length = len(istr)
    index = 0

    while index < length:
        if isCommented:
            if istr[index] == "\n" and not isBlockComment:
                isCommented = False
            elif isBlockComment and (index + 1) < length \
                                and istr[index:index+2] == "*/":
                isBlockComment = False
                isCommented = False
                index += 1
            index += 1
            continue
        if istr[index] == "#":
            isCommented = True
            index += 1
            continue
        if istr[index] == "/":
            if index + 1 < length:
                if istr[index + 1] == "*":
                    isBlockComment = True
                    isCommented = True
                elif istr[index + 1] == "/":
                    isCommented = True
                if isCommented:
                    index += 2
                    continue
        if istr[index] in str_open:
            end_str = get_index_of_closing_char(istr[index:])
            if end_str == -1:
                # instead of error, rather return original content;
                # but it seems that config file is not correct
                return istr
            ostr += istr[index:index+end_str+1]
            index += end_str + 1
            continue
        ostr += istr[index]
        index += 1

    return ostr

def find_section(istr, section):
    """
    Return index of the section or -1.

    :param istr: input string
    :param section: name of the searched section, e.g. "options"
    """

    index = 0
    length = len(istr)

#######################################################
