import DATABASE
import os, sys, time
import mysql.connector as mariadb
import json

def executeQuery(query, commit=False, debug=False, quiet=False):
	mariadb_connection = mariadb.connect(
							user='root',
							password='password',
							database='decktracker')
	cursor = mariadb_connection.cursor()
	result=None
	try:
		cursor.execute(query)
		if commit: mariadb_connection.commit()
		else:
			result = cursor.fetchall()
			if len(result) == 0: result=None
			elif len(result) == 1: result=result[0]
	except:
		print(f"\n[ERROR] Failed Query: {query}\n")
		traceback.print_exc()
		sys.exit()
	mariadb_connection.close()
	query=query.replace('\t',' ').replace('\n',' ')
	if debug: print(f"executeQuery query {query} -> result {result}")
	elif not quiet: print(f"executeQuery query {query}")
	time.sleep(0.05)
	return result



'''
Have 1 table for static elements:

Have a different table for dynamic elements - up to 4, including health/attack.
- Find the base health/attack
- Find the base for the special abilities.
- Maybe do a double-pass on the file to find those 4 elements that changes.
  ["Damage"]: "28",
  ["Health"]: "180",
  Special1 (name and value)
  Special2 (name and value)
  Level
  Upgrades

[Pows][Trigger][Type] - EnteredRadius,Death,ChargedPowerActivated

[TechtreePatterns][Upgrades][SlotProperty]
[TechtreePatterns][Upgrades][PowerValue]
[TechtreePatterns][Evolutions][SlotProperty]
[TechtreePatterns][Evolutions][PowerValue]

'''

upgrade_evolve_map = {
	5 : 0,
	15 : 1,
	25 : 2,
	40 : 3,
	55 : 4,
	70 : 5
}

mypath = r'C:\Users\Remin\Documents\GitHub\sppd-data\cards'
onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

