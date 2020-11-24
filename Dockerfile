FROM ubuntu:18.04
MAINTAINER Jon-Pierre Stoermer <jp@dronemapper.com>

EXPOSE 3000

ENV TZ=US/Mountain
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils \
x11proto-core-dev make cmake libx11-dev git ca-certificates imagemagick gcc g++ \
exiv2 libimage-exiftool-perl libgeo-proj4-perl \
mesa-common-dev libgl1-mesa-dev libglapi-mesa libglu1-mesa opencl-headers \
proj-bin gdal-bin python-gdal graphicsmagick php figlet vim curl libboost-all-dev less

RUN apt-get update -y && apt-get install -y --no-install-recommends openssl python-pip
RUN pip install --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pip

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org setuptools
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org appsettings
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org Shapely
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org utm
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyproj==2.2.0

RUN curl --silent --location https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get install -y nodejs python-gdal libboost-dev libboost-program-options-dev git cmake
RUN npm install -g nodemon

# Build LASzip and PotreeConverter
WORKDIR "/staging"
RUN git clone https://github.com/pierotofy/LAStools /staging/LAStools && \
	cd LAStools/LASzip && \
	mkdir build && \
	cd build && \
	cmake -DCMAKE_BUILD_TYPE=Release .. && \
	make

RUN git clone https://github.com/pierotofy/PotreeConverter /staging/PotreeConverter
RUN cd /staging/PotreeConverter && \
	mkdir build && \
	cd build && \
	cmake -DCMAKE_BUILD_TYPE=Release -DLASZIP_INCLUDE_DIRS=/staging/LAStools/LASzip/dll -DLASZIP_LIBRARY=/staging/LAStools/LASzip/build/src/liblaszip.a .. && \
	make && \
	make install

RUN mkdir /var/www

WORKDIR "/var/www"

COPY . /var/www

RUN npm install
RUN mkdir tmp
RUN mkdir /code

RUN git clone https://github.com/dronemapper-io/micmac.git

RUN cd micmac && rm -rf build && mkdir build && cd build && \
    cmake \
    	-DBUILD_POISSON=0 \
    	-DBUILD_RNX2RTKP=0 \
    	-DWITH_OPENCL=OFF  \
    	-DWITH_OPEN_MP=OFF  \
    	-DWITH_ETALONPOLY=OFF \
    	-DWERROR=OFF \
    	../ && \
      make clean && \
      make -j$(cat /proc/cpuinfo | grep processor | wc -l) && make install && \
      mkdir /code/micmac && \
      cd .. && \
      cp -Rdp bin binaire-aux lib include /code/micmac

ENV PATH "$PATH:/code/micmac/bin"

RUN figlet -f slant DRONEMAPPER

RUN mkdir /code/opendm
COPY dm/opendm /code/opendm
COPY dm/odm_options.json /code
COPY dm/settings.yaml /code
COPY dm/VERSION /code
COPY dm/run.sh /code
COPY dm/run.py /code

#RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR "/var/www"

ENTRYPOINT ["/usr/bin/nodejs", "/var/www/index.js"]
