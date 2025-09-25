How to enable https with Lets Encrypt Certbot

1. Install certbot-nginx on your machine
sudo apt install certbot python3-certbot-nginx -y

2. Then use your domain that specified before in nginx-template
sudo certbot --nginx -d example.com -d www.example.com

3. Follow the steps and the https should be enabled