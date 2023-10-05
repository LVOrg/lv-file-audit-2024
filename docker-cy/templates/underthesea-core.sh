#!/bin/sh
apt install wget -y
apt install curl build-essential gcc make -y
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
apt install cargo -y
pip3 install maturin patchelf

mkdir /tmp-build
cd /tmp-build
wget https://files.pythonhosted.org/packages/b3/7f/8d136185263619e25473af7584bb224918a3546975afeb375b87b3bcae20/underthesea_core-1.0.4.tar.gz
tar -xvf underthesea_core-1.0.4.tar.gz
cd underthesea_core-1.0.4
maturin build --target aarch64
python3 -m pip install target/wheels/*.whl
python3 -c "import underthesea_core;print(underthesea_core.__file__);"