import argparse
import json
import pathlib
import subprocess
import sys
import os
if __name__ == '__main__':
    if sys.platform == "linux":
        import signal
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    parser = argparse.ArgumentParser(description='Do OCR file')
    parser.add_argument('input', help='Image file for OCR')
    parser.add_argument('output', help='Image file for OCR')
    parser.add_argument('verify', help='verify file for OCR')
    args = parser.parse_args()
    if not os.path.isfile(args.input):
        raise FileNotFoundError(args.input)
    print(f"generate image from {args.input} ... to {args.output}")
    command = ["/usr/bin/soffice",
               "--headless",
               "--convert-to",
               "png", "--outdir",
               f"{args.output}",
               args.input]
    print(" ".join(command))
    # Execute the command using subprocess
    try:
        subprocess.run(command, check=True)
        ret= dict(
            result=os.path.join(
                args.output,
                f"{pathlib.Path(args.input).stem}.png")
        )
        with open(f"{args.verify}.txt","wb") as ret_fs:
            ret_fs.write(json.dumps(ret).encode())

        print(f"generate image from {args.input} ... to {args.output} successfully!")

    except subprocess.CalledProcessError as error:
        str_error = str(error)
        ret = dict(
            error= str_error
        )
        with open(f"{args.verify}.txt", "wb") as ret_fs:
            ret_fs.write(json.dumps(ret).encode())
        print(f"generate image from {args.input} ... to {args.output} fail!", error)

    #/usr/bin/soffice --headless --convert-to png --outdir /tmp-files /tmp-files/759d6cb7-83cb-4d92-9b83-711f9733a457.docx

    #/usr/bin/soffice --headless --convert-to png --outdir "/tmp-files" "/tmp-files/38cdd081-dc5d-4d8d-9e8b-614e3f278c57.docx"
