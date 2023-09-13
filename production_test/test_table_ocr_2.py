import sys
import pathlib

working_path = pathlib.Path(__file__).parent.parent.__str__()

import os
import huggingface_hub.utils._http
sys.path.append(working_path)
os.environ["TRANSFORMERS_OFFLINE"] = "true"
os.environ["HF_HUB_OFFLINE"]="true"
os.environ["XDG_CACHE_HOME"]=f"{working_path}/dataset"
os.environ["DOCTR_CACHE_DIR"]=f"{working_path}/dataset/doctr"
from typing import List

from deepdoctection.utils import LayoutType, get_configs_dir_path, CellType
from deepdoctection.utils.metacfg import AttrDict
from deepdoctection.pipe import (
    PipelineComponent,
    ImageLayoutService,
    SubImageLayoutService,
    PubtablesSegmentationService,
    TextExtractionService,
    TextOrderService,
    MatchingService,
    DoctectionPipe,
    DetectResultGenerator,
)

from deepdoctection.extern import ModelCatalog, ModelDownloadManager, D2FrcnnDetector, HFDetrDerivedDetector, TesseractOcrDetector, ModelProfile
# from deepdoctection.utils import set_logger_dir
from deepdoctection.utils import PadTransform
import deepdoctection as dd

def build_detr_analyzer(cfg: AttrDict):
    pipe_component_list: List[PipelineComponent] = []

    layout_config_path = ModelCatalog.get_full_path_configs(cfg.CONFIG.LAYOUT)
    layout_weights_path = ModelDownloadManager.maybe_download_weights_and_configs(cfg.WEIGHTS.LAYOUT)
    profile_layout = ModelCatalog.get_profile(cfg.WEIGHTS.LAYOUT)
    categories_layout = profile_layout.categories
    assert categories_layout is not None
    assert layout_weights_path is not None
    d_layout = D2FrcnnDetector(layout_config_path, layout_weights_path, categories_layout, device=cfg.DEVICE)
    layout = ImageLayoutService(d_layout, to_image=True, crop_image=True)
    pipe_component_list.append(layout)

    structure_config_path = ModelCatalog.get_full_path_configs(cfg.CONFIG.STRUCTURE)
    structure_weights_path = ModelDownloadManager.maybe_download_weights_and_configs(cfg.WEIGHTS.STRUCTURE)
    structure_preprocessor_config = ModelCatalog.get_full_path_preprocessor_configs(cfg.CONFIG.STRUCTURE)
    profile = ModelCatalog.get_profile(cfg.WEIGHTS.STRUCTURE)
    categories_structure = profile.categories
    hf_table_structure = HFDetrDerivedDetector(structure_config_path,
                                            structure_weights_path,
                                            structure_preprocessor_config,
                                            categories_structure,
                                            filter_categories=[LayoutType.table])
    padder = PadTransform(top=cfg.PAD.TOP,right=cfg.PAD.RIGHT,bottom=cfg.PAD.BOTTOM,left=cfg.PAD.LEFT)
    detect_result_generator = DetectResultGenerator(categories_structure, exclude_category_ids=["1","3","4","5","6"])
    structure = SubImageLayoutService(hf_table_structure,
                                      LayoutType.table,
                                      {1: 6, 2:7, 3:8, 4:9, 5:10, 6:11},
                                      detect_result_generator,
                                      padder)
    pipe_component_list.append(structure)
    pubtables = PubtablesSegmentationService(cfg.SEGMENTATION.ASSIGNMENT_RULE,
                                             cfg.SEGMENTATION.THRESHOLD_ROWS,
                                             cfg.SEGMENTATION.THRESHOLD_COLS,
                                             cfg.SEGMENTATION.FULL_TABLE_TILING,
                                             cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_ROWS,
                                             cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_COLS,
                                             cfg.SEGMENTATION.CELL_CATEGORY_ID,
                                             stretch_rule=cfg.SEGMENTATION.STRETCH_RULE)
    pipe_component_list.append(pubtables)

    tess_ocr_config_path = get_configs_dir_path() / cfg.CONFIG.TESS_OCR
    d_tess_ocr = TesseractOcrDetector(
    tess_ocr_config_path, config_overwrite=[f"LANGUAGES={cfg.LANG}"] if cfg.LANG is not None else None
)
    text = TextExtractionService(d_tess_ocr)
    pipe_component_list.append(text)

    match = MatchingService(
        parent_categories=cfg.WORD_MATCHING.PARENTAL_CATEGORIES,
        child_categories=LayoutType.word,
        matching_rule=cfg.WORD_MATCHING.RULE,
        threshold=cfg.WORD_MATCHING.THRESHOLD,
        max_parent_only=cfg.WORD_MATCHING.MAX_PARENT_ONLY
    )
    pipe_component_list.append(match)

    order = TextOrderService(
        text_container=LayoutType.word,
        floating_text_block_names=[LayoutType.title, LayoutType.text, LayoutType.list],
        text_block_names=[
            LayoutType.title,
            LayoutType.text,
            LayoutType.list,
            LayoutType.cell,
            CellType.spanning,
            CellType.projected_row_header,
            CellType.column_header,
            CellType.row_header,
        ],
    )
    pipe_component_list.append(order)

    pipe = DoctectionPipe(pipeline_component_list=pipe_component_list)
    return pipe

