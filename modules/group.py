import os
import re
from .utils import Facility
ops = {}
groups = {}

def insert(key, value, dict:dict[str,list] = groups):
  if not dict.get(key):
    dict[key] = []
  dict[key].append(value)
  
def add_group(op:str, group:str):
  if not ops.get(op):
    ops[op] = {}
  insert('groups', group, ops[op])
  insert(group, op)

def make_groups(proj_dir: str):
  global ops
  global groups
  
  td_dir = os.path.join(proj_dir, 'InfrastSim', 'TimeDriven')
  
  
  global_props = {}
  simu_file = os.path.join(td_dir, 'Simulator.cs')
  with open(simu_file, encoding='utf-8') as f:
    pattern = r'\b(?:public\s+AggregateValue\s+(\w+))\s*=>\s*GetGlobalValue\("([^"]+)"\);'
    matches = re.findall(pattern, f.read())
    for match in matches:
      global_props[match[0]] = match[1]

  ops_dir = os.path.join(td_dir, 'Operators')
  op_files = [os.path.join(ops_dir, f) for f in os.listdir(ops_dir) if os.path.isfile(os.path.join(ops_dir, f))]
  namemap = {}
  
  name_pattern = r'public\s+override\s+string\s+Name\s*=>\s*"([^"]+)";'
  for op_file in op_files:
    with open(op_file, encoding='utf-8') as f:
      code = f.read()
      match = re.search(name_pattern, code)
      if match:
        namemap[op_file] = name = match.group(1)
        ops[name] = op = {'name': name}
      else:
        print("读取 {} 文件失败!".format(op_file))
        exit(1)
        
      if re.search('ManufacturingStation.*!IsTired', code, re.IGNORECASE):
        insert('positions', Facility.manufacturing, op)
      if re.search('manufacturing', code, re.IGNORECASE):
        insert(Facility.manufacturing, name)
      
      if re.search('TradingStation.*!IsTired', code, re.IGNORECASE):
        insert('positions', Facility.trading, op)
      if re.search('trading', code, re.IGNORECASE):
        insert(Facility.trading, name)
      
      if re.search('PowerStation.*!IsTired', code, re.IGNORECASE):
        insert('positions', Facility.power, op)
      if re.search('power', code, re.IGNORECASE):
        insert(Facility.power, name)
        
      if re.search('ControlCenter.*!IsTired', code, re.IGNORECASE):
        insert('positions', Facility.center, op)
      if re.search('center', code, re.IGNORECASE):
        insert(Facility.center, name)
        
      if re.search('Office.*!IsTired', code, re.IGNORECASE):
        insert('positions', Facility.office, op)
      if re.search('office', code, re.IGNORECASE):
        insert(Facility.office, name)
        
      if re.search('Facility is Dormitory', code, re.IGNORECASE):
        insert('positions', Facility.dorm, op)
      if re.search('dorm', code, re.IGNORECASE):
        insert(Facility.dorm, name)

      pattern = r'if\s*\(.*?(\w+)\.IsProduce(\w+)\(\)[\s\S]*?\)\s*{[\s\S]*?EfficiencyModifier\.SetValue\([\w\s,]*([\d.-]+)\)'
      matches = re.findall(pattern, code)
      for match in matches:
          #condition_variable = match[0]
          product = match[1]
          eff = float(match[2])
          if product == 'CombatRecord':
            insert('prefer_product', ('初级作战记录', eff), op)
          elif product == 'Gold':
            insert('prefer_product', ('赤金', eff), op)
          elif product == 'OriginStone':
            insert('prefer_product', ('源石碎片', eff), op)

      for prop, propCN in global_props.items():
        if re.search(prop, code):
          add_group(name, propCN)
        
      op_groups = []
      pattern = r'static\s+string\[\]\s+_groups(\d?)\s+=\s+{(.+?)};'
      matches = re.findall(pattern, code)
      for match in matches: # FIXME: 对于不同阶段下解锁组别的干员，重复添加了低进阶的组别
        level = match[0] if match[0] != '' else '0'
        op_groups.extend([group.strip(' "') for group in match[1].split(',')])
        #print(name, level, op_groups)
      for group in set(op_groups):
        add_group(name, group)
        
      pattern = r'static\s+int\[\]\s+_thresholds\s+=.*?{(.+?)};'
      matches = re.findall(pattern, code)
      for match in matches:
        thresholds = [int(th.strip(' ')) for th in match.split(',')]
        for threshold in thresholds:
          insert('thresholds', threshold, op)
      
      matches = re.findall('WorkingTime', code)
      if any(matches):
        op['warm_up'] = True
      
      # 所有字符串都是与该干员相关的组或干员
      matches = re.findall('".*?"', code)
      excludes = [name, 'control-center-extra', 'dorm-extra', '芬芳疗养beta', '泡泡']
      tmp_excludes = ['伊内丝', 'W'] # 这是因为没有被实现的干员而临时移除的
      excludes.extend(tmp_excludes)
      for match in set(map(lambda x: x.strip('"'), matches)):
        if match not in excludes:
          insert('relevant', match, op)
        
  # 提取 OperatorGroups.cs
  groups_file = os.path.join(td_dir, 'OperatorGroups.cs')
  with open(groups_file, encoding='utf-8') as f:
    pattern = r'public\s+static\s+readonly\s+HashSet<string>\s+(\w+)\s*=\s*new\(\)\s*{([^}]*)\};'

    match = re.search(pattern, f.read(), re.DOTALL)
    if match:
      group = match.group(1)
      hashset_content = match.group(2).strip()
      op_names = list(map(lambda x: x.strip(' "'), hashset_content.split(',')))
    else:
      print("读取 {} 文件失败!".format(groups_file))
      exit(1)
    for item in op_names:
      add_group(item, group)
      
  for op in ops.values():
    if op.get('relevant'):
      for str in op['relevant']:
        if str not in groups and str in ops:
          insert('relevant_ops', str, op)
        else:
          add_group(op['name'], str)
  for group_name, group in groups.items():
    groups[group_name] = list(set(group))
  for op in ops.values():
    if op.get('groups'):
      op['groups'] = list(set(op['groups']))
    if not op.get('positions'):
      op['positions'] = []