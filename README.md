
# openvpn - application
- docker container + (уже есть)
- as service systectl

# Admin flow
- console/http request to service to
    - generate new user w/ security code
    - save it to db
    - return security code associated w/ user

# User flow
- user opens web page
    - enter security code
    - make up password for new ovpn file
- service asks openvpn
    - openvpn generate key pairs
    - openvpng enerate ovpn file
    - service returns ovpn file
    
    
# How to run
The Docker images use Python 3.13.18 on Debian Bookworm and the application
requires Python 3.13. The pinned CA bundle removes the compromised eMudhra
chain. Rebuild with `docker build --pull` and redeploy to apply the runtime and
dependency security fixes to existing installations.

`cp config.ini.example config.ini`

`docker build -t get-your-vpn-config .`

`docker run --rm --name get-your-vpn -v $(pwd)/config.ini:/app/config.ini -p 8080:8080 get-your-vpn-config`

Or

`touch get-your-vpn-config.sqlite3`

`docker-compose up`

# How to run tests

`./run_tests.sh`
