import pathlib
import sys

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
from cyx.common import config
from fastapi import FastAPI

app = FastAPI()
from cy_jobs.controllers.files_controller import FilesController
from cy_jobs.controllers.file_pushing_controller import FilesPushingController
@app.get("/healthz")
async def health_check():
  """A simple health check endpoint."""
  return {"message": "Healthy!"}
app.include_router(router=FilesController.router())
app.include_router(router=FilesPushingController.router())
if __name__ == "__main__":
  bin_info= config.bind or "0.0.0.0:8007"
  host =bin_info.split(":")[0]
  port = int (bin_info.split(":")[1])
  import uvicorn
  import psutil
  number_of_workers = psutil.cpu_count(logical=False)
  uvicorn.run(app, host=host, port=port)