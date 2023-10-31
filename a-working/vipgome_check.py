from viphoneme import vi2IPA


import gradio as gr
import viphoneme

# Define a function to convert Vietnamese text to IPA transcriptions
def convert_to_ipa(text):
    phoneme = vi2IPA(text)
    return phoneme

# Create a Gradio interface
interface = gr.Interface(fn=convert_to_ipa, inputs="text", outputs="text")

# Launch the Gradio interface
interface.launch(server_name="0.0.0.0", server_port=8017)