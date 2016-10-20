# LetsEncryptAutoRenew
This is an script to renew your let's encrypt certificate. you can then cron the script to have auto renew on IE: 60 days.I will also give you exemple of the cron task i set. an exemple .ini file is available.

Enjoy

#crontab entry exemple
0 0 1 */2   * /path/to/script/autorenew.py
