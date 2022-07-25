upload:
	sh bin/upload.sh

test-upload:
	sh bin/test-upload.sh

build:
	sh bin/build.sh

install:
	sh bin/install.sh

docker-build:
	sh bin/docker-build.sh

docker-run:
	docker run --rm -it pubsub-meta bash

format:
	black .