FROM python:3.11


WORKDIR /rpgram_backend

COPY ./requirements.txt /rpgram_backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /sotrans_documents/requirements.txt

COPY ./src /src
WORKDIR /src


ENTRYPOINT ["hypercorn", "\"rpgram.main:create_app()\""]
