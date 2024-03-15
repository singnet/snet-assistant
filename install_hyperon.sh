#!/bin/sh
  set -e
  hdir="$1"
#install hyperon
    apt-get update &&  apt-get install sudo
    sudo DEBIAN_FRONTEND=noninteractive TZ=UTC apt-get install -y git python3 python3-pip wget curl gcc cmake unzip \
    && sudo python3 -m pip install --upgrade pip && \
    sudo  rm -rf /var/lib/apt/lists/*
    cd ${HOME}

    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > /tmp/rustup.sh
    sudo sh /tmp/rustup.sh -y && rm /tmp/rustup.sh
    export PATH=${PATH}:${HOME}/.cargo/bin
    #source "${HOME}/.cargo/env"
    cargo install cbindgen

    sudo python3 -m pip install conan==1.59.0
    export PATH=${PATH}:${HOME}/.local/bin

    conan profile new --detect default
    if [ ${hdir} != "${HOME}" ]
    then
        mkdir -p ${hdir}
        cd ${hdir}
    fi

    if test -e ${hdir}/hyperon-experimental; then
      echo "hyperon exsists"
    else
       git clone https://github.com/trueagi-io/hyperon-experimental.git
    fi
    cd ${hdir}/hyperon-experimental

    rm -rf build
    mkdir build
    cd ${hdir}/hyperon-experimental/build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    make
    find . -type f ! -name '*.so' -delete
    cd ${hdir}/hyperon-experimental
    sudo python3 -m pip install -e ./python[dev]
    sudo echo "export PYTHONPATH=$PYTHONPATH:${hdir}/hyperon-experimental/build/python" >> ${HOME}/.bashrc
    # pythonpath hyperon
    export PYTHONPATH=${PYTHONPATH}:${hdir}/hyperon-experimental/build/python
