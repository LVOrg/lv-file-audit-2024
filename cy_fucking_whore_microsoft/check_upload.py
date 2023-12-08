import requests
import os
token = "EwCQA8l6BAAUAOyDv0l6PcCVu89kmzvqZmkWABkAAXqyWKBK2C/wNCcGHc/nWO7qzrRsbEqt/E9Uls4Gg5xhzPyiEXhehg6/DkPgXXo2dz8RxC3PZSJOB8M3VpgyVei3dahK/3+A4YjL9ONHAG6AwNcaqA8FgF4+wiBQszqb+rf9P6kDKR9zg5Shvx6IqGJ9iIVGZ7ltJGzCzRnJCeCz23geOToKfDL9D8tYTQ5XPLwTunsk8l5ga7cDfalcN3Gu56JCJorF1zpcnSp0uP3GCgwNlIwx2BKVdAEz7ngciTI4BebcxNSGFYxGA+vnL/siaS7iXWTKajMqY+ck1qcULMNc0G52ybfTF8MTA4onId5FUgGcbl61qmDe0kJC+KQDZgAACAyqb7ou043fYAJ5lmHfbRXTB/b5706uPS76np9PlmsQWdYKRHjdJ1aw36hI5YEsNaJfn/eXXi9CHQgBzporOVHBrssBLLDRHDL8lkjkSRI/zzeTVZVcI7pv3Vjbytx7attgGbPWRR8TANR0yN6eyniEA0dBhIKHGbzOlPxOZ5FnFSMIbghcnU91sW6+hOL7qqxEq7Di2WaSgyjbMtxZTIdBr3bbM11Ckg/e/jFoRnmNRkgjX/vkTI4V1pWGKmnWp0Yg7+llZCmgntkgI9jZx/pqFMH8kV20AmCU0PhtuVTFuudF8/pGT6dA2h18Imenyp9CcCSDXhhg5TUeEdnIUIapzxd5gbb9OGLJywYcgR7oqoxLVjhQW+VvV+lyBGyLLoTRo1cDHo3q+Y0EFyzBO23yC0wR1UL3cQ1Nlo+fyR46T0ak6MlAZG1avBt+mRHIhL9E5/JkgAyTOgMAaqKjOsbaypoXqC5ZqXBhLs2/Dvk33s+yUXfKdRP4t+UDZsCGFLC0jJQxexsdOHx2Go23v0xqqG05wUY3WKTg5aoL8448oi7p5VsB0mIuGlsfndSlOLla3J9UofEszEYOJVL6q+ac+nklnT6ZloHfqaWRVXKWY1p+khYP9JQPxm+L3X5Ocv+fYEcvjBOlgELM16gcQDpxOOGt8MRbhBcD1Fzwnv+X3T/6QP2EUPZzUehSa9C0OHjRXVluqW2ymvyT/6R8YwZNUXK2zbMBqKXTzPxX6ViVMq0VLon7EZZrcntbHTj7OkOEJHZiIAol4wKuKB7Ncm+4zjfInmXZtwDOmJUpEbO8LWQGH3rxVpBy85sC"
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
              "deferCommit": True
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
    res = requests.put(upload_url, headers={
        'Content-Type': 'application/octet-stream',
        'Content-Length': "0",
        'Content-Range': f'bytes {file_size}-{file_size - 1}/{file_size}'
    })
    r= res.json()
    print(r)

upload_file_chunked(
    file_path=f"/home/vmadmin/python/cy-py/cy_fucking_whore_microsoft/check_upload.py",
    drive_item_id="test moi"
)