from src.overloaded_harbor import OverloadedHarbor
import json

config = None
with open('config.json', 'r') as f:
    config = json.load(f)

oh = OverloadedHarbor(*config['parameters'].values())
rt = []
rc = []
for i in range(config['num-simulations']):
    ap, ad, dd, dp = oh.simulate(config['num-days']*24)
    result = []
    for s, t in ap.items():
        result.append(dp[s] - t)
    avg = sum(result)/len(result)
    rt.append(avg)
    rc.append(len(result))
    print(f'Simulation {i + 1}: Total Ships = {len(result)}; AVG Waiting Time = {avg}') 

print(f'Final Time AVG: {sum(rt)/len(rt)}')
print(f'Final Ship Count AVG: {sum(rc)/len(rc)}')
