# -*- coding: utf-8 -*-
import pathlib
w = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(w)
import cy_kit
from cyx.common.vn_text_normalizer import VnTextNormalizer
ins = cy_kit.singleton(VnTextNormalizer)
print(ins.correct(u"UCS2 : Tôi làm viec ở ban công ngệ FPT, tôi là người viêt nam. hôm nay tôi ko thích ăn mì tôm. tôi làm đc 2 bài tập."))