FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-devel

WORKDIR /code

COPY requirements.txt requirements.txt

COPY infer.py infer.py

COPY inference.py inference.py

RUN pip install -r requirements.txt

EXPOSE 7676

CMD ["uvicorn", "inference:router", "--host", "0.0.0.0", "--port", "7676"]