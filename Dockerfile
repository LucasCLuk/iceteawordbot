FROM gorialis/discord.py:3.7.4-alpine-pypi-full

WORKDIR /app

COPY requirements.txt ./

RUN apk add --update --no-cache g++ gcc libxslt-dev libffi-dev python3-dev make && \
	pip install -r requirements.txt


COPY . .

CMD ["python", "bot.py"]
