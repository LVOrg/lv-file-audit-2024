
import sys
import pathlib
working_path = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_path)
from cyx.common import config
import  doctr
print(doctr.__version__)
import os
# os.system('pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.9/index.html')

# work around: https://discuss.huggingface.co/t/how-to-install-a-specific-version-of-gradio-in-spaces/13552
# os.system("pip uninstall -y gradio")
# os.system("pip install gradio==3.4.1")
from cyx import graphic_utils
import  cy_kit
from cyx.doctr_service import DoctrService
doc_tr_service = cy_kit.singleton(DoctrService)
model= doc_tr_service.model
# graphic_utils.set_temp_dir(f"{working_path}/temp-data")
# graphic_utils.set_dataset_cache_dir(f"{working_path}/dataset")
# os.environ["DOCTR_CACHE_DIR"]=f"{working_path}/dataset/doctr"
os.environ["GRADIO_SERVER_NAME"]="0.0.0.0"
from os import getcwd, path, environ
import deepdoctection as dd
from deepdoctection.dataflow.serialize import DataFromList

import gradio as gr

sub_app_dir = pathlib.Path(__file__).parent.name
_DD_ONE = f"{sub_app_dir}/conf_dd_one.yaml"
_DETECTIONS = ["table", "ocr"]
lay_out_model_file="model_final_inf_only.pt"
#lay_out_model_file="model_0829999_layout_inf_only.pt"
model = dd.ModelProfile(
            name=f"layout/{lay_out_model_file}",
            description="Detectron2 layout detection model trained on private datasets",
            config="dd/d2/layout/CASCADE_RCNN_R_50_FPN_GN.yaml",
            size=[1024*1024*10],
            tp_model=True, #False original
            # hf_repo_id=environ.get("HF_REPO"),
            # hf_model_name="model_final_inf_only.pt",
            hf_config_file=["Base-RCNN-FPN.yaml", "CASCADE_RCNN_R_50_FPN_GN.yaml"],
            categories={"1": dd.LayoutType.text,
                        "2": dd.LayoutType.title,
                        "3": dd.LayoutType.list,
                        "4": dd.LayoutType.table,
                        "5": dd.LayoutType.figure},
        )
dd.ModelCatalog.register(f"layout/{lay_out_model_file}",model)

# Set up of the configuration and logging. Models are globally defined, so that they are not re-loaded once the input
# updates
cfg = dd.set_config_by_yaml(
    os.path.join( working_path,_DD_ONE)
)
cfg.freeze(freezed=False)
cfg.DEVICE = "cpu"
cfg.freeze()

# layout detector
layout_config_path = dd.ModelCatalog.get_full_path_configs(cfg.CONFIG.D2LAYOUT)
layout_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(cfg.WEIGHTS.D2LAYOUT)
categories_layout = dd.ModelCatalog.get_profile(cfg.WEIGHTS.D2LAYOUT).categories
assert categories_layout is not None
assert layout_weights_path is not None
d_layout = dd.D2FrcnnDetector(
    layout_config_path,
    layout_weights_path,
    categories_layout,
    device=cfg.DEVICE
)

# cell detector
cell_config_path = dd.ModelCatalog.get_full_path_configs(cfg.CONFIG.D2CELL)
cell_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(cfg.WEIGHTS.D2CELL)
categories_cell = dd.ModelCatalog.get_profile(cfg.WEIGHTS.D2CELL).categories
assert categories_cell is not None
d_cell = dd.D2FrcnnDetector(
    cell_config_path,
    cell_weights_path,
    categories_cell,
    device=cfg.DEVICE
)

# row/column detector
item_config_path = dd.ModelCatalog.get_full_path_configs(cfg.CONFIG.D2ITEM)
item_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(cfg.WEIGHTS.D2ITEM)
categories_item = dd.ModelCatalog.get_profile(cfg.WEIGHTS.D2ITEM).categories
assert categories_item is not None
d_item = dd.D2FrcnnDetector(
    item_config_path,
    item_weights_path,
    categories_item,
    device=cfg.DEVICE
)

# word detector
det = dd.DoctrTextlineDetector()

# text recognizer
rec = dd.DoctrTextRecognizer(

)


