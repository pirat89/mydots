#!/usr/bin/python

"""
This is really just set of simple functions that could be quite useful
in various situation when you want to "parse" e.g. configuration files.
Now it contains function that removes comments and function that finds
equivalent closing element (bracket, quotes, ...) to the first character
of the given string. - It's usable for me in some cases but it is far away
from real parsing.
"""

import re

###########################################################
### functions that helps with pseudo parsing of config file
###########################################################
def is_comment_start(istr, index=0):
    if istr[index] == "#" or (
            index+1 < len(istr) and istr[index:index+2] in ["//", "/*"]):
        return True
    return False

def find_end_of_comment(istr, index=0):
    """
    Returns index where the comment ends.

    :param istr: input string
    :param index: begin search from the index; from the start by default

    Support usual comments till the end of line (//, #) and block comment
    like (/* comment */). In case that index is outside of the string or end
    of the comment is not found, return -1.

    In case of block comment, returned index is position of slash after star.
    """
    length = len(istr)

    if index >= length or index < 0:
        return -1

    if istr[index] == "#" or istr[index:].startswith("//"):
        return istr.find("\n", index)

    if index+2 < length and istr[index:index+2] == "/*":
        res = istr.find("*/", index+2)
        if res != -1:
            return res + 1

    return -1

def is_opening_char(c):
     return c in "\"'{(["

def find_next_token(istr,index=0):
    """
    Return index of another interesting token or -1 when there is not next.

    :param istr: input string
    :param index: begin search from the index; from the start by default

    In case that initial index contains already some token, skip to another.
    But when searching starts on whitespace or beginning of the comment,
    choose the first one.

    The function would be confusing in case of brackets, but content between
    brackets is not evaulated as new tokens.
    E.g.:

    "find { me };"      : 5
    " me"               : 1
    "find /* me */ me " : 13
    "/* me */ me"       : 9
    "me;"               : 2
    "{ me }; me"        : 6
    "{ me }  me"        : 8
    "me }  me"          : 3
    "}} me"             : 1
    "me"                : -1
    "{ me } "           : -1

    BUG: position in input data is really important, because we have troubles
         with quotes and apostrophes. In these two cases be sure, that when
         searching begins on \" or \' charachters, function will try find
         end of the string. So for the string --foo " bar "; foo1 " bar1 "--
         when you start on the second quote, you will get index of bar1
         instead of expected semicolon. It is highly recommended to start
         searching on the beginning of the current token, so you will be sure,
         that you skip really to the next one.
    """
    length = len(istr)
    if index >= length or index < 0:
        return -1

    #skip to the end of the current token
    if is_opening_char(istr[index]):
        index2 = find_closing_char(istr, index)
        if index2 == -1:
            return -1
        index = index2 +1;
    elif is_comment_start(istr, index):
        index2 = find_end_of_comment(istr, index)
        if index2 == -1:
            return -1
        index = index2 +1
    elif istr[index] not in "\n\t ;})]":
        # so we have to skip to the end of the current token
        index += 1
        while index < length:
            if (istr[index] in "\n\t ;})]"
                    or is_comment_start(istr, index)
                    or is_opening_char(istr[index])):
                break
            index += 1
    elif istr[index] in ";)]}":
        index += 1

    # find next token (can be already under the current index)
    while index < length:
        if is_comment_start(istr, index):
            index = find_end_of_comment(istr, index)
            if index == -1:
                break
        elif is_opening_char(istr[index]) or istr[index] not in "\t\n ":
            return index
        index += 1
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
    important_chars = { #TODO: should be that rather global var?
        "{" : "}",
        "(" : ")",
        "[" : "]",
        "\"" : "\"",
        "'" : "'",
        }
    length = len(istr)

    if length < 2:
        return -1

    if index >= length or index < 0:
        return -1

    closing_char = important_chars.get(istr[index], None)
    if closing_char is None:
        return -1

    isString = istr[index] in "\"'"
    index += 1
    curr_c = ""
    while index < length:
        curr_c = istr[index]
        if curr_c == "\\":
            index += 1
        elif is_comment_start(istr, index) and not isString:
            index = find_end_of_comment(istr, index)
            if index == -1:
                return -1
        elif not isString and is_opening_char(curr_c):
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
        if is_comment_start(istr, index):
            index = find_end_of_comment(istr,index)
            if index == -1:
                # comment till EOF
                break
            if istr[index] == "\n":
                ostr += "\n"
        elif istr[index] in str_open:
            end_str = find_closing_char(istr, index)
            if end_str == -1:
                ostr += istr[index:]
                break
            ostr += istr[index:end_str+1]
            index = end_str
        else:
            ostr += istr[index]
        index += 1

    return ostr

def find_key(istr, key, index=0):
    """
    Return index of the key or -1.

    :param istr: input string; it could be whole file or content of a section
    :param index: start searching from the index
    :param key: name of the searched key in the current scope

    Funtion is not recursive. Searched key has to be in the current scope.
    Attention:

     In case that input string contains data outside of section by
    mistake, the closing character is ignored and the key outside of scope
    could be found. Example of such wrong input could be:
          key1 "val"
          key2 { key-ignored "val-ignored" };
        };
        controls { ... };
    In this case, the key "controls" is outside of original scope.
    """
    length = len(istr)
    keylen = len(key)
    notFirstKey = False

    if index >= length or index < 0:
        return -1

    while index != -1:
        if istr.startswith(key, index):
            if index+keylen < length and istr[index+keylen] in "\n\t {;":
                # key has been found
                return index

        while notFirstKey and index != -1 and istr[index] != ";":
            index = find_next_token(istr, index)
        index = find_next_token(istr, index)

    return -1


#######################################################
if __name__ == "__main__":
    from pprint import pprint
    getoc = find_end_of_comment
    bb = lambda x,y: (getoc(x,y), aa[getoc(x,y)], aa[getoc(x,y):])

    aa = "aho// kdyby /*/ neco\n ahahaa */ jo"
    pprint(aa)
    for i in range(0,19):
        pprint((i, bb(aa,i)))

    for i in range(0,19):
        pprint((i, remove_comments(aa[i:])))

    cc = """
# options {
# whatever "akdf"; // };
# neco { fjaka ; } ; /*
# kdyby-sos "kdo vi co" }; // */
#};

options {
 valid "akdf"; // };
 valid-1 { fjaka ; } ; /*
 invalid-trap "kdo vi co" }; // */
}; controls { tak-to-je-labuzo "ba ze"; a-tak-dale { /* { trap } ; */ kdyby { nahodou "prselo}"; }; } ; } ;
# fake "fs" };

controls {
     # .---
     ;
};
    """

    print "============ REMOVE =============="
    print remove_comments(cc)
    print "=================================="
    index = 0
    ccl= len(cc)
    prev_index = -2
    #import pdb; pdb.set_trace()

    while index < ccl and index != -1:
        if index == prev_index:
            print index, "SHIT ==== ", cc[index:], "\n"
            break
        prev_index = index
        index = find_next_token(cc, index)
        print(index, cc[index:])
    print "=================================="
    index = find_closing_char(cc, 108)
    print (index, cc[index:])
    print "=================================="
    index = find_key(cc, "controls", 0)
    print (index, cc[index:])
    print "=================================="
    index = find_key(cc, "options", 0)
    print (index, cc[index:])


