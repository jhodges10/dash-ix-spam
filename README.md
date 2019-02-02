# dash-ix-spam

## Setup

1. First run `make install` to install requirements
2. Then, to setup infrastructure, make sure you have Docker installed and then run, `make infra`
3. Then, start up a worker with `rq worker`
4. Then run `python3 ixspam.py` and set the spam speed you want
5. Profit