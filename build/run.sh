#!/usr/bin/env bash
set -e

rm -rf gcp_credentials.json

cat << EOF >> gcp_credentials.json
$GOOGLE_APPLICATION_CREDENTIALS
EOF

TAG=sisense-sanity-tests
echo "Building the sisense sanity tests docker image"
docker build -f build/Dockerfile -t ${TAG} .

docker run -e SISENSE_USERNAME="${SISENSE_USERNAME}" \
-e SISENSE_PASSWORD="${SISENSE_PASSWORD}" \
-e ENVIRONMENT="${ENVIRONMENT}" \
-e DASHBOARD_NAME="${DASHBOARD_NAME}" \
-e FROM_ADDR="${FROM_ADDR}" \
-e TO_ADDR="${TO_ADDR}" \
-e FROM_PASSWORD="${FROM_PASSWORD}" \
-e THREAD="${THREAD}" \
  ${TAG}

function cleanup(){
  rm -rf gcp_credentials.json
  docker rmi -f ${TAG}
}

trap cleanup EXIT
