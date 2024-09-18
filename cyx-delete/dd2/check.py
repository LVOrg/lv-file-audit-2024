import os
from IPython.core.display import HTML
os.environ["DEEPDOCTECTION_CACHE"]="/mnt/files/dataset/dd2"
from matplotlib import pyplot as plt
file_test=f"/mnt/files/lacvietdemo/2024/01/12/jpg/aad020e0-3b99-4236-9c4d-0a2830a088ad/â.jpg"
# test_file=f"/mnt/files/lacvietdemo/2024/01/07/pdf/541d7b98-5014-4242-a570-bd8383834eaa/số 02 - ngày 03.01.2024.pdf"
file_test=f"/mnt/files/lacvietdemo/2024/01/10/png/659446ab-f316-42fa-9324-e4e1a25ab371/2024-01-09_16-27-56.png"
from cyx.dd2.utils import predict_image
predict_image(file_test,"/mnt/files/tmp")
# from deepdoctection.extern.base import TextRecognizer
# analyzer = init_dd("/mnt/files/dataset/dd3")  # instantiate the built-in analyzer similar to the Hugging Face space demo
# from deepdoctection.pipe.text import TextExtractionService
# # tr=TextRecognizer()
# # TextExtractionService
# df = analyzer.analyze(path = test_file)  # setting up pipeline

#
#
# image = page.viz()
# from PIL import Image
# import  numpy  as np
# image_pil = Image.fromarray(image.astype(np.uint8))
# image_pil.save(f"/mnt/files/cacher/test-pdf.png")
# plt.figure(figsize = (25,17))
# plt.axis('off')
# plt.imshow(image)