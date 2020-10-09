import os

import requests
import configparser
import shutil
from random import randint
from reportlab.pdfgen.canvas import Canvas
from svglib.svglib import svg2rlg
from discord_webhook import DiscordWebhook, DiscordEmbed


config_name = 'config.ini'
config = configparser.ConfigParser()
if os.path.isfile(config_name):
    config.read(config_name)
else:
    config['DISCORD'] = {
        'webhook': ''
    }

    with open(config_name, 'w') as configfile:
        config.write(configfile)

url = input("url? ")
name = input("name? ")

# Checking url
print("Checking url..")
status_code = requests.get(url + "1").status_code
if status_code != 200:
    print(f"Specified url is not valid (error: {status_code})")
    exit(1)  # Exit if url isn't valid

print("Url is valid, fetching..")

# Fetching and saving svg
i = 1
c = Canvas(name + '.pdf', pagesize=(1200, 650))

os.makedirs(os.path.join(os.curdir, name), exist_ok=True)

while True:
    print("Requesting page", i)
    request = requests.get(url + str(i))
    if request.status_code == 200:
        with open(os.path.join(name, str(i)) + ".svg", "w") as image:
            image.write(request.text)
        svg2rlg(os.path.join(name, str(i) + ".svg")).drawOn(c, 0, 0)
        c.showPage()
    else:
        print(f"Unknown page {i}")
        break
    i += 1

print("Saving to pdf..")
c.save()

print("Deleting svgs")
shutil.rmtree(os.path.join(os.curdir, name))

# Upload to discord if webhook in config
if 'DISCORD' in config and config['DISCORD']['webhook'] != '':
    print("Uploading to Discord..")
    webhook = DiscordWebhook(config['DISCORD']['webhook'])
    embed = DiscordEmbed(title="Nouvelle présentation!", color=randint(100000, 999999))
    embed.set_description(name)

    with open(name + ".pdf", "rb") as file:
        webhook.add_file(file=file.read(), filename=name + ".pdf")

    webhook.add_embed(embed)
    response = webhook.execute()

    if response.status_code == 200:
        print("Sent on Discord!")
    else:
        print(f"Something went wrong! (status_code: {status_code}")
