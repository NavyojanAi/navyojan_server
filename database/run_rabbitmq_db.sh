docker run -d --rm --name rabbitmq \
        --hostname localhost \
        -e RABBITMQ_DEFAULT_USER='guest' \
        -e RABBITMQ_DEFAULT_PASS='guest' \
        -p 5672:5672 \
        -p 15672:15672 \
        rabbitmq:3.13-management

# -v ./rabbitmq:/var/lib/postgresql/data:rw \