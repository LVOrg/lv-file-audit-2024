# def verify_header(data_header,fs):
#     pos =fs.tell()
#     fs.seek(0)
#     data = fs.read(len(data_header))
#     if data != data_header:
#         raise Exception()
#     fs.seek(pos)
#
# def verify_footer(data_footer,fs):
#     pos =fs.tell()
#     fs.seek(-len(data_footer),2)
#     data = fs.read(len(data_footer))
#     if data != data_footer:
#         raise Exception()
#     fs.seek(pos)