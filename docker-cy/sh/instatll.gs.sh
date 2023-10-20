#!/bin/bash
docker run --entrypoint /bin/bash -v $(pwd)/../../:/hack  -it jbarlow83/ocrmypdf
#apt-get update
#root@405092257b04:/app/share-storage# apt-get install tesseract-ocr-vie
#['/usr/local/lib/python3.10/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.10/dist-packages']
# mkdir -p /usr/local/lib/python3.10/site-packages
#pip install Pillow==9.5.0
#cp -r /app/env_jobs/lib/python3.10/site-packages/* /usr/local/lib/python3.10/dist-packages

#python3 /app/cy_consumers/files_upload.py
#python3 /app/cy_consumers/files_generate_thumbs.py
#python3 /app/cy_consumers/files_save_default_thumb.py
#python3 /app/cy_consumers/files_save_custom_thumb.py
#python3 /app/cy_consumers/files_generate_pdf_from_image.py
#python3 /app/cy_consumers/files_ocr_pdf.py
#python3 /app/cy_consumers/files_save_orc_pdf_file.py
#python3 /app/cy_consumers/files_extrac_text_from_image.py