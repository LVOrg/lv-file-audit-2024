import gradio as gr
import segment_word

app = gr.Interface(
  fn=segment_word.test,
  inputs=gr.inputs.Textbox(),
  outputs=gr.outputs.HTML()
)

if __name__ == "__main__":
  app.launch(

      server_name="0.0.0.0",
      server_port=8014

  )