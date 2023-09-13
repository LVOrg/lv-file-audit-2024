import pathlib
import sys
import os
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
from cyx.common.share_storage import ShareStorageService
import cyx.document_layout_analysis.system
share_storage_service = cy_kit.singleton(ShareStorageService)

cyx.document_layout_analysis.system.set_dataset_path(
    os.path.join(share_storage_service.get_root(),"dataset")
)

from vietTTS.hifigan.mel2wave import mel2wave
from vietTTS.nat.text2mel import text2mel
# from vietTTS import nat_normalize_text
import numpy as np
import gradio as gr
print(gr.__version__)
os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"
"""
gdown
git+https://github.com/NTT123/vietTTS.git@demo
gradio==3.0.2
"""
import vietTTS.nat.config
tts_path = os.path.join(cyx.document_layout_analysis.system.get_dataset_path(),"vn-tts")
vietTTS.nat.config.FLAGS.ckpt_dir =pathlib.Path(tts_path)

def text_to_speech(text):
    # prevent too long text
    if len(text) > 500:
        text = text[:500]
    # text = nat_normalize_text(text)

    lexicon_path = os.path.join(tts_path,"lexicon.txt")
    acoustic_latest_ckpt = os.path.join(tts_path,"acoustic_latest_ckpt.pickle")
    duration_latest_ckpt = os.path.join(tts_path,"duration_latest_ckpt.pickle")
    config_path = os.path.join(tts_path,"config.json")
    hk_hifi_path = os.path.join(tts_path, "hk_hifi.pickle")
    fx=f"/home/vmadmin/python/v6/file-service-02/share-storage/dataset/vn-tts/lexicon.txt"
    mel = text2mel(
        text = text,
        lexicon_fn=lexicon_path
        # acoustic_ckpt =acoustic_latest_ckpt,
        # duration_ckpt =duration_latest_ckpt

    )
    wave  = mel2wave(mel)
    # wave = mel2wave(mel, config_path, hk_hifi_path)
    return (wave * (2**15)).astype(np.int16)


def speak(text):
    y = text_to_speech(text)
    return 16_000, y


title = "vietTTS"
description = "A vietnamese text-to-speech demo."

gr.Interface(
    fn=speak,
    inputs="text",
    outputs="audio",
    title = title,
    examples = [
    "Trăm năm trong cõi người ta, chữ tài chữ mệnh khéo là ghét nhau.",
    "Đoạn trường tân thanh, thường được biết đến với cái tên đơn giản là Truyện Kiều, là một truyện thơ của đại thi hào Nguyễn Du",
    "Lục Vân Tiên quê ở huyện Đông Thành, khôi ngô tuấn tú, tài kiêm văn võ. Nghe tin triều đình mở khoa thi, Vân Tiên từ giã thầy xuống núi đua tài.",
    "Lê Quý Đôn, tên thuở nhỏ là Lê Danh Phương, là vị quan thời Lê trung hưng, cũng là nhà thơ và được mệnh danh là nhà bác học lớn của Việt Nam trong thời phong kiến",
    "Tất cả mọi người đều sinh ra có quyền bình đẳng. Tạo hóa cho họ những quyền không ai có thể xâm phạm được; trong những quyền ấy, có quyền được sống, quyền tự do và quyền mưu cầu hạnh phúc."
    ],
    description=description,
    theme="default",
    allow_screenshot=False,
    allow_flagging="never",
).launch(share=True,
    server_port=8013,
    server_name="0.0.0.0")