#squashed_cards_file = open('tbd.json',"w")
#squashed_cards_file.write('[\n')
modified_by_level = []
all_card_data = {}
evolve_card_data = {}
for filename in onlyfiles:
	split_fn = filename.split('_') #CardId_2251_StuartSciCard.json
	try:
		if len(split_fn) != 3 or \
		int(split_fn[1]) < 0: continue
		#int(split_fn[1]) not in DATABASE.DECK_MAP: continue
	except:
		print(f'unknown cardid: {split_fn[1]}')
		continue
	seen_just_now = []
	if 'json' not in filename: continue
	fh = open(os.path.join(mypath, filename),"r",encoding='utf8')
	json_string = fh.read()
	result = None
	try:
		result = json.loads(json_string)
	except:
		print(f'[ERROR] Unable to parse JSON in {filename}')
		sys.exit(1)
	if 'TechTree2' not in result or 'Id' not in result:
		print(f'skipping {filename}')
		continue
	ID = result['Id']
	all_card_data[ID]=[]
	evolve_card_data[ID]=[]
	base_health = "NULL"
	base_damage = "NULL"
	base_special1 = "NULL"
	base_special1_name = "NULL"
	base_special2 = "NULL"
	base_special2_name = "NULL"
	base_special3 = "NULL"
	base_special3_name = "NULL"
	base_level = 1
	base_upgrade = 1
	multiplier1 = 1
	if "Health" in result: base_health = float(result["Health"])
	if "Damage" in result: base_damage = float(result["Damage"])
	if 'TechtreePatterns' in result:
		TechtreePatterns = result['TechtreePatterns']
		if 'Upgrades' in TechtreePatterns:
			for elem in TechtreePatterns['Upgrades']:
				if 'SlotProperty' in elem and 'PowerValue' in elem:
					property = elem['SlotProperty']
					if property == 'MaxHealth' or property == 'Damage' or property == '': continue
					pval = elem['PowerValue']
					if pval == '': pval = 0
					if type(pval) != float: pval =float(pval)
					if base_special1_name == 'NULL' or base_special1_name == property:
						base_special1_name = property
						base_special1 = pval
						if base_special1_name == 'PowerSummonLevelAbs': base_special1+=1
					else:
						#print(f'base2_special name = {property}')
						base_special2_name = property
						base_special2 = pval
						if base_special2_name == 'PowerSummonLevelAbs': base_special2+=1
		if 'Evolutions' in TechtreePatterns:
			for elem in TechtreePatterns['Evolutions']:
				if 'SlotProperty' in elem and 'PowerValue' in elem:
					property = elem['SlotProperty']
					if property == 'MaxHealth' or property == 'Damage' or property == '': continue
					pval = elem['PowerValue']
					if pval == '': pval = 0
					if type(pval) != float: pval =float(pval)
					if base_special1_name == 'NULL' or base_special1_name == property:
						base_special1_name = property
						base_special1 = pval
						if base_special1_name == 'PowerSummonLevelAbs': base_special1+=1
					else:
						base_special2_name = property
						base_special2 = pval
						if base_special2_name == 'PowerSummonLevelAbs': base_special2+=1
	if ID == DATABASE.NAME_TO_ID["A.W.E.S.O.M.-O 4000"]:
		base_special2=4.0
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Chicken Coop"]:
		base_special2=4
		base_special2_name='PowerInterval'
	elif ID == DATABASE.NAME_TO_ID["Dark Mage Craig"]:
		base_special1=6
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Cyborg Kenny"]:
		base_special2=10
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Freeze Ray"]:
		base_special2=4
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Ice Sniper Wendy"]:
		base_special1=4.5
		base_special1_name='PowerRangeAbs'
		base_special2=4
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Kyle of the Drow Elves"]:
		base_special1=3
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Paladin Butters"]:
		base_special1=3
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Hermes Kenny"]:
		base_special1=4
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Mr. Hankey"]:
		base_special1=20
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Gunslinger Kyle"]:
		base_special3=4.5
		base_special3_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Mr. Slave Executioner"]:
		base_special3=3
		base_special3_name='PowerSummonAmount'
	elif ID == DATABASE.NAME_TO_ID["Poseidon Stan"]:
		base_special1=8
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Shieldmaiden Wendy"]:
		base_special1=4
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Power Bind"]:
		base_special2=40
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Space Pilot Bradley"]:
		base_special1=1.5
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Princess Kenny"]:
		base_special1=5
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Regeneration"]:
		base_special2=10
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Dragonslayer Red"]:
		base_special1=10
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Marine Craig"]:
		multiplier1=3
	elif ID == DATABASE.NAME_TO_ID["Alchemist Scott"]:
		multiplier1=2
	elif ID == DATABASE.NAME_TO_ID["Stan of Many Moons"]:
		multiplier1=2
	elif ID == DATABASE.NAME_TO_ID["Stan the Great"]:
		base_special2=5
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Swashbuckler Red"]:
		base_special1=10
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Youth Pastor Craig"]:
		base_special1=30
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Human Kite"]:
		base_special1=3
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Professor Chaos"]:
		base_special3=2
		base_special3_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Doctor Timothy"]:
		base_special2=4
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Captain Diabetes"]:
		base_special2=8
		base_special2_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Big Mesquite Murph"]:
		base_special1=1.3
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Sizzler Stuart"]:
		base_special1=3.5
		base_special1_name='PowerDurationAbs'
	elif ID == DATABASE.NAME_TO_ID["Wonder Tweek"]:
		base_special2=5
		base_special2_name='PowerDurationAbs'
	elif ID == 1650: # Turbo Space Grunt
		base_special1=3
		base_special1_name='PowerDurationAbs'
	elif ID == 1983: # Imp Tweek
		multiplier1=4
		base_special2=2
		base_special2_name='PowerDurationAbs'
	elif ID == 1728 or ID == 1647: # Subzero Titan
		base_special1=2
		base_special1_name='PowerDurationAbs'
	elif ID == 1658: # Beast Mode
		base_special1=50
		base_special1_name='PowerMaxHPGainAbs'
		base_special2=10
		base_special2_name='PowerAttackBoostAbs'
	elif ID == 2429: # Future Randy
		base_special2=3
		base_special2_name='PowerDurationAbs'
	elif ID == 1659: # Invincibility
		base_special1=4
		base_special1_name='PowerDurationAbs'
	elif ID == 2408: # Cyborg Tower
		base_special1=8
		base_special1_name='PowerDurationAbs'
	elif ID in DATABASE.IGNORE_LIST and DATABASE.IGNORE_LIST[ID][0] == 'Potted Plant':
		base_special1=3
		base_special1_name='PowerDurationAbs'
		base_special2=8
		base_special2_name='PowerTimeInterval'
	all_card_data[ID].append([base_level,base_upgrade,base_health,base_damage,base_special1*multiplier1,base_special1_name,base_special2,base_special2_name,base_special3,base_special3_name])
	evolve_card_data[ID]=[ [0,0,0,0] for i in range(6) ]
	if 'Evolve' in result['TechTree2']:
		for multi_slot in result['TechTree2']['Evolve']:
			if 'Slots' not in multi_slot: continue
			starlevel = multi_slot['StarLevel']
			for slot in multi_slot['Slots']:
				if 'property' in slot:
					property = slot['property']
					if property not in modified_by_level:
						modified_by_level.append(property)
				
					if property not in seen_just_now:
						seen_just_now.append(property)
					
					value = slot['value']
					if property == 'MaxHealth':
						evolve_card_data[ID][starlevel][0]+=value
					elif property == 'Damage':
						evolve_card_data[ID][starlevel][1]+=value
					elif property == base_special1_name:
						evolve_card_data[ID][starlevel][2]+=value
					elif property == base_special2_name:
						evolve_card_data[ID][starlevel][3]+=value
						
	if 'Slots' in result['TechTree2']:
		for slot in result['TechTree2']['Slots']:
			if 'property' in slot:
				property = slot['property']
				value = slot['value']
				x_num = slot['x']
				if property not in modified_by_level:
					modified_by_level.append(property)
				
				if property not in seen_just_now:
					seen_just_now.append(property)
				if property == 'MaxHealth':
					base_health+=value
				elif property == 'Damage':
					base_damage+=value
				elif property == base_special1_name:
					base_special1+=value
				elif property == base_special2_name:
					base_special2+=value
					
				base_upgrade+=1
				if x_num + 2 != base_upgrade:
					print(f'missing {base_upgrade} on {ID}')
					sys.exit()
					
				all_card_data[ID].append([base_level,base_upgrade,base_health,base_damage,base_special1*multiplier1,base_special1_name,base_special2,base_special2_name,base_special3,base_special3_name])
				if base_upgrade in upgrade_evolve_map.keys():
					base_level+=1
					offset = upgrade_evolve_map[base_upgrade]
					evolve_values = evolve_card_data[ID][offset]
					if base_health != 'NULL':
						base_health+=evolve_values[0]
					if base_damage != 'NULL':
						base_damage+=evolve_values[1]
					if base_special1_name != 'NULL':
						base_special1+=evolve_values[2]
					if base_special2_name != 'NULL':
						base_special2+=evolve_values[3]
					all_card_data[ID].append([base_level,base_upgrade,base_health,base_damage,base_special1*multiplier1,base_special1_name,base_special2,base_special2_name,base_special3,base_special3_name])
			elif base_special1_name in slot['type']:
				base_special1=1
				base_upgrade+=1
				all_card_data[ID].append([base_level,base_upgrade,base_health,base_damage,base_special1*multiplier1,base_special1_name,base_special2,base_special2_name,base_special3,base_special3_name])
			elif base_special2_name in slot['type']:
				base_special2=1
				base_upgrade+=1
				all_card_data[ID].append([base_level,base_upgrade,base_health,base_damage,base_special1*multiplier1,base_special1_name,base_special2,base_special2_name,base_special3,base_special3_name])
	if len(all_card_data[ID])==1:
		for evolve_values in evolve_card_data[ID]:
			base_level+=1
			if base_health != 'NULL':
				base_health+=evolve_values[0]
			if base_damage != 'NULL':
				base_damage+=evolve_values[1]
			if base_special1_name != 'NULL':
				base_special1+=evolve_values[2]
			if base_special2_name != 'NULL':
				base_special2+=evolve_values[3]
			all_card_data[ID].append([base_level,base_upgrade,base_health,base_damage,base_special1*multiplier1,base_special1_name,base_special2,base_special2_name,base_special3,base_special3_name])
	print(f'Completed {filename}')
	
