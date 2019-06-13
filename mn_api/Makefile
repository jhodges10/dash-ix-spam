# Defining shell is necessary in order to modify PATH
SHELL := sh

now = `date -u +"%Y-%m-%dT%H:%M:%SZ"`
latest = `date -u +"%Y-%m-%d"`
log = echo "$(now) $(1)"


# -- Prep --
bootstrap:
	$(call log,"Fetching bootstrap file ...")
	curl -O https://dash-bootstrap.ams3.digitaloceanspaces.com/mainnet/$(latest)/bootstrap.dat.zip

# -- Prep --
bootstrap-testnet:
	$(call log,"Fetching bootstrap file ...")
	curl -O https://dash-bootstrap.ams3.digitaloceanspaces.com/testnet/$(latest)/bootstrap.dat.zip
	mv bootstrap.dat.zip /data/testnet3/bootstrap.dat.zip

infra:
	$(call log,"Starting services ...")
	docker-compose up -d --force-recreate && \
	sleep 2 && \
	$(call log,"Services started.")

infra-stop:
	$(call log,"Stopping services ...")
	docker-compose stop
	$(call log,"Services stopped.")

infra-restart: infra-stop infra
