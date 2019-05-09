# extract-knack
Command line tool to extract data and schemas from Knack.

## Requirements
- Python 3.5+
- Pip
- Knack Application ID and Knack API Key

## Usage
```bash
# Extract a schema from knack to stdout
extract-knack generate-schema \
              your-knack-app-id \
              your-knack-api-key-9hdb3dsaplcd \
              object_id \
              --ident 4 # Optionally indent some number of spaces

# Extract a schema from knack to S3
extract-knack generate-schema \
              your-knack-app-id \
              your-knack-api-key-9hdb3dsaplcd \
              object_id \
              --ident 4 \ # Optionally indent some number of spaces
              --s3_bucket my-s3-bucket \
              --s3_key dir/schema_name.json

# Extract records from knack to stdout
extract-knack extract-records \
              your-knack-app-id \
              your-knack-api-key-9hdb3dsaplcd \
              object_id

# Extract records from knack to S3
extract-knack extract-records \
              your-knack-app-id \
              your-knack-api-key-9hdb3dsaplcd \
              object_id \
              --s3_bucket my-s3-bucket \
              --s3_key dir/schema_name.json
```