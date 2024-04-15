FROM higherground2/satellite_monitor_base:2.0.0

# inherited the base UHD and GR already from above

RUN parallel_builds="$(expr $(nproc --all) / 2 + 1)"

RUN apt-get update && \
    apt-get install -y \
      flex \
      build-essential \
      cmake \
      gir1.2-gtk-3.0 \
      bison \
      libarmadillo-dev \
      libblas-dev \
      libboost-chrono-dev \
      libboost-date-time-dev \
      libboost-dev \
      libboost-serialization-dev \
      libboost-system-dev \
      libboost-thread-dev \
      libgflags-dev \
      libgnutls28-dev \
      libgoogle-glog-dev \
      libgtest-dev \
      libiio-dev \
      liblapack-dev \
      libmatio-dev \
      libsndfile1-dev \
      liborc-0.4-dev \
      libpcap-dev \
      libprotobuf-dev \
      libpugixml-dev \
      libuhd-dev \
      libxml2-dev \
      nano \
      protobuf-compiler \
      python3-mako \
      gdb \
      && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PYTHONPATH /usr/lib/python3/dist-packages

WORKDIR /opt/gnss-sdr
COPY . /opt/gnss-sdr/
