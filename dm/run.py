#!/usr/bin/python

from opendm import log
from opendm import config
from opendm import system
from opendm import io
from opendm.progress import progressbc

from collections import namedtuple
from shapely.geometry import Point

import os
import utm
import glob
import subprocess


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
    Image = namedtuple('Image', ['image', 'point', 'altitude'])

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
    :return: write xml, return proj
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
    return proj


def gdal_translate(proj_str, src, dst):
    '''
    Execute gdal_translate
    :param proj_str: projection string
    :param src: input tif
    :param dst: output tif
    :return:
    '''
    kwargs = {
        'tiled': '-co TILED=yes',
        'compress': 'LZW',
        'predictor': '-co PREDICTOR=2',
        'proj': proj_str,
        'bigtiff': 'YES',
        'src': src,
        'dst': dst,
        'max_memory': 2048,
        'threads': args.max_concurrency
    }

    system.run('gdal_translate '
        '{tiled} '
        '-co BIGTIFF={bigtiff} '
        '-co COMPRESS={compress} '
        '{predictor} '
        '-co BLOCKXSIZE=512 '
        '-co BLOCKYSIZE=512 '
        '-co NUM_THREADS={threads} '
        '-a_srs \"{proj}\" '
        '--config GDAL_CACHEMAX {max_memory} '
        '{src} {dst}'.format(**kwargs))


def get_last_etape(file_str):
    '''
    Get last etape or step file based on args.zoom
    :return: filename
    '''
    if glob.glob(file_str):
        etape_files = glob.glob(file_str)
        etape_files.sort(key=lambda f: int(filter(str.isdigit, f)))
        return etape_files[-1]


def create_lcd(image_dir, image_ext, ccd_width, ccd_height):
    '''
    Create MicMac-LocalChantierDescripteur.xml
    :param image_dir: string path
    :param image_ext: string
    :param ccd_width: float
    :param ccd_height: float
    :return:
    '''
    image_wildcard = '*.{}'.format(image_ext)
    image_files = glob.glob(io.join_paths(image_dir, image_wildcard))
    image_files.sort(key=lambda f: int(filter(str.isdigit, f)))
    camera_model = subprocess.check_output(['exiftool', '-Model', '-T', image_files[0]])
    with open(io.join_paths(image_dir, 'MicMac-LocalChantierDescripteur.xml'), 'wb') as f:
        f.write('<Global>\n')
        f.write('\t<ChantierDescripteur>\n')
        f.write('\t\t<LocCamDataBase>\n')
        f.write('\t\t\t<CameraEntry>\n')
        name = '\t\t\t\t<Name> {} </Name>\n'.format(camera_model)
        f.write(name)
        ccd_size = '\t\t\t\t<SzCaptMm> {} {} </SzCaptMm>\n'.format(ccd_width, ccd_height)
        f.write(ccd_size)
        short_name = '\t\t\t\t<ShortName> {} </ShortName>\n'.format(camera_model)
        f.write(short_name)
        f.write('\t\t\t</CameraEntry>\n')
        f.write('\t\t</LocCamDataBase>\n')
        f.write('\t</ChantierDescripteur>\n')
        f.write('</Global>\n')


