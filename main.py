from fastapi import FastAPI, File, UploadFile, Request, Form, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

Model = tf.keras.models.load_model("models/model1")
classes = ["Early Blight", "Late Blight", "Potato Healthy"]
Model2 = tf.keras.models.load_model("models/model2")
classes2 = ['Bacterial spot', 'Early blight', 'Late blight', 'Leaf Mold', 'Septoria leaf spot', '2 spotted spider mite', 'Target Spot', 'YellowLeaf Curl Virus', 'mosaic virus', 'Tomato healthy']
Model3 = tf.keras.models.load_model("models/model3")
classes3 = ["Bacteria spot", "Pepper Healthy"]


def read_image(file)->np.ndarray:
    return np.array(Image.open(BytesIO(file)))

@app.post("/predict")
async def predict(request: Request, type: str = Body(...), file: UploadFile = File(...)):
    try:
        image = read_image(await file.read())
        batch = np.expand_dims(image,0)
        if type == 'tomato':
            pred = Model2.predict(batch) #prediction for batch(which has just one element)
            cl = classes2[np.argmax(pred[0])]
            conf = np.max(pred[0])
        elif type == 'pepper':
            pred = Model3.predict(batch) #prediction for batch(which has just one element)
            cl = classes3[np.argmax(pred[0])]
            conf = np.max(pred[0])
        else:
            pred = Model.predict(batch)
            cl = classes[np.argmax(pred[0])]
            conf = np.max(pred[0])
        res = f"Class: {cl} || Conf: {round(conf*100,2)}%"
    except Exception as e:
        print(e)
        res = "Upload Vaild Image"
    return templates.TemplateResponse("index.html", {"request": request, "pred": res})
    
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)