#!/usr/bin/python

from opendm import log
from opendm import config
from opendm import system
from opendm import io

from collections import namedtuple
from shapely.geometry import Point

import os
import utm


def get_image_type():
    '''
    Determine the image type from extension.
    :return: ext
    '''
    file, ext = os.path.splitext(os.listdir(os.getcwd())[0])
    ext = ext.replace('.', '')
    return ext


def get_projection(image_type):
    '''
    Generate EXIF data, utm zone and hemisphere.
    :param image_type:
    :return: utm_zone, hemisphere
    '''
    Image = namedtuple('UAVImage', ['image', 'point', 'altitude'])

    kwargs = {
        'image_type': image_type
    }

    system.run('exiftool -filename -gpslongitude -gpslatitude -gpsaltitude '
               '-T -n *.{image_type} > imageEXIF.txt'.format(**kwargs))

    with open('imageEXIF.txt', 'r') as f:
        lines = (l.split('\t') for l in f.readlines())
        coords = [Image(image=l[0].strip(),
                        point=Point(float(l[1]), float(l[2])),
                        altitude=l[3].strip())
                  for l in lines]

    p = Point(coords[0][1])
    u = utm.from_latlon(p.y, p.x)
    utm_zone = u[2]
    hemisphere = "north" if p.y > 0 else "south"

    log.MM_INFO('UTM - %s' % utm_zone)
    log.MM_INFO('Hemisphere - %s' % hemisphere)

    return {'utm_zone': utm_zone, 'hemisphere': hemisphere}


def create_sysutm_xml(projection):
    '''
    Generate SysUTM.xml
    :param utm_zone:
    :return: write xml
    '''
    if projection['hemisphere'] == 'north':
        proj = '+proj=utm +zone={} +ellps=WGS84 +datum=WGS84 +units=m +no_defs'.format(projection['utm_zone'])
    else:
        proj = '+proj=utm +zone={} +ellps=WGS84 +south +datum=WGS84 +units=m +no_defs'.format(projection['utm_zone'])

    with open('SysUTM.xml', 'a') as xml:
        xml.write('<SystemeCoord>\n')
        xml.write('\t<BSC>\n')
        xml.write('\t\t<TypeCoord>  eTC_Proj4   </TypeCoord>\n')
        xml.write('\t\t<AuxR>   1   </AuxR>\n')
        xml.write('\t\t<AuxR>   1   </AuxR>\n')
        xml.write('\t\t<AuxR>   1   </AuxR>\n')
        xml.write('\t\t<AuxStr> ' + proj + '  </AuxStr>\n')
        xml.write('\t</BSC>\n')
        xml.write('</SystemeCoord>\n')
    xml.close()


# RUN
if __name__ == '__main__':

    args = config.config()

    log.MM_INFO('Initializing NodeMICMAC app - %s' % system.now())
    log.MM_INFO(args)

    projectDir = io.join_paths(args.project_path, args.name)
    imageDir = io.join_paths(projectDir, 'images')

    IN_DOCKER = os.environ.get('DEBIAN_FRONTEND', False)

    if IN_DOCKER:
        mm3d = 'mm3d'
    else:
        mm3d = '/home/mm-aug2018/bin/mm3d' # for dev: locally installed micmac branch

    try:
        log.MM_INFO('Starting..')
        os.chdir(imageDir)

        image_ext = get_image_type()
        projection = get_projection(image_ext)

        log.MM_INFO(image_ext)
        log.MM_INFO(projection)

        create_sysutm_xml(projection)

        # generate xif to gps and xif to xml
        kwargs_gps2txt = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        system.run('{mm3d} XifGps2Txt .*.{ext}'.format(**kwargs_gps2txt))
        system.run('{mm3d} XifGps2Xml .*.{ext} RAWGNSS'.format(**kwargs_gps2txt))

        # generate image pairs based on match distance or auto
        kwargs_ori = {
            'distance': args.matcher_distance,
            'mm3d': mm3d
        }
        if args.matcher_distance:
            log.MM_INFO('Image pairs by distance: {}'.format(args.matcher_distance))
            system.run('{mm3d} OriConvert "#F=N X Y Z" GpsCoordinatesFromExif.txt RAWGNSS_N ChSys=DegreeWGS84@RTLFromExif.xml MTD1=1 NameCple=dronemapperPair.xml DN={distance}'.format(**kwargs_ori))
        else:
            log.MM_INFO('Image pairs by auto-distance')
            system.run('{mm3d} OriConvert "#F=N X Y Z" GpsCoordinatesFromExif.txt RAWGNSS_N ChSys=DegreeWGS84@RTLFromExif.xml MTD1=1 NameCple=dronemapperPair.xml DN='.format(**kwargs_ori))

        # tie-points (SIFT default [patented] - not for commercial use)
        kwargs_tapioca = {
            'num_cores': args.cores,
            'image_size': args.size,
            'mm3d': mm3d
        }
        system.run('{mm3d} Tapioca File dronemapperPair.xml {image_size} ByP={num_cores}'.format(**kwargs_tapioca))

        # camera calibration and initial bundle block adjustment (RadialStd is the less accurate but can be more robust vs. Fraser/others)
        kwargs_tapas = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        system.run('{mm3d} Tapas RadialStd .*.{ext} EcMax=500'.format(**kwargs_tapas))

        # transform from relative to real
        kwargs_bascule = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        system.run('{mm3d} CenterBascule .*.{ext} RadialStd RAWGNSS_N Ground_Init_RTL'.format(**kwargs_bascule))

        # bundle block adjustment with camera calibration and GPS
        kwargs_campari = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        system.run('{mm3d} Campari .*.{ext} Ground_Init_RTL Ground_RTL EmGPS=[RAWGNSS_N,5] AllFree=1'.format(**kwargs_campari))

        # change projection and system coords to UTM from relative
        kwargs_chg = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        system.run('{mm3d} ChgSysCo .*.{ext} Ground_RTL RTLFromExif.xml@SysUTM.xml Ground_UTM'.format(**kwargs_chg))

        # build DEM
        kwargs_malt = {
            'num_cores': args.cores,
            'ext': image_ext,
            'zoom': args.zoom,
            'mm3d': mm3d
        }
        system.run('{mm3d} Malt Ortho .*.{ext} Ground_UTM EZA=1 ZoomI=64 ZoomF={zoom} NbVI=2 HrOr=1 RoundResol=0 ResolOrtho=1 DefCor=0.0005 NbProc={num_cores}'.format(**kwargs_malt))

        # build ORTHO
        system.run('{mm3d} Tawny Ortho-MEC-Malt RadiomEgal=1'.format(**kwargs_malt))

        # point cloud
        system.run('{mm3d} Nuage2Ply MEC-Malt/NuageImProf_STD-MALT_Etape_8.xml Attr=Ortho-MEC-Malt/Orthophotomosaic.tif 64B=1 Out=DroneMapper.ply'.format(**kwargs_malt))

        exit(0)

    except Exception, e:
        log.MM_ERROR(e)
        exit(1)
