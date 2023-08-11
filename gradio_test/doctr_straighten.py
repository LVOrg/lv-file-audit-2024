import sys
import pathlib
wrk=pathlib.Path(__file__).parent.parent.__str__()
app_dir =pathlib.Path(__file__).parent.__str__()
print(wrk)
sys.path.append(wrk)
from seg import U2NETP
from GeoTr import GeoTr
from IllTr import IllTr
from inference_ill import rec_ill

import torch
import torch.nn as nn
import torch.nn.functional as F
import skimage.io as io
import numpy as np
import cv2
import glob
import os
from PIL import Image
import argparse
import warnings

warnings.filterwarnings('ignore')

import gradio as gr

example_img_list =[] # ['51_1 copy.png', '48_2 copy.png', '25.jpg']


def reload_model(model, path=""):
    if not bool(path):
        return model
    else:
        model_dict = model.state_dict()
        pretrained_dict = torch.load(path, map_location='cpu')
        # print(len(pretrained_dict.keys()))
        pretrained_dict = {k[7:]: v for k, v in pretrained_dict.items() if k[7:] in model_dict}
        # print(len(pretrained_dict.keys()))
        model_dict.update(pretrained_dict)
        model.load_state_dict(model_dict)

        return model


def reload_segmodel(model, path=""):
    if not bool(path):
        return model
    else:
        model_dict = model.state_dict()
        pretrained_dict = torch.load(path, map_location='cpu')
        # print(len(pretrained_dict.keys()))
        pretrained_dict = {k[6:]: v for k, v in pretrained_dict.items() if k[6:] in model_dict}
        # print(len(pretrained_dict.keys()))
        model_dict.update(pretrained_dict)
        model.load_state_dict(model_dict)

        return model


class GeoTr_Seg(nn.Module):
    def __init__(self):
        super(GeoTr_Seg, self).__init__()
        self.msk = U2NETP(3, 1)
        self.GeoTr = GeoTr(num_attn_layers=6)

    def forward(self, x):
        msk, _1, _2, _3, _4, _5, _6 = self.msk(x)
        msk = (msk > 0.5).float()
        x = msk * x

        bm = self.GeoTr(x)
        bm = (2 * (bm / 286.8) - 1) * 0.99

        return bm


# Initialize models
GeoTr_Seg_model = GeoTr_Seg()
# IllTr_model = IllTr()

# Load models only once
reload_segmodel(GeoTr_Seg_model.msk, f'{app_dir}/model_pretrained/seg.pth')
reload_model(GeoTr_Seg_model.GeoTr, f'{app_dir}/model_pretrained/geotr.pth')
# reload_model(IllTr_model, './model_pretrained/illtr.pth')

# Compile models (assuming PyTorch 2.0)
GeoTr_Seg_model = torch.compile(GeoTr_Seg_model)


# IllTr_model = torch.compile(IllTr_model)

def process_image(input_image):
    GeoTr_Seg_model.eval()
    # IllTr_model.eval()

    im_ori = np.array(input_image)[:, :, :3] / 255.
    h, w, _ = im_ori.shape
    im = cv2.resize(im_ori, (288, 288))
    im = im.transpose(2, 0, 1)
    im = torch.from_numpy(im).float().unsqueeze(0)

    with torch.no_grad():
        bm = GeoTr_Seg_model(im)
        bm = bm.cpu()
        bm0 = cv2.resize(bm[0, 0].numpy(), (w, h))
        bm1 = cv2.resize(bm[0, 1].numpy(), (w, h))
        bm0 = cv2.blur(bm0, (3, 3))
        bm1 = cv2.blur(bm1, (3, 3))
        lbl = torch.from_numpy(np.stack([bm0, bm1], axis=2)).unsqueeze(0)

        out = F.grid_sample(torch.from_numpy(im_ori).permute(2, 0, 1).unsqueeze(0).float(), lbl, align_corners=True)
        img_geo = ((out[0] * 255).permute(1, 2, 0).numpy()).astype(np.uint8)

        ill_rec = False

        if ill_rec:
            img_ill = rec_ill(IllTr_model, img_geo)
            return Image.fromarray(img_ill)
        else:
            return Image.fromarray(img_geo)


# Define Gradio interface
input_image = gr.inputs.Image()
output_image = gr.outputs.Image(type='pil')

iface = gr.Interface(fn=process_image, inputs=input_image, outputs=output_image, title="DocTr",
                     examples=example_img_list)
iface.launch(

    server_name="0.0.0.0",
    server_port=8012
)