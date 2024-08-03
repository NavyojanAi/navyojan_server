docker run -d -ti --rm --name postgres-db-server \
    -e POSTGRES_PASSWORD='Networking@123' \
    -v /$(pwd)/postgres:/var/lib/postgresql/data:rw \
    -p 5432:5432 \
    postgres
