
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
`cp config.ini.example config.ini`
`docker build -t get-your-vpn-config .`
`docker run --rm --name get-your-vpn -v /home/some/config.ini:/app/config.ini -p 8080:8080 get-your-vpn-config`