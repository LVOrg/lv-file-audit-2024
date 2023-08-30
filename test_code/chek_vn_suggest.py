import datetime
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
from cy_vn_suggestion import suggest
from cy_vn_suggestion.analyzers import analyzer_words


import gradio as gr

def do_suggest(text,separate_sticky_words,correct_spell):
    t= datetime.datetime.now()
    ret = suggest(text,separate_sticky_words=separate_sticky_words,correct_spell=correct_spell)
    n = datetime.datetime.now()-t
    return f'"{ret}" in {n.total_seconds()} second(s)'
  # return suggest(text,skip_if_in_langs=["en_US"])


# Create a Gradio interface
demo = gr.Interface(fn=do_suggest, inputs=[
    "text",
    gr.Checkbox(label="Separate sticky words"),
    gr.Checkbox(label="Correct spell"),
],outputs="text")

# Launch the Gradio interface
demo.launch(
    server_name="0.0.0.0",
    server_port=8014

)