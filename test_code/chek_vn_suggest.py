import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
from check_vn_suggets import suggest, analyzer_words


import gradio as gr

def greet(text):
    fx = analyzer_words(text,seperate_sticky_word=False)[0]
    if fx is None:
        return text
    _, begin, vowel, end, _, _ =fx

    return begin+","+vowel+"."+(end) or ""
def do_suggest(text):
    return suggest(text,)
  # return suggest(text,skip_if_in_langs=["en_US"])


# Create a Gradio interface
demo = gr.Interface(fn=do_suggest, inputs="text", outputs="text")

# Launch the Gradio interface
demo.launch(
    server_name="0.0.0.0",
    server_port=8014

)