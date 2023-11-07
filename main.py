from modules.InfrastSim import Simulator
from modules.utils import write_csv, merge_groups
from modules.group import make_groups, groups, ops
from modules.resolver import resolve_internal
import time

preset_243 = {
  "Control Center": {
    "level": 5
  },
  "B103": {
    "type": "Power",
    "level": 3
  },
  "B203": {
    "type": "Power",
    "level": 3
  },
  "B303": {
    "type": "Power",
    "level": 3
  },
  "B101": {
    "type": "Trading",
    "level": 3
  },
  "B102": {
    "type": "Trading",
    "level": 3
  },
  "B201": {
    "type": "Manufacturing",
    "level": 3
  },
  "B202": {
    "type": "Manufacturing",
    "level": 3
  },
  "B301": {
    "type": "Manufacturing",
    "level": 3
  },
  "B302": {
    "type": "Manufacturing",
    "level": 3
  },
  "Dormitory 1": {
    "level": 5
  },
  "Dormitory 2": {
    "level": 5
  },
  "Dormitory 3": {
    "level": 5
  },
  "Dormitory 4": {
    "level": 5
  },
  "Reception": {
    "level": 3
  },
  "Crafting": {
    "level": 3
  },
  "Office": {
    "level": 3
  },
  "Training": {
    "level": 3
  }
}

start_time = time.time()
Simulator.load('./lib')
make_groups("/home/funny_ppt/src/InfrastSim")
print("组:", groups)
print()
print("干员:", ops)
print()
import json
with open('ops.json', 'w+', encoding='utf-8') as f:
  f.write(json.dumps(ops, ensure_ascii=False))

merged = merge_groups(ops, groups)
for grps in merged:
  grps_name = ','.join(grps)
  grp_ops = []
  for grp_name in grps:
    for name in groups[grp_name]:
      if ops[name] not in grp_ops:
        grp_ops.append(ops[name])
  write_csv(grps_name, resolve_internal(grp_ops, preset_243), encoding='gbk')
for group in ['贸易站', '制造站']:
    grp_ops = []
    for op_name in groups[group]:
      grp_ops.append(ops[op_name])
    write_csv(group, resolve_internal(grp_ops, preset_243, 5), encoding='gbk')

# write_csv('总表', resolve_internal(ops.values(), preset_243), encoding='gbk')

end_time = time.time()
run_time = end_time - start_time
print(f"程序运行时间：{run_time} 秒")