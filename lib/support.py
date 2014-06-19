# pylint: disable=missing-docstring,line-too-long,too-many-public-methods,

import argparse
import logging
import json
import FixedFifo
import default
from urllib import FancyURLopener
import cPickle as pickle
import os

def get_verbosity_level():

    # build the parser
    parser = argparse.ArgumentParser(prog='e621dl',
        description='automated e621 downloader.\
        add artists/tags to tags.txt and run!')

    # add mutually exclusive options verbose/quiet
    verbosity = parser.add_mutually_exclusive_group(required=False)
    verbosity.add_argument('-v', '--verbose', action='store_true',
        help='display debug information while running')
    verbosity.add_argument('-q', '--quiet', action='store_true',
        help='display no output while running (except errors)')

    # parse using argparser
    args = parser.parse_args()

    if args.quiet:
        return logging.ERROR
    elif args.verbose:
        return logging.DEBUG
    else:
        return logging.INFO

def make_default_configfile(filename):
    log = logging.getLogger('configfile')
    log.error('new default file created: ' + filename)
    log.error('verify this new config file and re-run the program')
    with open(filename, 'w') as outfile:
        json.dump(default.CONFIG_FILE, outfile, indent=4, sort_keys=True,)
    return default.CONFIG_FILE

def read_configfile(filename):
    log = logging.getLogger('configfile')
    with open(filename, 'r') as infile:
        log.debug('opened ' + filename)
        return json.load(infile)

def make_default_tagfile(filename):
    log = logging.getLogger('tagfile')
    with open(filename, 'w') as outfile:
        outfile.write(default.TAG_FILE)

    log.error('new default file created: ' + filename)
    log.error('please add tags you wish to this file and re-run the program')

def read_tagfile(filename):
    log = logging.getLogger('tagfile')
    tag_list = []

    # read out all lines not starting with #
    for line in open(filename):
        raw_line = line.strip()
        if not raw_line.startswith("#"):
            tag_list.append(raw_line)

    log.debug('opened ' + filename + ' and read ' + str(len(tag_list)) + ' items')
    return tag_list

def get_cache(filename, size):
    log = logging.getLogger('cache')
    try:
        cache = pickle.load(open(filename, 'rb'))
        cache.resize(size)
        log.debug('loaded existing cache')
        log.debug('capacity = ' + str(len(cache)) + ' of ' + str(cache.size()))
        log.debug('size on disk = ' + str(os.path.getsize(filename)/1024) + 'kb')

    except IOError:
        cache = FixedFifo.FixedFifo(size)
        log.debug('new blank cache created. size = ' + str(size))

    return cache


def sub_char(char):
    illegal = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ']
    return '_' if char in illegal else char

def safe_filename(tag_line, item, config_dict):
    safe_tagline = ''.join([sub_char(c) for c in tag_line])

    if config_dict['create_subdirectories'] == True:
        if not os.path.isdir(config_dict['download_directory'] + safe_tagline):
            os.makedirs(config_dict['download_directory'] + safe_tagline)
        safe_filename = safe_tagline + '/' + item.md5 + '.' + item.ext

    else:
        safe_filename = safe_tagline + '_' + item.md5 + '.' + item.ext

    return safe_filename

class SpoofOpen(FancyURLopener):
    version = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12'
