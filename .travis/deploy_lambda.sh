#!/usr/bin/env bash

aws lambda update-function-code  \
    --function-name extract-knack-$ENVIRONMENT \
    --s3-bucket citygeo-airflow-databridge2 \
    --s3-key lambda/extract-knack-$ENVIRONMENT.zip