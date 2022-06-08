FROM ubuntu:20.04

EXPOSE 3000

# ENV TZ=US/Mountain
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt update
RUN apt install -y -qq tzdata
RUN apt install -y -qq --no-install-recommends software-properties-common
RUN add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
RUN apt-get update && apt install -y --no-install-recommends apt-utils \
x11proto-core-dev make cmake libx11-dev git ca-certificates imagemagick gcc g++ \
exiv2 libimage-exiftool-perl build-essential gpg-agent \
mesa-common-dev libgl1-mesa-dev libglapi-mesa libglu1-mesa opencl-headers \
proj-bin gdal-bin graphicsmagick php figlet vim curl libboost-all-dev less

RUN apt update -y && apt install -y -qq --no-install-recommends openssl python3-pip python3-setuptools
RUN pip3 install -U pip
RUN pip3 install -U shyaml
#RUN pip3 install --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pip

RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org setuptools
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org appsettings
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org Shapely
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org utm
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyproj #==2.2.0
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org scikit-image

RUN curl --silent --location https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs python3-gdal libboost-dev libboost-program-options-dev git cmake
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
RUN mkdir -p tmp
RUN mkdir -p /code

RUN git clone https://github.com/rumenmitrev/micmac

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

#RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR "/var/www"

ENTRYPOINT ["/usr/bin/node", "/var/www/index.js"]
