
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