[![Build Status](https://travis-ci.com/CityOfPhiladelphia/extract-knack.svg?branch=master)](https://travis-ci.com/CityOfPhiladelphia/extract-knack)

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

## Installation
```bash
pip install git+https://github.com/CityOfPhiladelphia/extract-knack#egg=extract_knack
```

## Deployment
When a commit is made to master or test, Travis CI bundles the code and its dependencies into a zip file, loads it to S3, and then publishes a new version of a lambda function using that updated zip file in S3. Additionally, Travis CI builds a docker image with an installed version of this repo and pushes it to ECR.

For this reason you should make changes to the test branch, make sure they pass automated tests and manual QA testing before making any changes to master.