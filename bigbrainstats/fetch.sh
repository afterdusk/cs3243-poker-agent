#!/usr/bin/env bash
# Fetches and saves the tournament results.

FOLDER=$(date +%F)

mkdir -p $FOLDER

curl 'http://ddstratcollab01.d2.comp.nus.edu.sg/ranking/' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.9' -H 'Cookie: _ga=GA1.3.1208109439.1553476399; _fbp=fb.2.1553476399040.1905622766; csrftoken=TUy9cOGWyJKxiyDpmrE09vJx5CIAxKUkcWe6Pz39Sy4hAkRo94caQ0MRuekJMW3Q; sessionid=c6kwi6myhhp1iesw783fvrs7vv32p8dd; _gid=GA1.3.549081127.1554308588' --compressed > $FOLDER/$(date +%T).html
