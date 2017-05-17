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
def get_index_of_closing_char(istr):
    isCommented = False
    isBlockComment = False
    index = 1
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

    closing_char = important_chars.get(istr[0], None)
    if closing_char is None:
        return -1

    isString = istr[0] in "\"'"
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
            deep_close = get_index_of_closing_char(istr[index:])
            if deep_close == -1:
                break
            index += deep_close
        elif curr_c == closing_char:
            return index
        index += 1

    return -1

def remove_comments(istr):
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
                return None
            ostr += istr[index:index+end_str+1]
            index += end_str + 1
            continue
        ostr += istr[index]
        index += 1

    return ostr

