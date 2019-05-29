#!/usr/bin/env bash

set -e

cd $TRAVIS_BUILD_DIR

mkdir dist

ZIP_FILE_PATH=$TRAVIS_BUILD_DIR/dist/extract-knack-$ENVIRONMENT.zip

echo "Zip up site-packages"
cd /home/travis/virtualenv/python3.5.6/lib/python3.5/site-packages/
zip -rq $ZIP_FILE_PATH .

echo "Zip together previous zip file and lambda function"
cd $TRAVIS_BUILD_DIR/lambda
zip -gq $ZIP_FILE_PATH index.py