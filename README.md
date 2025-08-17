# KASMAS

KASMAS (Kitchen and Storage Management System) is a smart fridge project running on a Raspberry Pi to track your food supplies at home. The Raspberry Pi also hosts a webserver, where you can check the contents of your fridge from anywhere in the world.

---

## Features

- Use a barcode-scanner to add, remove and modify items in your storage.
- Items in stock are listed on a touchscreen.
- Keep track of expiration dates of items.
- Raspberry pi hosts a webserver which hosts a password-protected website to check your fridge while shopping.

---

## Requirements

### Hardware
- Raspberry Pi (here model 3B)
- (Touch-) Screen with HDMI port
- Barcode-scanner with UART communication protocol (optional but recommended)

### Software
- Python 3.9
- pyserial (for Barcode-scanner)
- python-dateutil
- Apache2 (for webserver)
- Certbot (if you want a secure https connection)

## Installation

1. clone the repository to a local folder

    ```bash
    git clone https://www.github.com/mazae1/KASMAS
    ```
2. install python dependencies

    ```bash
    pip install -r requirements.txt
    ```
3. adapt **'config.json'** to your system

4. (optional) install apache2, default website path is **'var/www/html/'**
    ```bash
    sudo apt install apache2
    ```
5. (optional) install certbot
    ```bash
    sudo apt install certbot
    ```
6. (optional) forward port 80 (http) and/or port 443 (https) from your router to the Raspberry Pi

7. (optional) get a ddns service if your router has a dynamic id (e.g. noip)

8. (optional) get necessary certificate for https connections
    ```bash
    sudo certbot --apache -d <your-domain-name>.ddns.net
    ```