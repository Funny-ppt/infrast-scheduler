from .utils import Facility as FacName
from .InfrastSim import Simulator

def resolve_internal(input_ops:list[dict[str, list]], preset, max_size=100) -> list:
  ops = [{'fac': pos, **op} for op in input_ops for pos in op['positions'] if not op.get('thresholds')]
  for op in input_ops:
    if op.get('thresholds'):
      high = low = 24
      for threshold in reversed(op['thresholds']):
        high = low
        low = threshold
        ops.extend([{'fac': pos, 'mood_high': high, 'mood_low': low, **op} for pos in op['positions']])
  
  global_prefer = { '赤金': 0, '初级作战记录': 0, '源石碎片': 0 }
  for op in ops:
    prefer = op.get('prefer_product')
    if prefer:
      for prod, eff in prefer:
        if op['fac'] == FacName.manufacturing:
          if eff > 0:
            op['product'] = prod
        elif op['fac'] == FacName.center:
          global_prefer[prod] += eff
  
  global_prefer = list(sorted(global_prefer.items(), key=lambda x: x[1], reverse=True))
  for op in ops:
    if not op.get('product'):
      op['product'] = global_prefer[0][0]
  
  return Simulator.enumerate_group({
    'preset': preset,
    'ops': ops,
    'max_size': max_size,
  })

### 已经废弃的纯python实现版本
###
# def resolve_group(group) -> list:
#   results = []
#   members = groups[group]
#   max_size = min(12, len(members))
  
#   member_pos = [(member, pos) for member in members for pos in positions[member]]
  
#   for size in range(2, max_size + 1):
#     for comb in combinations(member_pos, size):
#       if len(set([mem for mem, pos in comb])) < size:
#         continue
      
#       center = [mem for mem, pos in comb if pos == FacName.center]
#       manufacturing = split_list([mem for mem, pos in comb if pos == FacName.manufacturing], 3)
#       trading = split_list([mem for mem, pos in comb if pos == FacName.trading], 3)
#       power = [mem for mem, pos in comb if pos == FacName.power]
#       office = [mem for mem, pos in comb if pos == FacName.office]
      
#       sim = Simulator()
#       sim.set_facility_state(Facility.ControlCenter, {
#         'level': 5,
#         'operators': center
#       })
#       sim.set_facility_state(Facility.Office, {
#         'level': 3,
#         'operators': office
#       })
#       i = 9
#       for lst in trading:
#         sim.set_facility_state(i, {
#           'type': 'Trading',
#           'level': 3,
#           'operators': lst,
#           'strategy': 'gold'
#         })
#         i += 1
#       for op in power:
#         sim.set_facility_state(i, {
#           'type': 'Power',
#           'level': 3,
#           'operators': [op]
#         })
#         i += 1
#       best_res = None
#       for product in ['赤金', '源石碎片', '初级作战记录']:
#         j = i
#         for lst in manufacturing:
#           sim.set_facility_state(i, {
#             'type': 'Manufacturing',
#             'level': 3,
#             'operators': lst,
#             'product': product
#           })
#           j += 1
#         res = parse_data(sim)
#         if not best_res or res['manu_eff'] > best_res['manu_eff']:
#           best_res = res
#       if res['score'] >= get_expected_score(comb):
#         results.append({
#           'comb': comb,
#           'res': res
#         })
  
#   sim = Simulator()
#   print('调用GetData()次数: {}'.format(sim._id * 3))
  
#   sorted_res = sorted(results, key=lambda x: x['res']['score'], reverse=True)
#   return sorted_res