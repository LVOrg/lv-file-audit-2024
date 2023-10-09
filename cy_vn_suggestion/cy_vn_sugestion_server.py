import pathlib
import sys

working_dir = pathlib.Path(__file__).parent.__str__()
sys.path.append(working_dir)
from fastapi import FastAPI, Body
from  pydantic import BaseModel
import uvicorn

app = FastAPI()

from cy_vn_suggestion.suggestions import suggest

txt = suggest("kiem tra tieng viet khong dau")
print(txt)

class InputModel(BaseModel):
    input: str
@app.post("/suggest")
async def suggest_text(text: str=Body(...)):
    return suggest(text)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
