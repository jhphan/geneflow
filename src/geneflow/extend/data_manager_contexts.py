"""
This module contains data management extension functions for various contexts.
"""

import os
import shutil
from wcmatch import glob

from geneflow.log import Log
from geneflow.uri_parser import URIParser


### Local data management functions and move/copy with Local as source

def _list_local(uri, globstr, local=None):
    """
    List contents of local URI.

    Args:
        uri: parsed URI to list.
        local: local context options.

    Returns:
        On success: a list of filenames (basenames only).
        On failure: False.

    """
    prefix_length = len(uri['chopped_path'])+1
    #recursive = True if '**' in globstr else False
    try:
        file_list = [
            item[prefix_length:] for item in glob.glob(
                uri['chopped_path']+'/'+globstr,
                flags=glob.EXTGLOB|glob.GLOBSTAR
            ) if item[prefix_length:]
        ]

    except OSError as err:
        Log.an().error(
            'cannot get file list for uri: %s [%s]',
            uri['chopped_uri'], str(err)
        )
        return False

    return file_list


def _exists_local(uri, local=None):
    """
    Check if local URI exists.

    Args:
        uri: parsed URI to check.
        local: local context options.

    Returns:
        True if the URI exists, False otherwise.

    """
    return os.path.exists(uri['chopped_path'])


def _mkdir_local(uri, local=None):
    """
    Create local directory specified by URI.

    Args:
        uri: parsed URI to create.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    try:
        os.makedirs(uri['chopped_path'])

    except OSError as err:
        Log.an().error(
            'cannot create uri: %s [%s]', uri['chopped_uri'], str(err)
        )
        return False

    return True


def _mkdir_recursive_local(uri, local=None):
    """
    Recursively create local directory specified by URI.

    Args:
        uri: parsed URI to create.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    # same as the non-recursive call
    return _mkdir_local(uri, local)


def _delete_local(uri, local=None):
    """
    Delete local file/folder specified by URI.

    Args:
        uri: parsed URI to delete.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    try:
        shutil.rmtree(uri['chopped_path'])

    except OSError as err:
        Log.an().error(
            'cannot delete uri: %s [%s]', uri['chopped_uri'], str(err)
        )
        return False

    return True


def _copy_local_local(src_uri, dest_uri, local=None):
    """
    Copy local data with system shell.

    Args:
        src_uri: Source URI parsed into dict with URIParser.
        dest_uri: Destination URI parsed into dict with URIParser.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    try:
        shutil.copytree(
            src_uri['path'],
            dest_uri['path']
        )
    except OSError as err:
        Log.an().error(
            'cannot copy from %s to %s [%s]',
            src_uri['uri'],
            dest_uri['uri'],
            str(err)
        )
        return False

    return True


def _move_local_local(src_uri, dest_uri, local=None):
    """
    Move local data with system shell.

    Args:
        src_uri: Source URI parsed into dict with URIParser.
        dest_uri: Destination URI parsed into dict with URIParser.
        local: local context options.

    Returns:
        On success: True.
        On failure: False.

    """
    try:
        shutil.move(
            src_uri['path'],
            dest_uri['path']
        )
    except OSError as err:
        Log.an().error(
            'cannot move from %s to %s [%s]',
            src_uri['uri'],
            dest_uri['uri'],
            str(err)
        )
        return False

    return True
