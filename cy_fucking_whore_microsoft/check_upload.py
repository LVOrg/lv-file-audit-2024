import requests
import os
token = "EwCIA8l6BAAUAOyDv0l6PcCVu89kmzvqZmkWABkAAb3RoHtCzsFR0Zj5thf4CGZKgUWG6iKvFbiEckIxyCxuHUY7pZ7pIT6hf6caqEJHz6XOP1GQWGUdc1bmoigiIDdY5xCg6Gzmw6Z5n7dGwQvSDqWfoWRq/dZT4XV0PTs3cMdmpwozoDGjPjEkCI6PiVag4ovSYbI7lfz9GND0VcJ0WqDxUbC1LcbH6bEtaS5hnmAQ0v1Zbj92viFHaiyhhW/+iuGqY5qtbIojf9yOUk1dmVrJcxxxFPEjsv1/ftUdnDa+VD8xQ4XX8vNejVOLIEBO0TOBVL0iFKRIG2mXa3PeTEbcuxE83I2JfoiU9MwoCssGsnk1v7IfRnqH4IaXRYsDZgAACIQKfJwnT1HbWALQjRY1/dwunPBuDNN50mFQ/Y3m5MGrJQv+TZ03anWW9FbnaZK8Y4D9kdKPGaBOV1z4LbwnnSiuj+9u0ajdNQyiDqtYCBKvovb0WhGSLdiNJH1oMdRtjigQsiPZiQCyp7HuUT20Gk3iE0tCcHzpgGl9v/DbW0XcIow8FGNY/5VUGi1Bu2UOQl61o0RUC53AJmptu2HtJH2qyLIgBA1FsrmZJTct+ciObsRGNMPoShFaalaJ1eyxvbEcmi95krWmZg3XWTp7kvi5/Ozt7M8vgwy0aYKFpsyR9xGVA8ERjAHWvnyqFeRTJ6Lvj/wTyK9KLyER0/+weRFsys6ERNtpzb1SGwNlzLb+xuChuVjVEkYKwRfp+dky+6brfVTo6oJcDo7ANSUS/wJbLVKXUPDhnmdp5WtA6fuU1Z3HDHm3zVJQxjKfUwLjrFNYMOOhcv7PaIekhyHepRPE3wjTOZBkszNOlnfOLMnCJnWQqgHd4+EZ6FHPjLx4pD8pG0X25WyJyd45NqzWD/iedi3f9aRGDpvUN3S95qp/q3edvUN4biIoddqNUGrWwCElO8P1Bps/tcoBAsOvWkFeOAfJQ6toNE4vZBl0Zi7bP6VUxUnzlI3hMVhUCvMDSN8wXzbJ9ez+lmg54Rj53xXGMTSlVs6CibmzViQ0lPZLnnIx+PFRc1cfUDOuuWZVkJtf12xTDQ7Y4CHblRvJ7fGqUshJrmtuH5/zf+BY366ufwKRLMS9KQoX2V62ibAYUzSTvSwXBK3bbksO1TJBKtdK31ypP16bkVsutZk4TTGpoimbAg=="
from cy_fucking_whore_microsoft.fwcking_ms.caller import call_ms_func
def upload_file_chunked(file_path, drive_item_id, chunk_size=32768):
    file_name = os.path.basename(file_path)
    res_upload_session = call_ms_func(
        method="post",
        token=token,
        body= {
              "item": {
                "@microsoft.graph.conflictBehavior": "rename"
              },
              "deferCommit": False
            },
        api_url= f"/me/drive/items/root:/{drive_item_id}/{file_name}:/createUploadSession",
        request_content_type="application/json",
        return_type=dict
    )
    # Get file size
    file_size = os.path.getsize(file_path)

    # Calculate number of chunks
    chunk_number = file_size // chunk_size
    chunk_leftover = file_size - chunk_size * chunk_number

    # Set headers
    headers = {
        'Content-Type': 'application/octet-stream',
        'Authorization': token,
        'X-Upload-Start': '0',
        'X-Upload-Length': str(file_size)
    }

    # Initialize upload session
    upload_url = res_upload_session['uploadUrl']

    # Upload chunks
    with open(file_path, 'rb') as f:
        start_index = 0
        for chunk_index in range(chunk_number + 1):
            if chunk_index == chunk_number:
                chunk_size = chunk_leftover

            # Read chunk data
            chunk_data = f.read(chunk_size)

            # Update headers
            headers = {
                'Content-Type': 'application/octet-stream',
                'Content-Length': str(chunk_size),
                'Content-Range': f'bytes {start_index}-{start_index+chunk_size-1}/{file_size}'
            }

            # Send chunk
            res = requests.put(upload_url, headers=headers, data=chunk_data,verify=False)

            # Update start index
            start_index += chunk_size

    # Finalize upload
    # res = requests.put(upload_url, headers={
    #     'Content-Type': 'application/octet-stream',
    #     'Content-Range': f'bytes {start_index}-{start_index + chunk_size - 1}/{file_size}'
    # })
    # r= res.json()
    # print(r)

upload_file_chunked(
    file_path=f"/home/vmadmin/python/cy-py/cy_fucking_whore_microsoft/check_upload.py",
    drive_item_id="test moi"
)