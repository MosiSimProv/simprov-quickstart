FROM andreasruscheinski/simprov:latest

WORKDIR /
ADD ./requirements.txt .
RUN pip install -r requirements.txt
