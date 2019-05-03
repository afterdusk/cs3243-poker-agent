#!/usr/bin/env bash
# Fetches and saves the tournament results.

FOLDER=$(date +%F)

mkdir -p $FOLDER

curl 'http://ddstratcollab01.d2.comp.nus.edu.sg/finalTournament/' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36' -H 'DNT: 1' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3' -H 'Referer: http://ddstratcollab01.d2.comp.nus.edu.sg/ranking/' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.9,eo;q=0.8' -H 'Cookie: visid_incap_1750112=NKqZkh+1TQeMa82t7NzowY9Bs1wAAAAAQUIPAAAAAAANkRVJK/m9kCojowJ0HNf4; _ga=GA1.3.2076910979.1555251610; visid_incap_1988269=EEiQiwkxRd+QcbDN2hlZolKly1wAAAAAQUIPAAAAAAD0MWcLUtzA3Iqro4lulu4i; incap_ses_1219_1988269=bkrlA/xoDlEvDUCJNMLqEFKly1wAAAAAspidKxgiZ+pTSqGX/sGK/A==; _gid=GA1.3.1124009879.1556850004; csrftoken=zdTuiwW30WUBByUmBZHNjmTOoF9mvMEOGkkgcVHWUJazH7SyMavIlfAAMXVDdQWq; sessionid=al6im50vcljfrj37gdnjrrynch63bo40' --compressed > $FOLDER/$(date +%T).html
