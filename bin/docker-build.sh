#!/bin/sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

python3 -m build

VERSION=$(cat setup.cfg | grep "version =" | cut -d = -f 2 | xargs)

docker build . \
  --build-arg version=$VERSION \
  --tag pubsub-meta:latest \
  --tag pubsub-meta:$VERSION