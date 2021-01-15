build:
	docker-compose build --pull

up:
	docker-compose up -d

down:
	docker-compose down -v

start: build up
