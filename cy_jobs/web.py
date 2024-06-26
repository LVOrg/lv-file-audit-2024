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
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8087)