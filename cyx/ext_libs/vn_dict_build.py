# from cyx.ext_libs.vn_predicts import get_config, __config__
import collections
import os.path
import pathlib

import cyx.ext_libs.vn_predicts
from cyx.ext_libs.vn_validator import is_vn_word
from cyx.tools.progress_bar import printProgressBar
cyx.ext_libs.vn_predicts.get_config()
g2 = cyx.ext_libs.vn_predicts.__config__.tones
gram_1 = collections.OrderedDict()
gram_1 = g2
total = len(g2.keys())
index = 0
for k,v in g2.items():
    gram_1[k]=v
    index += 1
    printProgressBar(
        iteration=index,
        length=50,
        prefix=f"Validate {index}",
        total= total,

    )


import numpy as np
location = pathlib.Path(__file__).parent.__str__()
np.save(os.path.join(
    location,"vn_predictor_accents.npy"
),gram_1)