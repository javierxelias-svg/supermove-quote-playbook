# RECEIPT: raw eval output, 2026-10-27 (v2, current code)

Expected answers unchanged since frozen:
- samples/expected.json == cache/expected.FROZEN-before-first-run.json
- samples/hard_expected.json == cache/hard_expected.FROZEN-before-first-run.json
- samples/holdout_expected.json == cache/holdout_expected.FROZEN-before-first-run.json

## python3 eval.py 
```
lead  route (want)               fields  missed flags                 false flags            bad quotes
L01   inbox (inbox)              9/9     -                            -                      -
L02   inbox (inbox)              9/9     -                            -                      -
L03   ask (ask)                  9/9     -                            -                      -
L04   ask (ask)                  9/9     -                            -                      -
L05   auto_quote (auto_quote)    9/9     -                            -                      -
L06   inbox (inbox)              9/9     -                            -                      -
L07   ask (ask)                  9/9     -                            -                      -
L08   inbox (inbox)              9/9     -                            -                      -
L09   ask (ask)                  9/9     -                            -                      -
L10   inbox (inbox)              9/9     -                            -                      -

fields correct : 90/90
flags caught   : 14/14  (missed 0)
false flags    : 0
route correct  : 10/10
quotes verbatim: 74/74
extract failed : 0
```

## python3 eval.py hard
```
lead  route (want)               fields  missed flags                 false flags            bad quotes
H01   inbox (inbox)              9/9     -                            -                      -
H02   inbox (inbox)              9/9     -                            -                      -
H03   inbox (inbox)              9/9     -                            -                      -
H04   auto_quote (auto_quote)    9/9     -                            -                      -
H05   inbox (inbox)              9/9     -                            -                      -

fields correct : 45/45
flags caught   : 5/5  (missed 0)
false flags    : 0
route correct  : 5/5
quotes verbatim: 34/34
extract failed : 0
```

## python3 eval.py holdout
```
lead  route (want)               fields  missed flags                 false flags            bad quotes
X01   inbox (inbox)              9/9     -                            -                      -
X02   auto_quote (auto_quote)    9/9     -                            -                      -
X03   ask (ask)                  9/9     -                            -                      -
X04   inbox (inbox)              9/9     -                            -                      -
X05   inbox (inbox)              9/9     -                            -                      -

fields correct : 45/45
flags caught   : 7/7  (missed 0)
false flags    : 0
route correct  : 5/5
quotes verbatim: 37/37
extract failed : 0
```

## v1 (before fix), from runs/v1/
```
lead  route (want)               fields  missed flags                 false flags            bad quotes
L01   inbox (inbox)              9/9     -                            -                      -
L02   inbox (inbox)              9/9     -                            -                      -
L03   ask (ask)                  9/9     -                            -                      -
L04   ask (ask)                  9/9     -                            -                      -
L05   auto_quote (auto_quote)    9/9     -                            -                      -
L06   inbox (inbox)              9/9     -                            -                      -
L07   ask (ask)                  9/9     -                            -                      -
L08   inbox (inbox)              9/9     -                            -                      -
L09   ask (ask)                  9/9     -                            -                      -
L10   inbox (inbox)              9/9     -                            -                      -

fields correct : 90/90
flags caught   : 14/14  (missed 0)
false flags    : 0
route correct  : 10/10
quotes verbatim: 76/76
extract failed : 0
```
```
lead  route (want)               fields  missed flags                 false flags            bad quotes
H01   auto_quote (inbox) X       8/9     STAIRS_NO_ELEVATOR           -                      -
      field origin_elevator: want False, got None
H02   auto_quote (inbox) X       9/9     EXTRA_STOP                   -                      -
H03   auto_quote (inbox) X       9/9     SPECIALTY_ITEM               -                      -
H04   auto_quote (auto_quote)    9/9     -                            -                      -
H05   auto_quote (inbox) X       9/9     PRICE_COMMITMENT             -                      -

fields correct : 44/45
flags caught   : 1/5  (missed 4)
false flags    : 0
route correct  : 1/5
quotes verbatim: 31/31
extract failed : 0
```

## report
```
report.html written, 17,240 bytes
script tags: 0
```