def convert_gcp(gcp_dir, utm_zone, hemisphere):
    '''
    Convert MicMac GCP TXT files to MicMac GCP XML format
    :param image_dir: path
    :return:

    Expects files to be named, DroneMapperGCP_2D.txt and DroneMapperGCP_3D.txt or ODM format: gcp_list.txt

    DroneMapperGCP_2D.txt format (single space delimiter):
    GCP IMAGENAME PIXELX PIXELY

    DroneMapperGCP_3D.txt format (single space delimiter):
    GCP UTMX UTMY Z PRECISION X/Y PRECISIONZ
    '''
    from opendm import gcp

    log.MM_INFO('Converting GCP.')

    gcp_files = os.listdir(gcp_dir)
    for file in gcp_files:
        if '3d' in file.lower():
            gcp_3d_file = file
        if '2d' in file.lower():
            gcp_2d_file = file
        if 'gcp_list' in file.lower():
            gcp_file = gcp.GCPFile(os.path.join(gcp_dir, file))
            gcp_file.make_micmac_copy(gcp_dir, utm_zone='WGS84 UTM {}{}'.format(utm_zone, hemisphere))
            gcp_2d_file = '2d_gcp.txt'
            gcp_3d_file = '3d_gcp.txt'

    # MicMac GCP 2D - target locations in images
    # GCPNAME IMAGE PIXELX PIXELY
    MM2D = namedtuple('MM2D', ['gcp', 'img', 'px', 'py'])

    with open(io.join_paths(gcp_dir, gcp_2d_file), 'r') as f2d_txt:
        lines = (l.split() for l in f2d_txt.readlines())
        images = [MM2D(gcp=l[0].strip(),
                        img=l[1].strip(),
                        px=l[2].strip(),
                        py=l[3].strip())
                  for l in lines]

    with open(io.join_paths(image_dir, 'images.xml'), 'wb') as images_xml:
        images_xml.write('<?xml version="1.0"?>\n')
        images_xml.write('<SetOfMesureAppuisFlottants>\n')
        for image in images:
            log.MM_INFO('GCP in image {}'.format(image))
            gcp = image[0]
            img = image[1]
            px = image[2]
            py = image[3]
            images_xml.write('\t<MesureAppuiFlottant1Im>\n')
            name_im = '\t\t<NameIm> {} </NameIm>\n'.format(img)
            images_xml.write(name_im)
            images_xml.write('\t\t<OneMesureAF1I>\n')
            name_pt = '\t\t\t<NamePt> {} </NamePt>\n'.format(gcp)
            images_xml.write(name_pt)
            pt_im = '\t\t\t<PtIm> {} {} </PtIm>\n'.format(px, py)
            images_xml.write(pt_im)
            images_xml.write('\t\t</OneMesureAF1I>\n')
            images_xml.write('\t</MesureAppuiFlottant1Im>\n')
        images_xml.write('</SetOfMesureAppuisFlottants>\n')

    # MicMac GCP 3D - real world target position on ground (UTM)
    # GCPNAME UTMX UTMY Z PRECISIONXY PRECISIONZ
    MM3D = namedtuple('MM3D', ['gcp', 'x', 'y', 'z', 'pxy', 'pz'])

    with open(io.join_paths(gcp_dir, gcp_3d_file), 'r') as f3d_txt:
        lines = (l.split() for l in f3d_txt.readlines())
        coords = [MM3D(gcp=l[0].strip(),
                        x=l[1].strip(),
                        y=l[2].strip(),
                        z=l[3].strip(),
                        pxy=l[4].strip(),
                        pz=l[5].strip())
                  for l in lines]

    with open(io.join_paths(image_dir, 'ground.xml'), 'wb') as ground_xml:
        ground_xml.write('<?xml version="1.0"?>\n')
        ground_xml.write('<Global>\n')
        ground_xml.write('\t<DicoAppuisFlottant>\n')
        for c in coords:
            log.MM_INFO('GCP on ground {}'.format(c))
            gcp = c[0]
            x = c[1]
            y = c[2]
            z = c[3]
            pxy = c[4]
            pz = c[5]
            ground_xml.write('\t\t<OneAppuisDAF>\n')
            pt = '\t\t\t<Pt> {} {} {} </Pt>\n'.format(x, y, z)
            ground_xml.write(pt)
            name_pt = '\t\t\t<NamePt> {} </NamePt>\n'.format(gcp)
            ground_xml.write(name_pt)
            precision = '\t\t\t<Incertitude> {} {} {} </Incertitude>\n'.format(pxy, pxy, pz)
            ground_xml.write(precision)
            ground_xml.write('\t\t</OneAppuisDAF>\n')
        ground_xml.write('\t</DicoAppuisFlottant>\n')
        ground_xml.write('</Global>\n')


def remove_ortho_tiles():
    '''
    Remove every other orthomosaic tile. Optimizes color balance and radiometric routine,
    speeds up ortho generation using Porto/Tawny module.
    '''
    ort_files = 'Ortho-MEC-Malt/Ort_*.tif'
    if glob.glob(ort_files):
        tiles = glob.glob(ort_files)
        tiles.sort(key=lambda f: int(filter(str.isdigit, f)))
        for tile in tiles[::2]:
            os.remove(tile)
            log.MM_INFO('Removing ortho tile {}'.format(tile))


