from fastapi import FastAPI
from routes.embed import router as embed_router
from routes.inference import router as inference_router

app1 = FastAPI()

app1.include_router(embed_router, prefix="/api")
app1.include_router(inference_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app1, port=8000, host="0.0.0.0", reload=True)
