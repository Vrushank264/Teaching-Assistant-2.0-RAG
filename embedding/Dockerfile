FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-devel

WORKDIR /code

COPY requirements.txt requirements.txt

COPY embedding embedding

COPY app app

COPY inference_code inference_code

RUN pip install -r requirements.txt

EXPOSE 8000

RUN cd app/routes/

RUN pwd

CMD ["uvicorn", "embed:router", "--host", "0.0.0.0", "--port", "8000"]