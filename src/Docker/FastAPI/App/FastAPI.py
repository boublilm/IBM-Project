from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
from typing import Any, Dict, AnyStr, List, Union
import statistics
from utils.log import log
from server import ServerInterface
from fusion import FakeFusion
from utils.config import Configuration
import utils.definition as consts
import os

app = FastAPI()
config = Configuration()
if ("FAKE_FUSION" in os.environ and os.environ["FAKE_FUSION"].upper() == "TRUE" ):
    faker: FakeFusion = FakeFusion(config=config, server=ServerInterface(config=config))
    faker.generate_alerts()

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
        <html>
            <head>
                <title>IBM - NTA, Final Project</title>
            </head>
            <body>
                <h1>Welcome to IBM - NTA Final Project</h1>
            </body>
        </html>
        """
    return HTMLResponse(content=html_content, status_code=200)


@app.post(consts.SCORE_ENDPOINT_TOKEN)
async def predict(arbitrary_json: JSONStructure = None):
    if arbitrary_json is None:
        raise HTTPException(status_code=400, detail="No JSON provided")
    try:
        scores = []
        for detector in consts.DETECTORS_LIST:
            scores.append(arbitrary_json[b'score_details']['score explanation'][detector]['group_score'])
    except KeyError and TypeError:
        raise HTTPException(status_code=404, detail="Invalid JSON")

    return statistics.mean(scores)

@app.post(consts.FEEDBACK_ENDPOINT_TOKEN)
async def inset_feedback(arbitrary_json: JSONStructure = None):
    try:
        if arbitrary_json is None:
            raise HTTPException(status_code=400, detail="No JSON provided")

        arbitrary_json_str = dict((k.decode(),v) for k,v in arbitrary_json.items())
        ServerInterface(config=config).insert_new_feedback(feedback=arbitrary_json_str)
        return HTMLResponse(status_code=200, content="Successfully inserted feedback")
    except KeyError and TypeError as t:
        log.exception(t)
        raise HTTPException(status_code=404, detail="Invalid JSON")

    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail="Something went wrong")


uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile="localhost+2-key.pem",
            ssl_certfile="localhost+2.pem")
