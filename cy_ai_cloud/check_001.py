import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import pathlib
import textwrap
from  cy_ai_cloud.load_api_key import api_keys

from IPython.display import display
from IPython.display import Markdown
import  google.generativeai as genai
genai.configure(api_key=api_keys.GEMINI_KEY)
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# response = model.generate_content("Could you tell me about Donal Trump")
# print(response.text)
import gradio as gr
import mistune
import numpy
from PIL import Image
from tika import parser
def get_text_from_file(file_path:str):
    headers = {

    }
    ret = parser.from_file(
        filename=file_path,
        serverEndpoint=f'http://172.16.7.99:31807/tika',
        requestOptions={'headers': headers, 'timeout': 30000}
    )
    ret_content = ret['content'] or ""
    ret_content=ret_content.lstrip('\n').rstrip('\n').rstrip(' ').lstrip(' ')
    return ret_content

def echo(image:numpy.ndarray,file_path:str, text):
  """Simple function that returns the input text."""
  if image is not None:
      model = genai.GenerativeModel("gemini-pro-vision")
      img = Image.fromarray(image)
      response = model.generate_content([
                                           text,
                                            img], stream=True)
      response.resolve()

      html_text = mistune.html(response.text)
      return html_text
  else:
      ref_content =""
      if file_path is not None:
          ref_content = get_text_from_file(file_path)
      model = genai.GenerativeModel("gemini-pro")
      response = model.generate_content('"'+ref_content+'"'+ "\n"+ text, stream=True)
      response.resolve()

      html_text = mistune.html(response.text)
      return html_text

# Define the Gradio interface
interface = gr.Interface(
    fn=echo,
    inputs=["image","file","textarea"],  # Use "textbox" for input text
    outputs="html",  # Use "textbox" for output text
    title="Echo Text",
    description="This app echoes the text you enter.",
)

# Launch the interface
interface.launch(server_name="0.0.0.0",server_port=8017)