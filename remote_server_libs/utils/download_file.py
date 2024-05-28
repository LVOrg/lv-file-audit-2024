import typing

import requests
from tqdm import tqdm
import urllib.parse
def download_file_with_progress(url, filename)->typing.Tuple[str|None,dict|None]:
  """
  Downloads a file from the given URL with a progress bar.

  Args:
      url (str): URL of the file to download.
      filename (str): Name of the file to save locally.

  Raises:
      Exception: If an error occurs during download.
  """

  # Create response object

  response = requests.get(url, stream=True,verify=False)

  # Check for successful response
  if response.status_code >= 200  and response.status_code<300:
    # Get file size
    total_size = int(response.headers.get('content-length', 0))

    # Create progress bar
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename)

    with open(filename, 'wb') as file:
      for data in response.iter_content(chunk_size=1024):
        progress_bar.update(len(data))
        file.write(data)

    progress_bar.close()
    print(f"File '{filename}' downloaded successfully.")
    return filename,None
  else:
    return None, dict(code=f"{response.status_code}",message=response.text)
    # raise Exception(f"Error downloading file: {response.status_code}")

