#!/usr/bin/python

import sys, json

obj = json.load(sys.stdin)
# Do something with 'myjson' object

times = []
letters = []

for i in obj["intervals"]: times.append(i)
for l in obj["letters"]: letters.append(l)



print 'Content-Type: application/html\n\n'




print json.dumps(len(letters))    # or "json.dump(result, sys.stdout)"