#print(modified_by_level)
#New kid level	Experience needed	Health in total	Health in each bar	Attack / zap dmg	Shockwave damage
NK_MAP = [
	[1,10,450,150,7,75],
	[2,25,486,162,7,81],
	[3,50,524,175,7,87],
	[4,100,565,188,7,94],
	[5,200,610,203,7,102],
	[6,325,658,219,8,110],
	[7,500,710,237,9,118],
	[8,700,766,255,10,128],
	[9,850,827,276,11,138],
	[10,1250,892,297,12,149],
	[11,1900,963,321,14,161],
	[12,2250,1039,346,15,173],
	[13,2550,1121,374,17,187],
	[14,3000,1209,403,18,202],
	[15,3500,1305,435,20,218],
	[16,5000,1408,469,21,235],
	[17,7000,1519,506,23,253],
	[18,9000,1639,546,24,273],
	[19,12000,1768,589,26,295],
	[20,15000,1908,636,28,318],
	[21,20000,2059,686,30,343],
	[22,25000,2222,741,32,370],
	[23,30000,2397,799,34,400],
	[24,45000,2586,862,36,431],
	[25,'MAX',2791,930,38,465]
]
insert_str = []
for i in range(0,25):
	LEVEL,EXP,HEALTH,HEALTH_BAR,ATTACK,SHOCKWAVE = NK_MAP[i]
	insert_str.append(f"(1,{LEVEL},{LEVEL},{HEALTH},{ATTACK},{SHOCKWAVE},'PowerDamageAbs',NULL,NULL,NULL,NULL)")
