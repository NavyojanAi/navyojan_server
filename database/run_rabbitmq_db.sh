docker run -d --rm --name rabbitmq \
        --hostname rabbitmq-db-server \
        -e RABBITMQ_DEFAULT_USER='navyojan' \
        -e RABBITMQ_DEFAULT_PASS='Networking123' \
        -p 5672:5672 \
        -p 15672:15672 \
        rabbitmq:3.13-management


docker run -d --rm --name rabbitmq --hostname rabbitmq-db-server -e RABBITMQ_DEFAULT_USER='navyojan' -e RABBITMQ_DEFAULT_PASS='Networking123' -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management
# -v ./rabbitmq:/var/lib/postgresql/data:rw \