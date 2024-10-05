FROM python:3.11


WORKDIR /rpgram_backend

COPY ./requirements.txt /rpgram_backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /rpgram_backend/requirements.txt

COPY ./src /src
WORKDIR /src

EXPOSE 8000

CMD python -m rpgram.hype
