docker run -d -ti --name postgres-db-server \
    -e POSTGRES_PASSWORD='Networking123' \
    -v /$(pwd)/postgres:/var/lib/postgresql/data:rw \
    -p 25072:5432 \
    postgres

!/usr/bin/env pwsh

# # Create the directory if it doesn't exist
# $dir = "$((Get-Location).Path)\postgres"
# if (-Not (Test-Path -Path $dir)) {
#     New-Item -ItemType Directory -Path $dir
# }

# # Run the PostgreSQL container with provided credentials
# docker run -d -ti --name postgres-db-server `
#     -e POSTGRES_PASSWORD='AVNS_Bt_VNG6g8VOfas3VdMH' `
#     -v "${dir}:/var/lib/postgresql/data:rw" `
#     -p 25060:25060 `
#     postgres

docker run -d -ti --name navyojan-dev-postgres-db-server -e POSTGRES_PASSWORD='password' -v /postgres:/var/lib/postgresql/data:rw -p 5000:5432 postgres