def build_gradio_analyzer(table, table_ref, ocr):
    """Building the Detectron2/DocTr analyzer based on the given config"""

    cfg.freeze(freezed=False)
    cfg.TAB = table
    cfg.TAB_REF = table_ref
    cfg.OCR = ocr
    cfg.freeze()

    pipe_component_list = []
    layout = dd.ImageLayoutService(d_layout, to_image=True, crop_image=True)
    pipe_component_list.append(layout)

    if cfg.TAB:

        detect_result_generator = dd.DetectResultGenerator(categories_cell)
        cell = dd.SubImageLayoutService(d_cell, dd.LayoutType.table, {1: 6}, detect_result_generator)
        pipe_component_list.append(cell)

        detect_result_generator = dd.DetectResultGenerator(categories_item)
        item = dd.SubImageLayoutService(d_item, dd.LayoutType.table, {1: 7, 2: 8}, detect_result_generator)
        pipe_component_list.append(item)

        table_segmentation = dd.TableSegmentationService(
            cfg.SEGMENTATION.ASSIGNMENT_RULE,
            cfg.SEGMENTATION.IOU_THRESHOLD_ROWS
            if cfg.SEGMENTATION.ASSIGNMENT_RULE in ["iou"]
            else cfg.SEGMENTATION.IOA_THRESHOLD_ROWS,
            cfg.SEGMENTATION.IOU_THRESHOLD_COLS
            if cfg.SEGMENTATION.ASSIGNMENT_RULE in ["iou"]
            else cfg.SEGMENTATION.IOA_THRESHOLD_COLS,
            cfg.SEGMENTATION.FULL_TABLE_TILING,
            cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_ROWS,
            cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_COLS,
        )
        pipe_component_list.append(table_segmentation)

        if cfg.TAB_REF:
            table_segmentation_refinement = dd.TableSegmentationRefinementService()
            pipe_component_list.append(table_segmentation_refinement)

    if cfg.OCR:
        d_layout_text = dd.ImageLayoutService(det, to_image=True, crop_image=True)
        pipe_component_list.append(d_layout_text)

        d_text = dd.TextExtractionService(rec,
                                          extract_from_roi="WORD")
        pipe_component_list.append(d_text)

        match = dd.MatchingService(
            parent_categories=cfg.WORD_MATCHING.PARENTAL_CATEGORIES,
            child_categories=dd.LayoutType.word,
            matching_rule=cfg.WORD_MATCHING.RULE,
            threshold=cfg.WORD_MATCHING.IOU_THRESHOLD
            if cfg.WORD_MATCHING.RULE in ["iou"]
            else cfg.WORD_MATCHING.IOA_THRESHOLD,
        )
        pipe_component_list.append(match)
        order = dd.TextOrderService(
            text_container=dd.LayoutType.word,
            floating_text_block_names=[dd.LayoutType.title, dd.LayoutType.text, dd.LayoutType.list],
            text_block_names=[
                dd.LayoutType.title,
                dd.LayoutType.text,
                dd.LayoutType.list,
                dd.LayoutType.cell,
                dd.CellType.header,
                dd.CellType.body,
            ],
        )
        pipe_component_list.append(order)

    pipe = dd.DoctectionPipe(pipeline_component_list=pipe_component_list)

    return pipe


def prepare_output(dp, add_table, add_ocr):
    out = dp.as_dict()
    out.pop("_image")

    layout_items = dp.layouts
    if add_ocr:
        layout_items.sort(key=lambda x: x.reading_order)
    layout_items_str = ""
    for item in layout_items:
        layout_items_str += f"\n {item.category_name}: {item.text}"
    if add_table:
        html_list = [table.html for table in dp.tables]
        if html_list:
            html = ("\n").join(html_list)
        else:
            html = None
    else:
        html = None

    return dp.viz(show_table_structure=True), layout_items_str, html, out


def analyze_image(img, pdf, attributes):

    # creating an image object and passing to the analyzer by using dataflows
    add_table = _DETECTIONS[0] in attributes
    add_ocr = _DETECTIONS[1] in attributes

    analyzer = build_gradio_analyzer(add_table, add_table, add_ocr)

    if img is not None:
        image = dd.Image(file_name="input.png", location="")
        image.image = img[:, :, ::-1]

        df = DataFromList(lst=[image])
        df = analyzer.analyze(dataset_dataflow=df)
    elif pdf:
        df = analyzer.analyze(path=pdf.name, max_datapoints=3)
    else:
        raise ValueError

    df.reset_state()
    df_iter = iter(df)

    dp = next(df_iter)

    return prepare_output(dp, add_table, add_ocr)

print("OK")
demo = gr.Blocks(css="scrollbar.css")
app_path = pathlib.Path(__file__).parent.__str__()
with demo:
    with gr.Box():
        gr.Markdown("<h1><center>deepdoctection - A Document AI Package</center></h1>")
        gr.Markdown("<strong>deep</strong>doctection is a Python library that orchestrates document extraction"
                    " and document layout analysis tasks using deep learning models. It does not implement models"
                    " but enables you to build pipelines using highly acknowledged libraries for object detection,"
                    " OCR and selected NLP tasks and provides an integrated frameworks for fine-tuning, evaluating"
                    " and running models.\n This pipeline consists of a stack of models powered by <strong>Detectron2"
                    "</strong> for layout analysis and table recognition and <strong>DocTr</strong> for OCR.")
    with gr.Box():
        gr.Markdown("<h2><center>Upload a document and choose setting</center></h2>")
        with gr.Row():
            with gr.Column():
                with gr.Tab("Image upload"):
                    with gr.Column():
                        inputs = gr.Image(type='numpy', label="Original Image")
                with gr.Tab("PDF upload (only first image will be processed) *"):
                    with gr.Column():
                        inputs_pdf = gr.File(label="PDF")
                    gr.Markdown("<sup>* If an image is cached in tab, remove it first</sup>")
            # with gr.Column():
            #     gr.Examples(
            #         examples=[path.join(app_path, "sample_1.jpg"), path.join(app_path, "sample_2.png")],
            #         inputs = inputs)
            #     gr.Examples(examples=[path.join(app_path, "sample_3.pdf")], inputs = inputs_pdf)

        with gr.Row():
            tok_input = gr.CheckboxGroup(
                _DETECTIONS, value=_DETECTIONS, label="Additional extractions", interactive=True)
        with gr.Row():
            btn = gr.Button("Run model", variant="primary")

    with gr.Box():
        gr.Markdown("<h2><center>Outputs</center></h2>")
        with gr.Row():
            with gr.Column():
                with gr.Box():
                    gr.Markdown("<center><strong>Contiguous text</strong></center>")
                    image_text = gr.Textbox()
                with gr.Box():
                    gr.Markdown("<center><strong>Table</strong></center>")
                    html = gr.HTML()
                with gr.Box():
                    gr.Markdown("<center><strong>JSON</strong></center>")
                    json = gr.JSON()
            with gr.Column():
                with gr.Box():
                    gr.Markdown("<center><strong>Layout detection</strong></center>")
                    image_output = gr.Image(type="numpy", label="Output Image")

    btn.click(fn=analyze_image, inputs=[inputs, inputs_pdf, tok_input], outputs=[image_output, image_text, html, json])

demo.launch(
    share=True,
    server_port=int(config.host_port)
)