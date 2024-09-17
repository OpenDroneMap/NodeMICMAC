import os
import errno
import datetime
import subprocess

from opendm import log


def run(cmd, env_vars={}):
    """Run a system command"""
    log.MM_DEBUG('running %s' % cmd)

    env = os.environ.copy()
    env["PATH"] = env["PATH"] + ":" + "::/code:/code/micmac/bin:/code/micmac/binaire-aux/linux"

    for k in env_vars:
        env[k] = str(env_vars[k])

    retcode = subprocess.call(cmd, shell=True, env=env)

    if retcode < 0:
        log.MM_ERROR("Child was terminated by signal {}".format(-retcode))
    elif retcode > 0:
        log.MM_ERROR("Child returned {}".format(retcode))


def now():
    """Return the current time"""
    return datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')


def now_raw():
    return datetime.datetime.now()


def benchmark(start, benchmarking_file, process):
    """
    runs a benchmark with a start datetime object
    :return: the running time (delta)
    """
    # Write to benchmark file
    delta = (datetime.datetime.now() - start).total_seconds()
    with open(benchmarking_file, 'a') as b:
        b.write('%s runtime: %s seconds\n' % (process, delta))


def mkdir_p(path):
    """Make a directory including parent directories.
    """
    try:
        os.makedirs(path)
    except os.error as exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise


def calculate_EPSG(utmZone, south):
    """Calculate and return the EPSG"""
    if south:
        return 32700 + utmZone
    else:
        return 32600 + utmZone
