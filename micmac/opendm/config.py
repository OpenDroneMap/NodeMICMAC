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

    parser.add_argument('--gcp',
                        metavar='<path>',
                        help='Path to the gcp files')

    parser.add_argument('name',
                       metavar='<project name>',
                       type=alphanumeric_string,
                       help='Name of Project (i.e subdirectory of projects folder)')

    parser.add_argument('--max-concurrency',
                        metavar='<integer>',
                        default=4,
                        type=int,
                        help='The maximum number of cores to use in processing. '
                            'Default: 4')

    parser.add_argument('--resize-to',
                        metavar='<integer>',
                        default=800,
                        type=int,
                        help='Scale image width for tie-point extraction. '
                             'Default: 800')

    parser.add_argument('--zoom',
                        metavar='<integer>',
                        default=4,
                        type=int,
                        help='The level of DEM construction. 4 means 4x native GSD. '
                             'Default: 4 Values: 1, 2, 4, 8')

    parser.add_argument('--matcher-distance',
                        metavar='<integer>',
                        type=int,
                        help='Distance threshold in meters to find pre-matching '
                             'images based on GPS exif data. Default: 0')

    parser.add_argument('--multi-scale',
                        action='store_true',
                        default=False,
                        help='Uses an image file pair based multi-scale tie-point '
                             'generation routine similar to Photoscan.')

    parser.add_argument('--remove-ortho-tiles',
                        action='store_true',
                        default=False,
                        help='Remove every other ortho tile. Speeds up ortho creation and radiometric equalization.')

    parser.add_argument('--camera-cloud',
                        action='store_true',
                        default=False,
                        help='Creates a sparse point cloud with camera positions')

    parser.add_argument('--image-footprint',
                        action='store_true',
                        default=False,
                        help='Creates a point cloud and geojson with image footprints')

    parser.add_argument('--ccd-width',
                        metavar='<float>',
                        type=float,
                        help='The CCD sensor width in millimeters (mm). Example: 6.17')

    parser.add_argument('--ccd-height',
                        metavar='<float>',
                        type=float,
                        help='The CCD sensor height in millimeters (mm). Example: 4.55')

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
