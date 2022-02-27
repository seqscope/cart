tippecanoe -e tile/$1 -pC -Z6 -z15 -pd geojson/$1.geojson  -r1 -M 5000000 -O 1000000 -pf --force -s EPSG:3857
aws s3 cp tile/$1 s3://seqscope-web-test/tile/$1 --recursive --profile sqs  --quiet
