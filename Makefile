.PHONY: all up down build logs clean fclean re

all: up

# build images and start everything in the background
up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

# stop and remove containers and volumes (database data is lost)
clean:
	docker compose down -v

# clean + remove images built by this project
fclean:
	docker compose down -v --rmi local

re: fclean up
