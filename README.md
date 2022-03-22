# Telegram Gallery
Warning: you need to create your own local Telegram bot API server to run this. Main Telegram bot API server has a lot of limitations, so this program can't work well.
Use this [official guide](https://github.com/tdlib/telegram-bot-api) to setup local server.

All photos stored in JPG format to optimize size. HEIC and PNG will be converted to JPG too.

---
Installing requirements:
`sudo pip3 install pyTelegramBotAPI face_recognition numpy`
Imagemagick with HEIC support required. You can check is heic enabled or not using "convert --version". As installation guides you can use [step 1](https://eplt.medium.com/5-minutes-to-install-imagemagick-with-heic-support-on-ubuntu-18-04-digitalocean-fe2d09dcef1) from this guide.