def set_cfg():
    config_dict = {"CONFIG" : {"LAYOUT": "dd/d2/layout/CASCADE_RCNN_R_50_FPN_GN.yaml",
                               "STRUCTURE": "microsoft/table-transformer-structure-recognition/pytorch_model.bin",
                               "TESS_OCR": "dd/conf_tesseract.yaml"
                               },
                   "PAD" : {"TOP": 60, "RIGHT": 60, "BOTTOM": 60, "LEFT": 60},
                   "WEIGHTS": {"LAYOUT" : "layout/d2_model_0829999_layout_inf_only.pt",
                               "STRUCTURE": "microsoft/table-transformer-structure-recognition/pytorch_model.bin"
                               },
                   "SEGMENTATION": {"ASSIGNMENT_RULE": "ioa",
                   "THRESHOLD_ROWS": 0.4,
                   "THRESHOLD_COLS": 0.4,
                   "FULL_TABLE_TILING": True,
    "REMOVE_IOU_THRESHOLD_ROWS": 0.9,
    "REMOVE_IOU_THRESHOLD_COLS": 0.9,
    "CELL_CATEGORY_ID": 12,
    "STRETCH_RULE": "equal",
    },
    "LANG": "eng",
    "WORD_MATCHING": {"PARENTAL_CATEGORIES": ["text", "title", "cell","list","column_header","projected_row_header","spanning"],
                      "RULE": "ioa",
                      "THRESHOLD": 0.6,
                      "MAX_PARENT_ONLY": True,
                      },
    "DEVICE": None,
                   }
    cfg = AttrDict()
    cfg.from_dict(config_dict)
    return cfg

import cy_kit
from cyx.images import ImageServices
pdf_service = cy_kit.singleton(ImageServices)

if __name__=="__main__":
    f_logs=f"/home/vmadmin/python/v6/file-service-02/logs"
    # set_logger_dir(f_logs)   # set logger file to get insights from warnings
    cfg = set_cfg()
    analyzer = build_detr_analyzer(cfg)

    path = f"/home/vmadmin/python/v6/file-service-02/temp-data/Screenshot_3.png"
    pdf_file = pdf_service.convert_to_pdf(path)
    df = analyzer.analyze(path=pdf_file, output="image")
    df.reset_state()

    for idx, dp in enumerate(df):
        page = dd.Page.from_image(dp,text_container=dd.LayoutType.word,top_level_text_block_names=[layout for layout in dd.LayoutType if layout!=dd.LayoutType.cell])
        page.viz(interactive=True)