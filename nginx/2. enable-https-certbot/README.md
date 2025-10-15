## How to enable https with Lets Encrypt Certbot

* Install certbot-nginx on your machine
```sh
sudo apt install certbot python3-certbot-nginx -y
```

* Then use your domain that specified before in nginx-template
```sh
sudo certbot --nginx -d example.com -d www.example.com
```

* Follow that steps and the https should be enabled
