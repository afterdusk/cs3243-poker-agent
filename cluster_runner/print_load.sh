#!/usr/bin/bash

# SSHs into all cluster machines and prints their loadavgs, sorted in asc order.
# Source: Tee Hao Wei in Spamistan group.

XCNHOSTS="xcna0 xcna1 xcna2 xcna3 xcna4 xcna5 xcna6 xcna7 xcna8 xcna9 xcna10 xcna11 xcna12 xcna13 xcna14 xcna15 xcnc0 xcnc1 xcnc2 xcnc3 xcnc4 xcnc5 xcnc6 xcnc7 xcnc8 xcnc9 xcnc10 xcnc11 xcnc12 xcnc13 xcnc14 xcnc15 xcnc16 xcnc17 xcnc18 xcnc19 xcnc20 xcnc21 xcnc22 xcnc23 xcnc24 xcnc25 xcnc26 xcnc27 xcnc28 xcnc29 xcnc30 xcnc31 xcnc32 xcnc33 xcnc34 xcnc35 xcnc36 xcnc37 xcnc38 xcnc39 xcnc40 xcnc41 xcnc42 xcnc43 xcnc44 xcnc45 xcnc46 xcnc47 xcnc48 xcnc49 xcnb0 xcnb1 xcnb2 xcnb3 xcnb4 xcnb5 xcnb6 xcnb7 xcnb8 xcnb9 xcnb10 xcnb11 xcnb12 xcnb13 xcnb14 xcnb15 xcnb16 xcnb17 xcnb18 xcnb19 xcnd0 xcnd1 xcnd2 xcnd3 xcnd4 xcnd5 xcnd6 xcnd7 xcnd8 xcnd9 xcnd10 xcnd11 xcnd12 xcnd13 xcnd14 xcnd15 xcnd16 xcnd17 xcnd18 xcnd19 xcnd20 xcnd21 xcnd22 xcnd23 xcnd24 xcnd25 xcnd26 xcnd27 xcnd28 xcnd29 xcnd30 xcnd31 xcnd32 xcnd33 xcnd34 xcnd35 xcnd36 xcnd37 xcnd38 xcnd39 xcnd40 xcnd41 xcnd42 xcnd43 xcnd44 xcnd45 xcnd46 xcnd47 xcnd48 xcnd49 xcnd50 xcnd51 xcnd52 xcnd53 xcnd54 xcnd55 xcnd56 xcnd57 xcnd58 xcnd59"
XGPHOSTS="xgpa0 xgpa1 xgpa2 xgpa3 xgpa4 xgpb0 xgpb1 xgpb2 xgpc0 xgpc1 xgpc2 xgpc3 xgpc4 xgpc5 xgpc6 xgpc7 xgpc8 xgpc9 xgpd0 xgpd1 xgpd2 xgpd3 xgpd4 xgpd5 xgpd6 xgpd7 xgpd8 xgpd9"

echo $XCNHOSTS $XGPHOSTS | tr ' ' '\n' | \
    parallel --timeout 5 \
    'ssh -oBatchMode=yes -oStrictHostKeyChecking=no -q {} '"'"'echo {} $(cat /proc/loadavg)'"'" 2> /dev/null | \
    sort -nk2