if len(insert_str) != 0:
	insert_str = ','.join(x for x in insert_str)
	executeQuery(f"INSERT IGNORE INTO CARDS_DYNAMIC_STATS (CARDID,LEVEL,UPGRADE,HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2,SPECIAL3,STYPE3) VALUES {insert_str};", True,quiet=True)

for key in sorted(all_card_data.keys()):
	if key in DATABASE.DECK_MAP: print(f'In Progress... {DATABASE.DECK_MAP[key][0]}')
	else: print(f'In Progress... Unknown {key}')
	if key == 1: continue
	insert_str = []
	result = executeQuery(f"SELECT HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2 FROM CARDS_DYNAMIC_STATS WHERE CARDID = {key}",quiet=True)
	already_exists = result != None
	for elem in all_card_data[key]:
		base_level,base_upgrade,base_health,base_damage,base_special1,base_special1_name,base_special2,base_special2_name,base_special3,base_special3_name = elem
		if base_special1_name != 'NULL': base_special1_name = f"'{base_special1_name}'"
		if base_special2_name != 'NULL': base_special2_name = f"'{base_special2_name}'"
		if base_special3_name != 'NULL': base_special3_name = f"'{base_special3_name}'"
		if already_exists:
			result = executeQuery(f"SELECT HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2 FROM CARDS_DYNAMIC_STATS WHERE CARDID = {key} AND LEVEL = {base_level} AND UPGRADE = {base_upgrade}",quiet=True)
		if result != None and \
			(result[0] != base_health or \
			result[1] != base_damage or \
			(base_special1_name == result[3] and result[2] != base_special1) or \
			(base_special2_name == result[5] and result[4] != base_special2)):
			executeQuery(f"UPDATE CARDS_DYNAMIC_STATS SET HEALTH={base_health}, ATTACK={base_damage}, SPECIAL1={base_special1}, STYPE1='{base_special1_name}', SPECIAL2={base_special2}, STYPE2='{base_special2_name}' WHERE CARDID = {key} AND LEVEL = {base_level} AND UPGRADE = {base_upgrade}", True,quiet=True)
		else:
			insert_str.append(f"({key},{base_level},{base_upgrade},{base_health},{base_damage},{base_special1},{base_special1_name},{base_special2},{base_special2_name},{base_special3},{base_special3_name})")
	if len(insert_str) != 0:
		insert_str = ','.join(x for x in insert_str)
		executeQuery(f"INSERT IGNORE INTO CARDS_DYNAMIC_STATS (CARDID,LEVEL,UPGRADE,HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2,SPECIAL3,STYPE3) VALUES {insert_str};", True,quiet=True)


#for property in modified_by_level:
#	print(f'{property}')
print('\tComplete')
