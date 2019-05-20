#!/usr/bin/env bash

set -e

cd $TRAVIS_BUILD_DIR

mkdir dist

echo "Zip up site-packages"
cd /home/travis/virtualenv/python3.5.6/lib/python3.5/site-packages/
zip -rq $TRAVIS_BUILD_DIR/dist/extract-knack.zip .

echo "Zip together previous zip file and lambda function"
cd $TRAVIS_BUILD_DIR/lambda
zip -gq $TRAVIS_BUILD_DIR/dist/extract-knack.zip index.py