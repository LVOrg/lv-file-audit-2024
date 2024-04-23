import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())
import gradio as gr

import json
def process_text(text):

    data = json.loads(text)
    token= data.get("token")
    app_name = data.get("app_name")
    client_id= data.get('client_id')
    secret_key= data.get('secret_key')
    file_path = data.get('file_path')
    google_path = data.get('google_path')
    memcache_server= data.get('memcache_server')
    import cy_file_cryptor.context
    import cy_file_cryptor.wrappers
    memcache_server="172.16.13.72:11213"
    cy_file_cryptor.context.set_server_cache(memcache_server)
    g_path=f"google-drive://{google_path}"
    with open(
            g_path,
            "wb",
            token=token,
            client_id=client_id,
            client_secret=secret_key) as fs:
        ret = fs.write(file_path)
        return ret





    import cy_file_cryptor.wrappers
    print(text)
    return text
iface = gr.Interface(
    fn=process_text,
    inputs=["textbox"],
    outputs=["textbox"],
    title="Text Processor",
    description="Enter text and see it processed!",

)

iface.launch(
    server_name="0.0.0.0",  # Here's where you specify server name
    server_port=1115
)

