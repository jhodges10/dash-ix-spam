# Start node
`docker run -v ${PWD}/data:/home/dash/.dashcore --rm -p 9998:9998 --name dash_server -it -d jefethechefe/docker-dashd-nexus -server=1 -testnet=0`
`docker run -v ${PWD}/data:/home/dash/.dashcore --rm -p 9998:9998 --name dash_server -it -d jefethechefe/docker-dashd-nexus -server=1 -testnet=0 -rpcport=9998 -rpcallowip=0.0.0.0/0 -rpcauth=jeff:5cc5fa5bb15f5675603c36fdb7dccd9a$6b8223c1d5b23d38f2067ec1ef6450b773dd188f208d8136bc96804488a92ee7`

# attach to node and check status
`docker exec --user dash dash_server dash-cli getinfo`