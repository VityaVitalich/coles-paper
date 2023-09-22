#!/usr/bin/env bash

mkdir data

curl -OL https://storage.yandexcloud.net/datasouls-competitions/sirius/data.zip
unzip -j data.zip 'data/*.csv' -d data
mv data.zip data/
