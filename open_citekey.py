#!/usr/bin/python

import sqlite3
import urllib2
import zlib
import struct
import subprocess
import getpass
import codecs
import sys
import os


basepath = "/Users/%s/Library/Application Support/Papers2/" % getpass.getuser()
dbpath = basepath + "Library.papers2/Database.papersdb"

alphabet = [chr(x) for x in range(ord('a'), ord('z')+1)]
title_suffix = [chr(x) for x in range(ord('t'), ord('w')+1)]
doi_suffix = [chr(x) for x in range(ord('b'), ord('k')+1)]


def gen_crc(s):
    # Re-interpret the signed int returned by zlib.crc32 as an unsigned int:
    return struct.unpack('I', struct.pack('=i', zlib.crc32(s)))[0]


def gen_hash(text, suffixes):
    n1 = gen_crc(text)
    n2 = n1 % (len(alphabet) * len(suffixes))
    n3 = n2 / len(alphabet)
    n4 = n2 % len(alphabet)
    return "%s%s" % (suffixes[n3], alphabet[n4])


def gen_title_hash(title):
    if title is None: return None
    return gen_hash(title, title_suffix)


def gen_doi_hash(doi):
    if doi is None: return None
    return gen_hash(doi, doi_suffix)


def find_pdf(citekey):
    base, suffix = citekey.split(":")
    year = suffix[:4]
    citehash = suffix[4:]
    
    conn = sqlite3.connect(dbpath)

    # Papers does not store the hash part of the citekey in its database.
    # First do a partial match on the base (author) and year:
    candidates = conn.execute(
        "SELECT ROWID, canonical_title, doi FROM Publication "
        "WHERE citekey_base = ? AND substr(publication_date, 3, 4) == ?",
        (base, year))
    
    # Now generate the hashes for these candidates and look for an exact match:
    for (rowid, title, doi) in candidates:
        if (citehash == gen_title_hash(title) or
            citehash == gen_doi_hash(doi)):
            # Got a match for the complete citekey!
            # Let's see if we can find any PDF files for this paper:
            pdfs = conn.execute("SELECT Path FROM PDF WHERE object_id = ?",
                                (rowid,))
            # Return the first PDF entry:
            for (pdf_path,) in pdfs:
                return os.path.join(basepath, pdf_path)
            # If no PDF was found, move on to next matching paper:
            # there might be duplicates entries with the same hash.

    raise Exception("No matching PDF found for %s" % citekey)


def open_citekey(citekey):
    fpath = find_pdf(citekey)
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
