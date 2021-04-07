from collections import OrderedDict
import csv
import json
import pprint

x = '/projectnb/caad/meganmp/analysis/location_totals-sub.json'
#print(x)
#y = json.loads(x)

with open(x) as f:
  data = json.load(f)

data = dict(data)
data = OrderedDict(sorted(data.items(), key=lambda x: x[1], reverse=True))

first_n_values = list(data.items())[:100]


pprint.pprint(first_n_values)

with open('top100locations.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(first_n_values)


