#!/bin/bash

# This file executes the post-processing steps for a task after a dataset 
# has been processed by OpenDroneMap. It generates secondary outputs.
# 
# As a general rule, post-processing commands should never fail the task 
#(for example, if a point cloud could not be generated, the PotreeConverter 
# step will fail, but the script should still continue processing the rest and
# return a 0 code). The idea is to post-process as much as possible, knowing 
# that some parts might fail and that partial results should be returned in such cases.

if [ -z "$1" ]; then
	echo "Usage: $0 <projectPath>"
	exit 0
fi

# Switch to project path folder (data/<uuid>/)
script_path=$(realpath $(dirname "$0"))
cd "$script_path/../$1"
echo "Postprocessing: $(pwd)"

# Generate colored shaded relief for DTM/DSM files if available
dem_products=()
if [ -e "odm_dem/dsm.tif" ]; then dem_products=(${dem_products[@]} dsm); fi
if [ -e "odm_dem/dtm.tif" ]; then dem_products=(${dem_products[@]} dtm); fi

if hash gdaldem 2>/dev/null; then
	for dem_product in ${dem_products[@]}; do
		dem_path="odm_dem/""$dem_product"".tif"

		gdaldem color-relief $dem_path $script_path/color_relief.txt "odm_dem/""$dem_product""_colored.tif" -alpha -co ALPHA=YES
		gdaldem hillshade $dem_path "odm_dem/""$dem_product""_hillshade.tif" -z 1.0 -s 1.0 -az 315.0 -alt 45.0
		python "$script_path/hsv_merge.py" "odm_dem/""$dem_product""_colored.tif" "odm_dem/""$dem_product""_hillshade.tif" "odm_dem/""$dem_product""_colored_hillshade.tif"
	done
else
	echo "gdaldem is not installed, will skip colored hillshade generation"
fi

# Generate Tiles
g2t_options="--processes $(nproc) -z 12-21 -n -w none"
orthophoto_path="odm_orthophoto/odm_orthophoto.tif"

if [ -e "$orthophoto_path" ]; then
	python "$script_path/gdal2tiles.py" $g2t_options $orthophoto_path orthophoto_tiles
else
	echo "No orthophoto found at $orthophoto_path: will skip tiling"
fi

for dem_product in ${dem_products[@]}; do
	colored_dem_path="odm_dem/""$dem_product""_colored_hillshade.tif"
	if [ -e "$colored_dem_path" ]; then
		python "$script_path/gdal2tiles.py" $g2t_options $colored_dem_path "$dem_product""_tiles"
	else
		echo "No $dem_product found at $colored_dem_path: will skip tiling"
	fi
done

# Generate MBTiles
if hash gdal_translate 2>/dev/null; then
	orthophoto_path="odm_orthophoto/odm_orthophoto.tif"
	orthophoto_mbtiles_path="odm_orthophoto/odm_orthophoto.mbtiles"

	if [ -e "$orthophoto_path" ]; then
		gdal_translate $orthophoto_path $orthophoto_mbtiles_path -of MBTILES
		gdaladdo -r bilinear $orthophoto_mbtiles_path 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384
	else
		echo "No orthophoto found at $orthophoto_path: will skip MBTiles generation"
	fi
else
	echo "gdal_translate is not installed, will skip MBTiles generation"
fi

#Generate laz point cloud
pointcloud_input="odm_georeferencing/odm_georeferenced_model.ply"
pointcloud_output="odm_georeferencing/odm_georeferenced_model.laz"
pdal translate -i "$pointcloud_input"  "$pointcloud_output"

# Generate point cloud (if entwine is available)
pointcloud_input_path=""
for path in "odm_georeferencing/odm_georeferenced_model.laz" \
            "odm_georeferencing/odm_georeferenced_model.las" \
	    "odm_georeferencing/odm_georeferenced_model.ply" \
            "odm_filterpoints/point_cloud.ply"; do
    if [ -e $path ]; then
        echo "Found point cloud: $path"
        pointcloud_input_path=$path
        break
    fi
done

# Never generate point cloud tiles with split-merge workflows
if [ -e "submodels" ] && [ -e "entwine_pointcloud" ]; then
    pointcloud_input_path=""
    echo "Split-merge dataset with point cloud detected. No need to regenerate point cloud tiles."
fi

if [ ! -z "$pointcloud_input_path" ]; then
    # Copy the failsafe PLY point cloud to odm_georeferencing 
    # if necessary, otherwise it will not get zipped
    if [ "$pointcloud_input_path" == "odm_filterpoints/point_cloud.ply" ] || [ "$pointcloud_input_path" == "opensfm/depthmaps/merged.ply" ] || [ "$pointcloud_input_path" == "pmvs/recon0/models/option-0000.ply" ]; then
        echo "Copying $pointcloud_input_path to odm_georeferencing/odm_georeferenced_model.ply, even though it's not georeferenced..."
        cp $pointcloud_input_path "odm_georeferencing/odm_georeferenced_model.ply"
    fi
    
    if hash entwine 2>/dev/null; then
        # Optionally cleanup previous results (from a restart)
        if [ -e "entwine_pointcloud" ]; then
            rm -fr "entwine_pointcloud"
        fi
	
        #extract srs and add as option to entwine
	
	srs=`grep -oPm1 "(?<=<AuxStr>)[^<]+" < images/SysUTM.xml`
	
        entwine build --srs "$srs" --threads $(nproc) --tmp "entwine_pointcloud-tmp" -i "$pointcloud_input_path" -o entwine_pointcloud
        
        # Cleanup
        if [ -e "entwine_pointcloud-tmp" ]; then
            rm -fr "entwine_pointcloud-tmp"
        fi
    else
        echo "Entwine is not installed, checking if PotreeConverter is available instead..."
        if hash PotreeConverter 2>/dev/null; then
            PotreeConverter "$pointcloud_input_path" -o potree_pointcloud --overwrite -a RGB CLASSIFICATION
        else
            echo "PotreeConverter is also not installed, will skip generation of Potree point cloud"
        fi
    fi
else
    echo "Point cloud tiles will not be generated"
fi


echo "Postprocessing: done (•̀ᴗ•́)و!"
exit 0
