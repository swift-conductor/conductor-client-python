#!/usr/bin/env bash

mkdir -p ./api
rm -rf ./api/*

java -jar openapi-generator-cli.jar generate \
  --input-spec http://localhost:8080/api-docs \
  --generator-name python \
  --output ./api \
  --config config.json
