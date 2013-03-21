#!/usr/bin/python

import sqlite3
import urllib2
import zlib
import struct
import subprocess
import getpass
import sys
import codecs

basepath = "/Users/%s/Library/Application Support/Papers2/" % getpass.getuser()
dbpath = basepath + "Library.papers2/Database.papersdb"


alphabet = [chr(x) for x in range(ord('a'), ord('z')+1)]
title_suffix = [chr(x) for x in range(ord('t'), ord('w')+1)]
doi_suffix = [chr(x) for x in range(ord('b'), ord('k')+1)]


def gen_crc(s):
    # Re-interpret the signed int returned by zlib.crc32 as an unsigned int:
    return struct.unpack('I', struct.pack('=i', zlib.crc32(s)))[0]


def gen_citekey(s, x, suffixes1):
    n1 = gen_crc(s)
    n2 = n1 % x
    n3 = n2 / 26
    n4 = n2 % 26
    return "%s%s" % (suffixes1[n3], alphabet[n4])


def gen_title_citekey(title):
    if title is None: return None
    return gen_citekey(title, 104, title_suffix)


def gen_doi_citekey(doi):
    if doi is None: return None
    return gen_citekey(doi, 260, doi_suffix)


def decode(citekey):
    base, suffix = citekey.split(":")
    year = suffix[:4]
    citehash = suffix[4:]
    
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    
    result = cur.execute(
        "SELECT ROWID, canonical_title, doi FROM Publication "
        "WHERE citekey_base = ? AND substr(publication_date, 3, 4) == ?", (base, year))
    
    for (rowid, title, doi) in result:
        if citehash == gen_title_citekey(title) or citehash == gen_doi_citekey(doi):
            filepath = conn.execute("SELECT Path FROM PDF WHERE object_id = ?", (rowid,)).next()[0]
            return basepath + filepath
    
    raise Exception("No PDF found for %s" % citekey)


def open_citekey(citekey):
    fpath = decode(citekey)
    subprocess.call(["open", fpath])


def main(input_text):
    # Decode any URL escaping and remove any surrounding {}
    citekey = urllib2.unquote(input_text).strip().strip("{}")

    # now we have something like "author:2001qz"
    open_citekey(citekey)


if __name__ == "__main__":
    # Read the input.
    citekey = sys.argv[1]
    
    # Normalise UTF8 data to Unicode strings:
    try:
        citekey = codecs.utf_8_decode(citekey)[0]
    except UnicodeDecodeError:
        pass

    main(citekey)
