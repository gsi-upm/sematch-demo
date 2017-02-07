FROM python:2.7

RUN pip install sematch
RUN pip install flask gensim 
RUN python -m sematch.download

COPY . /sematch-demo

WORKDIR /sematch-demo

EXPOSE 5005

RUN mkdir -p data/lsa_index
RUN mkdir -p data/tfidf_index

CMD ["python", "server.py"]
