import DATABASE
import os, sys, time
import mysql.connector as mariadb
import json
import traceback

mypath = r'C:\Users\Remin\Documents\GitHub\sppd-data\cards'

def find(elem,mask=False):
	if elem == None or elem == '':
		print(f'[WARNING] {elem} not found!')
		return None
	elem = elem.lower()
	path = r'C:\Users\Remin\Documents\GitHub\sppd-data\characters'
	#Find the Name of the file
	for root, dirs, files in os.walk(path):
		if elem in dirs:
			return os.path.join(root, elem + r'\hd\UnitData.json')
	print(f'[WARNING] {elem} not found!')
	return None
	
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
	
def getTBA(filename):
	TBA = -1
	PreAttackDelay = 0
	AttackRange = -1
	asset_name = ''
	fh = open(os.path.join(mypath, filename),"r",encoding='utf8')
	json_string = fh.read()
	result = None
	try:
		result = json.loads(json_string)
	except:
		print(f'[ERROR] Unable to parse JSON in {filename}')
		sys.exit(1)
	if 'TimeInBetweenAttacks' in result:
		TBA = result['TimeInBetweenAttacks']
	if 'Ingame' in result:
		asset_name = result['Ingame'].replace('PF','')
	if 'AttackRange' in result:
		AttackRange = result['AttackRange']
	if 'PreAttackDelay' in result:
		PreAttackDelay = result['PreAttackDelay']
	return TBA,AttackRange,PreAttackDelay,asset_name
	
def getStaticStuff(filename):
	CNAME=''
	COST=0
	ctype=None
	TYPE=None
	CHARTYPE=None
	THEME=-1
	RARITY=-1

	fh = open(os.path.join(mypath, filename),"r",encoding='utf8')
	json_string = fh.read()
	result = None
	try:
		result = json.loads(json_string)
	except:
		print(f'[ERROR] Unable to parse JSON in {filename}')
		sys.exit(1)
	if 'Rarity' in result:
		RARITY = result['Rarity']
	if 'NameKey' in result:
		CNAME = result['NameKey']
	if 'Theme' in result:
		THEME = result['Theme']
	if 'ManaCost' in result:
		COST = result['ManaCost']
	if 'Type' in result:
		TYPE = result['Type']
	if 'CharacterType' in result:
		CHARTYPE = result['CharacterType']
	#'ass','fight','range','tank','tower','spell'
	if TYPE == 'Spell': ctype = 'spell'
	elif CHARTYPE == 'Trap': ctype = 'spell'
	elif CHARTYPE == 'Assassin': ctype = 'ass'
	elif CHARTYPE == 'Melee': ctype = 'fight'
	elif CHARTYPE == 'Ranged': ctype = 'range'
	elif CHARTYPE == 'Tank': ctype = 'tank'
	elif CHARTYPE == 'Totem': ctype = 'tower'
	else:
		print(f"[ERROR] Unknown type {filename} - {TYPE} : {CHARTYPE}")
	return CNAME,COST,ctype,THEME,RARITY
	
def getAttackAnimation(filename):
	attack_animation = -1
	fh = open(filename,"r",encoding='utf8')
	json_string = fh.read()
	result = None
	try:
		result = json.loads(json_string)
	except:
		print(f'[ERROR] Unable to parse JSON in {filename}')
		sys.exit(1)
	if 'data' in result and\
		'animations' in result['data'] and\
		'animationItems' in result['data']['animations']:
		for elem in result['data']['animations']['animationItems']:
			if 'name' in elem and elem['name']=='Attacking':
				attack_animation = elem['duration']
				break
	return attack_animation

def getType(ctype):
	if ctype not in ['ass','fight','range','tank','tower','spell']:
		print(f'could not find type {ctype}')
		sys.exit(1)
	return ctype

def getTheme(ctheme):
	tmp_theme = None
	if ctheme == 'Adv':
		tmp_theme = 'Adventure'
	elif ctheme == 'Fan':
		tmp_theme = 'Fantasy'
	elif ctheme == 'Gen':
		tmp_theme = 'Neutral'
	elif ctheme == 'Mys':
		tmp_theme = 'Mystical'
	elif ctheme == 'Sci':
		tmp_theme = 'Sci-Fi'
	elif ctheme == 'Sup':
		tmp_theme = 'Superheroes'
	else:
		print(f'could not find theme {ctheme}')
		sys.exit(1)
	return tmp_theme

def getRarity(crar):
	tmp_rar = None
	if crar == 0:
		tmp_rar = 'Common'
	elif crar == 1:
		tmp_rar = 'Rare'
	elif crar == 2:
		tmp_rar = 'Epic'
	elif crar == 3:
		tmp_rar = 'Legendary'
	else:
		print(f'could not find rarity {crar}')
		sys.exit(1)
	return tmp_rar

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

onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
#squashed_cards_file = open('tbd.json',"w")
#squashed_cards_file.write('[\n')
all_cards_tba=[]
for filename in onlyfiles:
	split_fn = filename.split('_') #CardId_2251_StuartSciCard.json
	try:
		if len(split_fn) != 3 or \
		int(split_fn[1]) < 0: continue
		#(int(split_fn[1]) not in DATABASE.DECK_MAP and int(split_fn[1]) not in DATABASE.IGNORE_LIST): continue
	except:
		#print(f'unknown cardid: {split_fn[1]}')
		continue
	CARD_ID=int(split_fn[1])
		
	#Get the TimeInBetweenAttacks
	if 'json' not in filename: continue
	TBA,AttackRange,PreAttackDelay,asset_name = getTBA(filename)
	if TBA == -1 or asset_name == '':
		print(f'Unable to get TBA/Asset from {filename}')
		continue
	cname,cost,ctype,ctheme,crarity=getStaticStuff(filename)
	if ctype == None:
		print(f'Unable to Card Type from {filename}')
		continue
	asset_filename = find(asset_name)
	if asset_filename == None:
		print(f'Unable to find file for asset {asset_filename}')
		continue
	card_name = ''
	PVE='Y'
	#cost = 0
	#ctype = ''
	#ctheme = ''
	#crarity = ''
	if CARD_ID in DATABASE.DECK_MAP:
		PVE='N'
		card_name = DATABASE.DECK_MAP[CARD_ID][0]
		#cost = DATABASE.DECK_MAP[CARD_ID][1]
		#ctype=getType(DATABASE.DECK_MAP[CARD_ID][2])
		#ctheme=getTheme(DATABASE.DECK_MAP[CARD_ID][3])
		#crarity=getRarity(DATABASE.DECK_MAP[CARD_ID][4])
	elif CARD_ID in DATABASE.IGNORE_LIST:
		card_name = DATABASE.IGNORE_LIST[CARD_ID][0]
		#cost = DATABASE.IGNORE_LIST[CARD_ID][1]
		#ctype=getType(DATABASE.IGNORE_LIST[CARD_ID][2])
		#ctheme=getTheme(DATABASE.IGNORE_LIST[CARD_ID][3])
		#crarity=getRarity(DATABASE.IGNORE_LIST[CARD_ID][4])
		#ctype = getType(ctype)
		#ctheme = getTheme(ctheme)
		#crarity = getRarity(crarity)
	elif cname != '':
		card_name = cname
		#ctype = getType(ctype)
		#ctheme = getTheme(ctheme)
		#crarity = getRarity(crarity)
	else:
		print("Unknown CARD_ID {CARD_ID}")
		continue
	ctype = getType(ctype)
	ctheme = getTheme(ctheme)
	crarity = getRarity(crarity)
		
		
	units = 1
	if card_name == 'Chaos Hamsters': units = 2
	elif card_name == 'Visitors': units = 2
	elif card_name == 'Terrance and Phillip': units = 2
	elif card_name == 'Cow Stampede': units = 3
	elif card_name == 'Underpants Gnomes': units = 3
	elif card_name == 'Rat Swarm': units = 4
	elif card_name == 'Pigeon Gang': units = 5
	
	
	#Get health and attack
	health_array = []
	attack_array = []
	result = executeQuery(f'SELECT HEALTH,ATTACK FROM CARDS_DYNAMIC_STATS WHERE CARDID={CARD_ID} AND ((LEVEL=1 AND UPGRADE=1)\
	OR (LEVEL=1 AND UPGRADE=5)\
	OR (LEVEL=2 AND UPGRADE=5)\
	OR (LEVEL=2 AND UPGRADE=15)\
	OR (LEVEL=3 AND UPGRADE=15)\
	OR (LEVEL=3 AND UPGRADE=25)\
	OR (LEVEL=4 AND UPGRADE=25)\
	OR (LEVEL=4 AND UPGRADE=40)\
	OR (LEVEL=5 AND UPGRADE=40)\
	OR (LEVEL=5 AND UPGRADE=55)\
	OR (LEVEL=6 AND UPGRADE=55)\
	OR (LEVEL=6 AND UPGRADE=70)\
	OR (LEVEL=7 AND UPGRADE=70)\
	)',quiet=True)
	if type(result) == tuple:
		print(f'Error parsing {card_name} at {CARD_ID}')
		continue
	for row in result:
		health_array.append(row[0])
		attack_array.append(row[1])
	attack_animation = getAttackAnimation(asset_filename)
	full_tba = None
	if attack_array[0] == 0:
		full_tba = 0
	elif attack_animation == -1:
		#print(f'Unable to get attack animation from asset {asset_filename}')
		continue
	else:
		full_tba = TBA+attack_animation+PreAttackDelay
	#ID,NAME,COST,UNITS,TYPE,THEME,RARITY,KEYWORDS,TBA,RANGE,HB1 - HB7, AB1 - AB7
	all_cards_tba.append([CARD_ID,card_name,cost,PVE,units,ctype,ctheme,crarity,full_tba,AttackRange])
	all_cards_tba[-1].extend(health_array)
	all_cards_tba[-1].extend(attack_array)


insert_str = []
for elem in all_cards_tba:
	print_result = []
	for word in elem:
		if type(word) == str:
			if "'" in word: word = word.replace("'","''")
			print_result.append(f"'{word}'")
		else:
			print_result.append(f"{word}")
	print_result = ','.join(x for x in print_result)
	#print(print_result)
	insert_str.append(f'({print_result})')
insert_str = ','.join(x for x in insert_str)
executeQuery(f"INSERT INTO CARDS_STATS (ID,NAME,COST,PVE,UNITS,TYPE,THEME,RARITY,TBA,RANG,HB1,HM1,HB2,HM2,HB3,HM3,HB4,HM4,HB5,HM5,HB6,HM6,HB7,AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7) VALUES {insert_str};", True, quiet=True)
print('\tComplete')
