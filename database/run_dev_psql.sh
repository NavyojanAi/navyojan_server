mkdir -p dev-data-psql

docker run -d -ti --rm --name navyojan-psql-dev-server \
    -e POSTGRES_PASSWORD='navyojan@123' \
    -v ./dev-data-psql:/var/lib/postgresql/data:rw \
    -p 5432:5432 \
    postgres
