docker run -d -ti --name postgres-db-server \
    -e POSTGRES_PASSWORD='Networking@123' \
    -v /$(pwd)/postgres:/var/lib/postgresql/data:rw \
    -p 5432:5432 \
    postgres

#!/usr/bin/env pwsh

# # Create the directory if it doesn't exist
# $dir = "$((Get-Location).Path)\postgres"
# if (-Not (Test-Path -Path $dir)) {
#     New-Item -ItemType Directory -Path $dir
# }

# # Run the PostgreSQL container with provided credentials
# docker run -d -ti --name postgres-db-server `
#     -e POSTGRES_PASSWORD='Networking@123' `
#     -v "${dir}:/var/lib/postgresql/data:rw" `
#     -p 5432:5432 `
#     postgres

