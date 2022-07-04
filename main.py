import uvicorn
from fastapi import FastAPI
from typing import Optional
from fastapi.responses import JSONResponse

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
    uvicorn.run(app, host="0.0.0.0", port=5000)