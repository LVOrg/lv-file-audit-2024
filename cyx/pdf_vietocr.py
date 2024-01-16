from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image
file_test=f"/mnt/files/developer/2023/09/26/pdf/bc61ab45-5308-43a7-bbd7-7630f5c1e0d5/pdf_images/page_0000.png"
def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--img', required=True, help='foo help')
    # parser.add_argument('--config', required=True, help='foo help')

    # args = parser.parse_args()
    config = Cfg.load_config_from_name('vgg_transformer')
    config['device']='cpu'
    detector = Predictor(config)

    img = Image.open(file_test)
    s = detector.predict(img)

    print(s)

if __name__ == '__main__':
    main()