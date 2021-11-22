from src.overloaded_harbor import OverloadedHarbor
import json
from matplotlib import pyplot as plt


config = None
with open('config.json', 'r') as f:
    config = json.load(f)

oh = OverloadedHarbor(*config['parameters'].values())

table = {}

for j in range(1, 365):
    rt = []
    rc = []
    for i in range(config['num-simulations']):
        ap, ad, dd, dp = oh.simulate(j*24)
        result = []
        for s, t in ap.items():
            result.append(dp[s] - t)
        avg = sum(result)/len(result)
        rt.append(avg)
        rc.append(len(result))
        #print(f'Simulation {i + 1}: Total Ships = {len(result)}; AVG Waiting Time = {avg}') 

        table[j] = sum(rt)/len(rt)

plt.scatter(table.keys(), table.values())
plt.xlabel('Days of Simulation')
plt.ylabel('AVG Waiting Time')
plt.savefig('g.png')
plt.show()





