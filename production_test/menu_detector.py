"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License

https://github.com/clovaai/donut
"""
import pathlib
import sys
import os
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
import gradio
import cyx.document_layout_analysis.system
cyx.document_layout_analysis.system.set_offline_dataset(False)
from cyx.common.share_storage import ShareStorageService

share_storage_service = cy_kit.singleton(ShareStorageService)
cyx.document_layout_analysis.system.set_dataset_path(
    os.path.abspath(
        os.path.join(share_storage_service.get_root(),"dataset")
    )
)

import re
import gradio as gr

import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel

processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-rvlcdip")
model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-rvlcdip")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


def process_document(image):
    # prepare encoder inputs
    pixel_values = processor(image, return_tensors="pt").pixel_values

    # prepare decoder inputs
    task_prompt = "<s_rvlcdip>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids

    # generate answer
    outputs = model.generate(
        pixel_values.to(device),
        decoder_input_ids=decoder_input_ids.to(device),
        max_length=model.decoder.config.max_position_embeddings,
        early_stopping=True,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        num_beams=1,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
        return_dict_in_generate=True,
    )

    # postprocess
    sequence = processor.batch_decode(outputs.sequences)[0]
    sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token

    return processor.token2json(sequence)


description = "Gradio Demo for Donut, an instance of `VisionEncoderDecoderModel` fine-tuned on RVL-CDIP (document image classification). To use it, simply upload your image and click 'submit', or click one of the examples to load them. Read more at the links below."
article = "<p style='text-align: center'><a href='https://arxiv.org/abs/2111.15664' target='_blank'>Donut: OCR-free Document Understanding Transformer</a> | <a href='https://github.com/clovaai/donut' target='_blank'>Github Repo</a></p>"

demo = gr.Interface(
    fn=process_document,
    inputs="image",
    outputs="json",
    title="Demo: Donut 🍩 for Document Image Classification",
    description=description,
    article=article,
    enable_queue=True,
    examples=[],
    cache_examples=False)
demo.launch(server_name="0.0.0.0",server_port=8013)
