import argparse
from opendm import io
from opendm import log
from opendm import context
from appsettings import SettingsParser

import sys

with open(io.join_paths(context.root_path, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()


def alphanumeric_string(string):
    import re
    if re.match('^[a-zA-Z0-9_-]+$', string) is None:
        msg = '{0} is not a valid name. Must use alphanumeric characters.'.format(string)
        raise argparse.ArgumentTypeError(msg)
    return string


parser = SettingsParser(description='DroneMapper MicMac',
                        usage='%(prog)s [options] <project name>',
                        yaml_file=open(context.settings_path))

def config():
    parser.add_argument('--images', '-i',
                       metavar='<path>',
                       help='Path to input images'),

    parser.add_argument('--project-path',
                       metavar='<path>',
                       help='Path to the project folder')

    parser.add_argument('name',
                       metavar='<project name>',
                       type=alphanumeric_string,
                       help='Name of Project (i.e subdirectory of projects folder)')

    parser.add_argument('--cores',
                        metavar='<integer>',
                        default=4,
                        type=int,
                        help='The maximum number of cores to use in processing. '
                            'Default: %(default)')

    parser.add_argument('--size',
                        metavar='<integer>',
                        default=800,
                        type=int,
                        help='Scale image width for tie-point extraction. '
                             'Default: %(default)')

    parser.add_argument('--zoom',
                        metavar='<integer>',
                        default=2,
                        type=int,
                        help='The level of DEM construction. 2 means 2x native GSD. '
                             'Default: %(default)')

    parser.add_argument('--matcher-distance',
                        metavar='<integer>',
                        type=int,
                        help='Distance threshold in meters to find pre-matching '
                             'images based on GPS exif data. Default: %(default)s')

    parser.add_argument('--version',
                        action='version',
                        version='DroneMapper MicMac {0}'.format(__version__),
                        help='Displays version number and exits. ')

    args = parser.parse_args()

    # check that the project path setting has been set properly
    if not args.project_path:
       log.MM_ERROR('You need to set the project path in the '
                    'settings.yaml file before you can run MicMac, '
                     'or use `--project-path <path>`. Run `python '
                     'run.py --help` for more information. ')
       sys.exit(1)

    return args