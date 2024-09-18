import os
import pathlib


class ExeService:
    def __init__(self):
        self.working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.output_dir = os.path.join(self.working_dir,"tmp","exe-file")
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir,exist_ok=True)


    def get_image(self, file_path):
        import pathlib

        filename_only = pathlib.Path(file_path).stem

        ret_file = os.path.join(self.output_dir, f"{filename_only}.ico")
        # icoextract [-h] [-V] [-n NUM] [-v] input output
        # print(f"{exec_path} {exe_file} {ret_file}")
        # exec_path = os.path.join(self.ext_lib_folder,"icoextract")
        # import icoextract
        # import argparse
        # import logging

        from icoextract import IconExtractor, logger, __version__

        def run(input: str, ouput: str):
            extractor = IconExtractor(input)
            extractor.export_icon(ouput, num=0)
            return ouput

        return run(file_path, ret_file)
