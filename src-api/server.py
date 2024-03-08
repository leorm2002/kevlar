from os import path, environ, listdir
from transformers import pipeline
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random
import glob
import logging

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

max_results = 100

models_path = environ.get("MODEL_PATH", "./models")
device = environ.get("DEVICE", "cpu")
language = environ.get("CLASSLANG", "en")
label_mappings_path = environ.get("LABEL_MAPPINGS_PATH", "./label_mappings")
mt_label_path = environ.get("MT_LABEL_PATH", "./mt_labels.json")
ui_path = environ.get("UI_PATH", "./dist")
lang_mappings_path = environ.get("MAPPINGS_PATH", "./mappings.json")

test_path = environ.get("UI_PATH", "./test")

lang_mappings = {}
with open(lang_mappings_path, "r") as f:
    lang_mappings = json.load(f)

classifiers = {}
models = {}
for lang in lang_mappings:
    modelName = lang_mappings[lang]
    config_file = path.join(models_path, modelName, "config.json")
    if not path.exists(config_file):
        continue
    models[lang] = modelName
    logger.info(f"Loading model {modelName}...")
    model_path = path.join(models_path, modelName)

    classifiers[lang] = pipeline(
        'text-classification',
        model = model_path,
        tokenizer = model_path, 
        config = path.join(model_path, "config.json"),
        device = device,
        padding = True,
        truncation = True,
        top_k = None,
        max_length = 128)

langsToDo = {}

test_data = {}
for l in glob.glob(path.join(test_path, "*.json")):
    bn = path.basename(l)
    bn = bn.replace(".json", "")
    if bn not in lang_mappings:
        continue
    if bn not in models:
        continue
    if len(langsToDo) > 0 and bn not in langsToDo:
        continue
    logger.info(f"Loading {bn} test data")
    test_data[bn] = []
    with open(l, "r") as f:
        test_data_tmp = json.load(f)
        for k in test_data_tmp:
            newRecord = {}
            newRecord['labels'] = test_data_tmp[k]['eurovoc_classifiers']
            newRecord['title'] = test_data_tmp[k]['title']
            newRecord['text'] = test_data_tmp[k]['text'][:1000]
            test_data[bn].append(newRecord)

labels = {
    "tc": {},
    "mt": {},
    "do": {}
}
with open(path.join(label_mappings_path, f"{language}.json"), "r", encoding="utf-8") as f:
    labels['tc'] = json.load(f)
if path.exists(path.join(label_mappings_path, f"{language}_mt.json")):
    with open(path.join(label_mappings_path, f"{language}_mt.json"), "r", encoding="utf-8") as f:
        labels['mt'] = json.load(f)
if path.exists(path.join(label_mappings_path, f"{language}_do.json")):
    with open(path.join(label_mappings_path, f"{language}_do.json"), "r", encoding="utf-8") as f:
        labels['do'] = json.load(f)

parents = {}
if path.exists(mt_label_path):
    with open(mt_label_path, "r", encoding="utf-8") as f:
        parents = json.load(f)

logger.info("Starting API...")
# Allow CORS for all origins
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins = ['*'],
        # allow_credentials=True, # uncomment this line if you want to allow credentials, but you have to set allow_origins to a list of allowed origins
        allow_methods = ['*'],
        allow_headers = ['*'],
        expose_headers = ['access-control-allow-origin'],
    )
]

app = FastAPI(middleware=middleware)
if path.exists(ui_path):
    app.mount("/ui", StaticFiles(directory=ui_path, html = True), name="ui")


# Define the request body. It should contain only a text field
class TextRequest(BaseModel):
    text: str = ""
    model: str
    title: str = ""
    top_k: int = 50
    threshold: float = 0.0
    greedy: bool = False

# Dummy endpoint to check if the API is running
@app.get("/api/models")
async def get_data():
    return models

@app.get("/api/random")
async def get_data(lang):
    if not lang:
        lang = random.choice(list(test_data.keys()))
    element = random.choice(test_data[lang])
    ret = {}
    ret['text'] = element['text']
    ret['title'] = element['title']
    ret['lang'] = lang
    ret['model'] = lang_mappings[lang]
    ret['labels'] = []
    for label in element['labels']:
        p = {}
        p['label'] = label
        p['description'] = labels['tc'][label]
        p['mapping'] = {}
        p['do'] = {}
        if p['label'] in parents and parents[p['label']] in labels['mt']:
            p['mapping']['label'] = parents[p['label']]
            p['mapping']['description'] = labels['mt'][parents[p['label']]]
            do_label = parents[p['label']][0:2]
            if do_label in labels['do']:
                p['do']['label'] = do_label
                p['do']["description"] = labels['do'][do_label]
        ret['labels'].append(p)
    return ret

# Endpoint to get the predictions for a text
@app.post("/api/predict")
async def post_data(request: TextRequest, Token: str = Header(None, convert_underscores=False)):

    if environ.get("AUTH_TOKEN") and Token != environ.get("AUTH_TOKEN"):
        raise HTTPException(status_code=500, detail="Wrong token header")

    text = request.text
    model = request.model
    title = request.title
    top_k = request.top_k
    threshold = request.threshold
    greedy = request.greedy

    text = title + "\n" + text

    if len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty text and title")

    if model not in classifiers:
        raise HTTPException(status_code=400, detail=f"Model '{model}' does not exist")

    t = models[model]
    predictions = classifiers[model](text)
    good_predictions = []
    i = 0
    for p in predictions[0]:
        p['description'] = labels["tc"][p['label']]
        p['mt'] = {}
        p['do'] = {}
        if p['label'] in parents and parents[p['label']] in labels['mt']:
            p['mt']['label'] = parents[p['label']]
            p['mt']['description'] = labels['mt'][parents[p['label']]]
            do_label = parents[p['label']][0:2]
            if do_label in labels['do']:
                p['do']['label'] = do_label
                p['do']["description"] = labels['do'][do_label]
        i += 1
        # condition = i > top_k or threshold > p['score']
        # if greedy:
        #     condition = i > top_k and threshold > p['score']
        # if condition or i > max_results:
        #     break
        if p['score'] < 0.01:
            break
        good_predictions.append(p)

    return good_predictions
