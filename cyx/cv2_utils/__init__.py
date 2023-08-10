import cv2
import numpy
import numpy as np


def show(img_obj, title: str = "unknown",max_width=1920):
    def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(image, dim, interpolation=inter)
    s_img = ResizeWithAspectRatio(img_obj,width=max_width)
    cv2.imshow(title, s_img)
    cv2.waitKey(0)


def load_from_file(img_src: str, is_gray_scale=False) -> numpy.ndarray:
    if is_gray_scale:
        img = cv2.imread(img_src, 0)
        return img
    else:
        img = cv2.imread(img_src)
        return img

def extract_chanels(img_obj:numpy.ndarray)->numpy.ndarray:
    (B, G, R) = cv2.split(img_obj)
    return B,G,R
def extract_red_chanel(img_obj:numpy.ndarray)->numpy.ndarray:
    (B, G, R) = cv2.split(img_obj)
    return R


def balance_contrast(img_obj:numpy.ndarray):
    alpha = 1.95  # Contrast control (1.0-3.0)
    beta = 0  # Brightness control (0-100)

    ret = cv2.convertScaleAbs(img_obj, alpha=alpha, beta=beta)
    return ret
def adjust_gamma(img_obj:numpy.ndarray, gamma=1.2):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(img_obj, table)

def automatic_brightness_and_contrast(image:numpy.ndarray, clip_hist_percent=1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum / 100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size - 1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return auto_result, alpha, beta