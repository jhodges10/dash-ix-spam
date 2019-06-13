# Defining shell is necessary in order to modify PATH
SHELL := sh

now = `date -u +"%Y-%m-%dT%H:%M:%SZ"`
latest = `date -u +"%Y-%m-%d"`
log = echo "$(now) $(1)"

# -- Prep --
bootstrap:
	$(call log,"Fetching bootstrap file ...")
	curl -O https://dash-bootstrap.ams3.digitaloceanspaces.com/mainnet/$(latest)/bootstrap.dat.zip

bootstrap-testnet:
	$(call log,"Fetching bootstrap file ...")
	curl -O https://dash-bootstrap.ams3.digitaloceanspaces.com/testnet/$(latest)/bootstrap.dat.zip
	mv bootstrap.dat.zip /mn_api/data/testnet3/bootstrap.dat.zip

# -- Infra --
infra:
	$(call log,"Starting service ...")
	docker-compose up -d --force-recreate && \
	sleep 2 
	$(call log,"Services started.")

infra-stop:
	$(call log,"Stopping services ...")
	docker-compose stop
	$(call log,"Services stopped.")

infra-restart: infra-stop infra

# -- SCRIPTS --

run:
	$(call log,"Starting spam service ...")
	rq-dashboard
	sleep 2
	$(call log,"Started dashboard ...")

# If you need to run a target all all times, add force as that target's dependency
.PHONY: force

# Allow custom, per developer modifications/additions of the makefile to suit their workflow
-include local.mk
