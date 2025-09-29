How to create a Reverse Proxy with Nginx

1. Install nginx on your machine
sudo apt install nginx -y

2. Change the placeholder in nginx-template.conf and place it to /etc/nginx/conf.d/example.conf
Examples:
<domain_name> -> example.domain.com
<app_ipaddress> -> 127.0.0.1
<port> -> 5000

3. After that test the nginx with
sudo nginx -t
and the result should like this:
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

4. After the test success reload nginx with
sudo systemctl reload nginx

5. And your reverse proxy should done.

Notes: Only accessible via http, if you want to use https follow enable-https-certbot tutorial in same folder