import uvicorn
from fastapi import FastAPI
from typing import Optional
from fastapi.responses import JSONResponse
import logging
# from python_elastic_logstash import ElasticHandler, ElasticFormatter


app = FastAPI()


@app.get("/")
async def bmi(height: float, weight: float):

    bmi = round((weight / (height/100)**2), 1)
    if bmi < 18.5:
        return JSONResponse(
            content={
                "bmi": bmi,
                "label": "Underweight"
            },
            status_code=200)
    elif bmi >= 18.5 and bmi < 24.9:
        return JSONResponse(
            content={
                "bmi": bmi,
                "label": "Normal weight"},
            status_code=200)
    elif bmi >= 25.0 and bmi < 29.9:
        return JSONResponse(
            content={
                "bmi": bmi,
                "label": "Overweight"},
            status_code=200)
    elif bmi >= 30.0 and bmi < 39.9:
        return JSONResponse(
            content={
                "bmi": bmi,
                "label": "Obese"},
            status_code=200)
    elif bmi >= 40.0:
        return JSONResponse(
            content={
                "bmi": bmi,
                "label": "Morbidly Obese"},
            status_code=200)

if __name__ == "__main__":
    # logging.basicConfig(level="INFO")
    # logging.info("Creating handler")
    # root = logging.getLogger()
    # hdlr = root.handlers[0]
    # json_format = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
    # hdlr.setFormatter(json_format)
   
    Log_Format = "%(levelname)s %(asctime)s - %(message)s"

    logging.basicConfig(filename = "log/logfile.log",
                    filemode = "w",
                    format = Log_Format, 
                    level = logging.INFO)

    logger = logging.getLogger()
    uvicorn.run(app, host="0.0.0.0", port=6000)