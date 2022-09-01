FROM ubuntu:22.04

EXPOSE 3000

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update
RUN apt-get install -y -qq --no-install-recommends software-properties-common build-essential cmake git \
    exiv2 libimage-exiftool-perl proj-bin gdal-bin figlet imagemagick pdal libpdal-dev \
    libboost-all-dev libtbb-dev libssl-dev libcurl4-openssl-dev pkg-config libpth-dev \
    curl libx11-dev python3-pip python3-setuptools python3-shapely

RUN pip3 install -U shyaml
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org appsettings
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org utm
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyproj #==2.2.0
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org scikit-image

RUN curl --silent --location https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g nodemon

# Build Entwine
WORKDIR "/staging"
RUN git clone --depth 1 https://github.com/OpenDroneMap/entwine /staging/entwine
RUN cd /staging/entwine && \
    mkdir build && \
    cd build && \
    cmake \
        -DCMAKE_INSTALL_PREFIX=/usr \
	-DWITH_TESTS=OFF \
	-DCMAKE_BUILD_TYPE=Release \
	../ && \
	make -j$(cat /proc/cpuinfo | grep processor | wc -l) && make install


RUN mkdir /var/www
WORKDIR "/var/www"
COPY . /var/www

RUN npm install
RUN mkdir -p tmp /code
RUN mkdir -p /code

# Build MicMac
RUN git clone --depth 1  https://github.com/OpenDroneMap/micmac
RUN cd micmac && \ 
    rm -rf build && mkdir build && cd build && \
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
      mkdir -p /code/micmac && \
      cd .. && \
      cp -Rdp bin binaire-aux lib include /code/micmac

ENV PATH "$PATH:/code/micmac/bin"

RUN ln -s "$(which python3)" /usr/bin/python
ENV python "$(which python3)"
RUN figlet -f slant NodeMICMAC

RUN mkdir -p /code/opendm
COPY dm/opendm /code/opendm
COPY dm/odm_options.json /code
COPY dm/settings.yaml /code
COPY dm/VERSION /code
COPY dm/run.sh /code
COPY dm/run.py /code

RUN apt clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /staging /var/www/micmac

WORKDIR "/var/www"

ENTRYPOINT ["/usr/bin/node", "/var/www/index.js"]
