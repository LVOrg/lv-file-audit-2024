import pathlib

import cy_kit_x
@cy_kit_x.thread_makeup()
def test(a,b):
    return  a+b
test(1,2).start()
log = cy_kit_x.create_logs(
    pathlib.Path(__file__).parent.__str__(),
    "test-001"
)
try:
    raise Exception("test")
except Exception as e:
    log.exception(e)
log.info(
    "Hello"
)