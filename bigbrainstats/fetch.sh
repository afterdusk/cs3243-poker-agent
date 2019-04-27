#!/usr/bin/env bash
# Fetches and saves the tournament results.

FOLDER=$(date +%F)

mkdir -p $FOLDER

curl 'http://ddstratcollab01.d2.comp.nus.edu.sg/finalTournament/' -H 'Connection: keep-alive' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36' -H 'DNT: 1' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.9,eo;q=0.8' -H 'Cookie: III_EXPT_FILE=aa28443; III_SESSION_ID=1d55190f7bd7d6463e805df528b52de5; SESSION_LANGUAGE=eng; _ga=GA1.3.1294284585.1526351723; lc_sso9022930=1548897950890; __lc.visitor_id.9022930=S1548897950.f6facbc542; lc_window_state=minimized; visid_incap_1988269=uYDGTAcsRaukfCRly/QhReIQklwAAAAAQUIPAAAAAAApndPejTziWuA2kuujbodo; incap_ses_960_1988269=9h0CNN20a28HL/dDeptSDeMQklwAAAAAdRiRLV3MziLWMcSQBdLnmQ==; csrftoken=g5CzU4XJKHsyxtb6xx69pNPc1Y028HNw2CisVmnG77xfgONKkqnkDgMBFnRxn0qA; sessionid=sb9j35xke35cet5f8xikkvhf4vc71vad' --compressed > $FOLDER/$(date +%T).html
