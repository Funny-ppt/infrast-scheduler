from enum import Enum
import csv
from .InfrastSim import Simulator

class Facility:
  center = '控制中枢'
  trading = '贸易站'
  manufacturing = '制造站'
  power = '发电站'
  office = '办公室'
  dorm = '宿舍'
  
def split_list(lst, size):
  return [lst[i:i+size] for i in range(0, len(lst), size)]

def index_to_room(i):
  return f'B{i / 3 + 1}0{i % 3 + 1}'

def get_expected_score(comb):
  total = len(comb) * (1 + len(comb) / 20) * 0.03 * 5
  for name, pos in comb:
    if pos == Facility.trading:
      total += 0.3 * 5
    elif pos == Facility.manufacturing:
      total += 0.25 * 6
    elif pos == Facility.power:
      total += 0.15 * 3
    elif pos == Facility.center:
      manu_count = 4
      trad_count = 2
      total += max(0.02 * manu_count * 6, 0.07 * trad_count * 5)
  return total

def parse_data(sim: Simulator):
  data = sim.get_data()
  
  pow_eff = data['drones-efficiency'] - 1
  manu_eff = sum([fac['operators-efficiency'] for fac in data['modifiable-facilities'] if fac and fac['type'] == 'Manufacturing'])
  trad_eff = sum([fac['operators-efficiency'] for fac in data['modifiable-facilities'] if fac and fac['type'] == 'Trading'])
  
  return {
    'pow_eff': pow_eff,
    'manu_eff': manu_eff,
    'trad_eff': trad_eff,
    'score': pow_eff * 3 + manu_eff * 6 + trad_eff * 5
  }

def op_to_str(op):
  props = [op['fac']]
  if op['fac'] == Facility.manufacturing:
    props.append(op['product'])
  if not (op['mood_low'] == 0 and op['mood_high'] == 24):
    props.append("心情{}-{}".format(op['mood_low'], op['mood_high']))
  return '{}({})'.format(op['name'], ', '.join(props))

def write_csv(path: str, data, encoding='utf-8'):
  if not path.endswith('.csv'):
    path += '.csv'
  with open(path, 'w+', encoding=encoding) as f:
    writer = csv.writer(f)
    header = ['组合', '制造站效率', '贸易站效率', '发电站效率', '制造站额外效率', '贸易站额外效率', '发电站额外效率']
    writer.writerow(header)

    for item in data:
        comb_rst = ' '.join(map(lambda op: op_to_str(op), item['comb']))
        
        eff = item['eff']
        extra_eff = item['extra_eff']
        manu_eff = eff.get('manu_eff', 0)
        trad_eff = eff.get('trad_eff', 0)
        power_eff = eff.get('power_eff', 0)
        extra_manu_eff = extra_eff.get('manu_eff', 0)
        extra_trad_eff = extra_eff.get('trad_eff', 0)
        extra_power_eff = extra_eff.get('power_eff', 0)
        row = [comb_rst, manu_eff, trad_eff, power_eff, extra_manu_eff, extra_trad_eff, extra_power_eff]
        writer.writerow(row)
        
def merge_groups(ops:dict, groups:dict):
  merged_groups = []
  vis = set()

  def dfs(ops:dict, op:str, merged_group:list):
    vis.add(op)
    op_groups = ops[op].get('groups')
    if op_groups:
      for group in op_groups:
        if group in ['异格']:
          continue # 异格你个辣鸡，别来污染套组build
        if group not in merged_group:
          merged_group.append(group)
          for neighbor_name in groups[group]:
            if neighbor_name not in vis:
              dfs(ops, neighbor_name, merged_group)

  for name in ops:
    if name not in vis:
      cur_group = []
      dfs(ops, name, cur_group)
      if any(cur_group): merged_groups.append(cur_group)
  return merged_groups