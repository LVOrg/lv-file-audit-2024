import gradio as gr
import subprocess

def ocr(image_file):
  """Performs OCR on an image file using Tesseract."""

  # Get the path to the Tesseract executable.
  tesseract_path = subprocess.check_output(['which', 'tesseract']).decode().strip()

  # Create a command line to run Tesseract.
  command = [tesseract_path, image_file, '-', '-l', 'vie+eng+ch_sim+chi_tra']

  # Run the Tesseract command and capture the output.
  output = subprocess.check_output(command, universal_newlines=True)

  # Return the OCR output.
  return output

# Create a Gradio interface.
interface = gr.Interface(fn=ocr, inputs="file", outputs="text")

# Launch the Gradio interface
interface.launch(
  server_name="0.0.0.0",
  server_port=8020

)