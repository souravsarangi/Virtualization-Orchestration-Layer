#!/bin/bash
sudo apt-get install python-pip
sudo -E pip instal MySQLdb
mysql -u root -p sar < sar.sql
python ../src/hello.py
