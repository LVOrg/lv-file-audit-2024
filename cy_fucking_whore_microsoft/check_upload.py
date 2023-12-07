import requests
import os
token = "EwCIA8l6BAAUAOyDv0l6PcCVu89kmzvqZmkWABkAAfwgeoDD0TysOm+6UTZhKswBRhwhkJA+Hq9UDdjPv6GKMV288ZbH7MrCK20aGjI/SY7mQYHiFfsxRE7hWq5t1GChQJ+lthI9ZPwKruWiMHbHsxGrPs1plF/PzRo6GjVtj16qd/1coezZda0YD98jsOreqBNAK3jpTSdMUcvdGszmnnT0ZDxQBIa8vZefv7BGWgeSvTX2eyVsvZemKZ1o770SlUAIedIhfbEnh7Bn+BVaQFrhie/6kxSXMoARqnhuZM1daJPQD/GnxNetL1eX2u0WB5fymseGS8VeesfvNoLu1LjvOxiVZ5HvJEhtjJ4/iPNxzPg92YqfL4Yligd9vhsDZgAACKPmAsZBisLnWAJ32tloUQ0qsN0LxpyOc3aabYvoEx+waqt+8ObCWHfqOa+aLd4bO5LWrOQe3RzZKuekGNHgzlmoyW9W0iISnwO3WgiY6bbHq+NdOX9eCb/o20+XRjvbfEGinM9nDfJLnKVoO1YosJHeUIeQCODKhKGw9LdwSGb4gX8Ev+QJqDGlZ3VkHl2+qW6zdqS23OQoWEJ9Dedbd3N+8Kq62gw7NL8xAiig4O8IJVKAtmQi0iMyZtAbcydbm5jXUNE0ZCZQe0/HcBizVGJC0J6A10qxHjDKPw/OTDRllkFurGLRcb21vH5AC0wpmu3n6exai5IhRPdS4ysEBGZJTx9kN9dn3LskuNJi52eaTV0OX+Wf5czpTB/qgQQw1kWEp5m4T49OhpsSOWvM/HUeZ3U2pD9gNFRqvQU1bC5lVp9VwDHWqL9vtUU7uBJEontb0hKrwq25sTFNQEh/8DDvLaGxUmbQgVHC6a1gBbsB4vsFN403/sMYraEsuk/pRJXfQnRo7qJRK76ZS86Aq/TBrWANVh+tbLrVkkqmSiFBQhB/QiYu+Oj+zm0ejSKNoUsiILVuDgfMSe2aqaSSAiKaxnqmVq67OomA2a/BAc0IZycvHZM3A2i4XTeM9rT8vcKG7jSujlufvGCQTBteGmrAI0ehjRbhZlKoQMLhP5tept06h94NG+lAi+sRLsq0xZsuJ/vpxpkYz9CzC5JB1H1JpGr96yLFMhI0U7RzFHmt/989X/xUN9ca1McdWYkOq49uvIMk6h7WvxC87s19l4PCxaj6avoQQxf0hn0FHfNHWEibAg=="
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
    requests.put(upload_url, headers={'Content-Type': 'application/octet-stream'})

upload_file_chunked(
    file_path=f"/home/vmadmin/python/cy-py/cy_fucking_whore_microsoft/check_upload.py",
    drive_item_id="553ae3ba-037a-4fc4-bd8e-368b06692c06"
)