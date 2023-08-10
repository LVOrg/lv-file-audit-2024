#!/bin/sh
pip install numpy --no-cache-dir
pip install scipy --no-cache-dir
pip install torch --extra-index-url https://download.pytorch.org/whl/cpu --no-cache-dir
pip install torchvision --extra-index-url https://download.pytorch.org/whl/cpu --no-cache-dir
pip install torchaudio --extra-index-url https://download.pytorch.org/whl/cpu --no-cache-dir
