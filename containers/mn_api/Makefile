# Defining shell is necessary in order to modify PATH
SHELL := sh

now = `date -u +"%Y-%m-%dT%H:%M:%SZ"`
latest = `date -u +"%Y-%m-%d"`
log = echo "$(now) $(1)"

build:
	IMAGE=${IMAGE} bash scripts/build.sh

test:
	IMAGE=${IMAGE} bash scripts/test.sh

tags:
	IMAGE=${IMAGE} bash scripts/tags.sh

publish:
	docker push ${IMAGE}

.PHONY: force