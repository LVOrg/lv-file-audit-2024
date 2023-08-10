import  torch
import torchvision
import platform
if platform.machine()=="aarch64":
    if torch.__version__ == '2.0.0':
        print(f"torch version 2.0.0")
    else:
        raise Exception(
            f"incorrect torch version. Torch version is {torch.__version__}  with platform {platform.machine()}")
else:
    if torch.__version__ == '2.0.0+cpu':
        print(f"torch version 2.0.0+cpu")
    else:
        raise Exception(f"incorrect torch version. Torch version is {torch.__version__}  with platform {platform.machine()}")
if platform.machine()=="aarch64":
    if torchvision.__version__ == "0.15.0":
        print(f"torchvision version 0.15.0")
    else:
        raise Exception(
            f"incorrect torchvision version. torchvision version is {torchvision.__version__} with platform {platform.machine()}")
else:
    if torchvision.__version__=="0.15.0+cpu":
        print(f"torchvision version 0.15.0+cpu")
    else:
        raise Exception(f"incorrect torchvision version. torchvision version is {torchvision.__version__} with platform {platform.machine()}")