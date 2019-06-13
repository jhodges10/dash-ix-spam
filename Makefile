# Defining shell is necessary in order to modify PATH
SHELL := sh

now = `date -u +"%Y-%m-%dT%H:%M:%SZ"`
log = echo "$(now) $(1)"

install: pip3 install -r requirements.txt

# -- Database --

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
