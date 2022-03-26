# Nginx configuration for `get-your-vpn`

Inspired by tutorial [How To Create a Self-Signed SSL Certificate for Nginx in Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-16-04)

## Create keys
Create a self-signed key and certificate pair with OpenSSL.

```sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./nginx-selfsigned.key -out ./nginx-selfsigned.crt```

We should also create a strong Diffie-Hellman group, which is used in negotiating Perfect Forward Secrecy with clients.

```sudo openssl dhparam -out ./dhparam.pem 2048```

## Run nginx
`docker-compose up -d`