# RUN
if __name__ == '__main__':

    args = config.config()

    log.MM_INFO('Initializing NodeMICMAC app - %s' % system.now())
    log.MM_INFO(args)

    progressbc.set_project_name(args.name)

    project_dir = io.join_paths(args.project_path, args.name)
    image_dir = io.join_paths(project_dir, 'images')
    gcp_dir = io.join_paths(project_dir, 'gcp')

    IN_DOCKER = os.environ.get('DEBIAN_FRONTEND', False)

    if IN_DOCKER:
        mm3d = 'mm3d'
    else:
        mm3d = '/home/drnmppr-micmac/bin/mm3d' # for dev: locally installed micmac branch

    try:
        log.MM_INFO('Starting..')
        os.chdir(image_dir)

        # create output directories (match ODM conventions for backward compatibility, even though this is MicMac)
        odm_dirs = ['odm_orthophoto', 'odm_dem', 'dsm_tiles',
                    'orthophoto_tiles', 'potree_pointcloud', 'odm_georeferencing']
        for odm_dir in odm_dirs:
            system.mkdir_p(io.join_paths(project_dir, odm_dir))

        image_ext = get_image_type()
        projection = get_projection(image_ext)

        # parse ccd_width and ccd_height options and generate MicMac-LocalChantierDescripteur.xml
        if args.ccd_width and args.ccd_height:
            log.MM_INFO('Force CCD sensor size {} x {} mm'.format(args.ccd_width, args.ccd_height))
            create_lcd(image_dir, image_ext, args.ccd_width, args.ccd_height)

        log.MM_INFO(image_ext)
        log.MM_INFO(projection)

        proj_str = create_sysutm_xml(projection)

        # generate xif to gps and xif to xml
        kwargs_gps2txt = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        system.run('{mm3d} XifGps2Txt .*.{ext}'.format(**kwargs_gps2txt))
        system.run('{mm3d} XifGps2Xml .*.{ext} RAWGNSS'.format(**kwargs_gps2txt))

        progressbc.send_update(2)

        # generate image pairs based on match distance or auto
        kwargs_ori = {
            'distance': args.matcher_distance,
            'mm3d': mm3d
        }
        if args.matcher_distance:
            log.MM_INFO('Image pairs by distance: {}'.format(args.matcher_distance))
            system.run('{mm3d} OriConvert "#F=N X Y Z" GpsCoordinatesFromExif.txt RAWGNSS_N '
                'ChSys=DegreeWGS84@RTLFromExif.xml MTD1=1 NameCple=dronemapperPair.xml '
                'DN={distance}'.format(**kwargs_ori))
        else:
            log.MM_INFO('Image pairs by auto-distance')
            system.run('{mm3d} OriConvert "#F=N X Y Z" GpsCoordinatesFromExif.txt RAWGNSS_N '
                'ChSys=DegreeWGS84@RTLFromExif.xml MTD1=1 NameCple=dronemapperPair.xml DN='.format(**kwargs_ori))

        progressbc.send_update(5)

        # tie-points SIFT w/ ANN
        # comment by @pierotofy - The SIFT patent has expired, so this can probably be used just fine in all settings.
        # https://piero.dev/2019/04/the-sift-patent-has-expired/
        mulscale_size = int(args.resize_to * 2)
        kwargs_tapioca = {
            'num_cores': args.max_concurrency,
            'image_size': args.resize_to,
            'mulscale_size': mulscale_size,
            'ext': image_ext,
            'mm3d': mm3d
        }
        if args.multi_scale:
            system.run('{mm3d} Tapioca MulScaleFile dronemapperPair.xml .*.{ext} '
                '{image_size} {mulscale_size} ByP={num_cores}'.format(**kwargs_tapioca))
        else:
            system.run('{mm3d} Tapioca File dronemapperPair.xml {image_size} ByP={num_cores}'.format(**kwargs_tapioca))

        progressbc.send_update(30)

        # camera calibration and initial bundle block adjustment (RadialStd is less accurate but can
        # be more robust vs. Fraser/others)
        kwargs_tapas = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        system.run('{mm3d} Tapas RadialStd .*.{ext} EcMax=500'.format(**kwargs_tapas))

        progressbc.send_update(40)

        # transform from relative to real
        kwargs_bascule = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        if args.gcp:
            convert_gcp(gcp_dir, projection['utm_zone'], projection['hemisphere'][0].upper())
            system.run('{mm3d} GCPBascule .*.{ext} RadialStd Ground_Init_RTL ground.xml images.xml ShowD=1'.format(**kwargs_bascule))
        else:
            system.run('{mm3d} CenterBascule .*.{ext} RadialStd RAWGNSS_N Ground_Init_RTL'.format(**kwargs_bascule))

        progressbc.send_update(50)

        # bundle block adjustment with camera calibration and GPS
        kwargs_campari = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        if args.gcp:
            system.run('{mm3d} Campari .*.{ext} Ground_Init_RTL Ground_RTL '
                'GCP=[ground.xml,0.005,images.xml,0.01] NbIterEnd=6 AllFree=1 DetGCP=1'.format(**kwargs_campari))
        else:
            system.run('{mm3d} Campari .*.{ext} Ground_Init_RTL Ground_RTL '
                'EmGPS=[RAWGNSS_N,5] AllFree=0'.format(**kwargs_campari))

        progressbc.send_update(60)

        # change projection and system coords to UTM from relative for GPS only
        kwargs_chg = {
            'ext': image_ext,
            'mm3d': mm3d
        }
        if args.gcp:
            io.copy('Ori-Ground_RTL', 'Ori-Ground_UTM')
            system.run('{mm3d} GCPCtrl .*.{ext} Ground_UTM ground.xml images.xml'.format(**kwargs_chg))
        else:
            system.run('{mm3d} ChgSysCo .*.{ext} Ground_RTL RTLFromExif.xml@SysUTM.xml Ground_UTM'.format(**kwargs_chg))

        progressbc.send_update(65)

        # camera cloud
        if args.camera_cloud:
            kwargs_camera_cloud = {
                'ext': image_ext,
                'mm3d': mm3d,
                'ply': '../odm_georeferencing/camera_cloud_utm.ply' # use ../ here for work-around to AperiCloud bug
            }
            system.run('{mm3d} AperiCloud .*.{ext} Ground_UTM Out={ply} Bin=0'.format(**kwargs_camera_cloud))

        progressbc.send_update(70)

        # image footprints
        if args.image_footprint:
            kwargs_image_footprint = {
                'ext': image_ext,
                'mm3d': mm3d,
                'ply': io.join_paths(project_dir, 'odm_georeferencing/image_footprint_wgs84.ply')
            }
            system.run('{mm3d} DroneFootPrint .*.{ext} Ground_UTM Out={ply} CodeProj=4326 Resol=[2000,0]'.format(**kwargs_image_footprint))

        progressbc.send_update(75)

        # build DEM
        kwargs_malt = {
            'num_cores': args.max_concurrency,
            'ext': image_ext,
            'zoom': args.zoom,
            'mm3d': mm3d
        }
        system.run('{mm3d} Malt Ortho .*.{ext} Ground_UTM EZA=1 ZoomI=64 ZoomF={zoom} NbVI=2 HrOr=1 '
            'RoundResol=0 ResolOrtho=1 DefCor=0.0005 NbProc={num_cores}'.format(**kwargs_malt))

        progressbc.send_update(80)

        # build ORTHO
        if args.remove_ortho_tiles:
            remove_ortho_tiles()

        if IN_DOCKER:
            porto_src = '/code/micmac/include/XML_MicMac/Param-Tawny.xml'
        else:
            porto_src = '/home/drnmppr-micmac/include/XML_MicMac/Param-Tawny.xml' # for dev: locally installed micmac branch

        porto_dst = 'Ortho-MEC-Malt/Param-Tawny.xml'
        io.copy(porto_src, porto_dst)
        system.run('{mm3d} Porto Ortho-MEC-Malt/Param-Tawny.xml'.format(**kwargs_malt))

        progressbc.send_update(90)

        # build PLY
        kwargs_nuage = {
            'mm3d': mm3d,
            'ply': io.join_paths(project_dir, 'odm_georeferencing/odm_georeferenced_model.ply'),
            'nuage': get_last_etape('MEC-Malt/NuageImProf_STD-MALT_Etape_*.xml')
        }
        system.run('{mm3d} Nuage2Ply {nuage} Attr=Ortho-MEC-Malt/Orthophotomosaic.tif '
            '64B=1 Out={ply}'.format(**kwargs_nuage))

        progressbc.send_update(95)

        # apply srs and geo projection to ORTHO (UTM) and write to odm_orthophoto/
        gdal_translate(proj_str,
                       io.join_paths(image_dir, 'Ortho-MEC-Malt/Orthophotomosaic.tif'),
                       io.join_paths(project_dir, 'odm_orthophoto/odm_orthophoto.tif'))

        # apply srs and geo projection to DEM (UTM) and write to odm_dem/
        gdal_translate(proj_str,
                       io.join_paths(image_dir, get_last_etape('MEC-Malt/Z_Num*_DeZoom{}*.tif'.format(args.zoom))),
                       io.join_paths(project_dir, 'odm_dem/dsm.tif'))
        
        progressbc.send_update(100)

        exit(0)

    except Exception, e:
        log.MM_ERROR(e)
        exit(1)
