import pathlib
import sys
working_dir = pathlib.Path(__file__).parent.parent.__str__()
task_dir = pathlib.Path(__file__).parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
from  cyx.common import config
from celery import Celery

app = Celery('tasks', broker=f'pyamqp://guest:guest@{config.rabbitmq.server}:{config.rabbitmq.port}//')

@app.task(binding='app1.tasks')
def add(x, y):
    import xxx
    print(f"cong {x},{y}")
    return x + y
#celery -A cy_brokers/check.py worker --loglevel=INFO
if __name__ == '__main__':
    args = ['worker', '--loglevel=INFO']
    app.worker_main(argv=args)