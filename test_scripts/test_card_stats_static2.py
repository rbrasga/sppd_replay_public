import DATABASE
import os, sys, time
import mysql.connector as mariadb
import json
import traceback

mypath = r'C:\Users\Remin\Documents\GitHub\sppd-data\cards'
VALID_TAGS = ['Adults','Adv','Character','Epic','Female','Human','Indians','Male','Melee','Parent','Kids','Legendary','Mys','Ranged','Holy','Rare','Sci','Spell','Common','Unholy','Assassin','HasMovementSounds','Pirates','AttackchangeImmune','AttractImmune','FreezeImmune','HealImmune','KillAbilityImmune','LifestealImmune','MAXHPchangeImmune','MindcontrolImmune','Object','PoisonImmune','PowerbindImmune','PurifyImmune','ResurrectImmune','ShieldImmune','SpeedchangeImmune','TeleportImmune','Totem','TransformImmune','Canadian','Kindergarteners','Fan','Animal','Gen','IgnoreDublicates','Cock','Alien','Tank','Disabled','HasAoeOnTarget','Flying','HasAoeOnUnit','Cowboys','Sup','AbilityImmune','SpellImmune','MovingObject','Trap','HasReviveAbility','isDarkAngelRed','Goth','isHumanKite2']

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
	
def getStaticData(filename):
	CARD_ID=-1
	NAME='NULL'
	RARITY='NULL'
	THEME='NULL'
	COST='NULL'
	TYPE='NULL'
	CHARTYPE='NULL'
	TAGS=[]
	RANG='NULL'
	TimeInBetweenAttacks='NULL'
	PreAttackDelay='NULL'
	HEALTH=0
	HLOSS='NULL'
	CASTAREA='NULL'
	AOE='NULL'
	ARADIUS='NULL'
	APERCENT='NULL'
	ACONE='NULL'
	TRADIUS='NULL'
	MARENA='NULL'
	CRADIUS='NULL'
	WEIGHT='NULL'
	KNOCKBACK='NULL'
	CREGEN='NULL'
	TVELOCITY='NULL'
	MVELOCITY='NULL'
	AGGRO='NULL'
	IMAGE='NULL'
	asset_name=''
	
	fh = open(os.path.join(mypath, filename),"r",encoding='utf8')
	json_string = fh.read()
	result = None
	try:
		result = json.loads(json_string)
	except:
		print(f'[ERROR] Unable to parse JSON in {filename}')
		return None
	
	if 'Id' in result:
		CARD_ID = result['Id']
	if 'NameKey' in result:
		NAME = result['NameKey']
	if 'Rarity' in result:
		RARITY = result['Rarity']
	if 'Theme' in result:
		THEME = result['Theme']
	if 'ManaCost' in result:
		COST = result['ManaCost']
	if 'Type' in result:
		TYPE = result['Type']
	if 'CharacterType' in result:
		CHARTYPE = result['CharacterType']
	if 'Tags' in result:
		TAGS = result['Tags']
	if 'AttackRange' in result:
		RANG = result['AttackRange']
		
	if 'TimeInBetweenAttacks' in result:
		TimeInBetweenAttacks = result['TimeInBetweenAttacks']
	if 'PreAttackDelay' in result:
		PreAttackDelay = result['PreAttackDelay']
	if 'Health' in result:
		HEALTH = result['Health']
	if 'HealthLoss' in result:
		HLOSS = float(result['HealthLoss'])
		if HLOSS > 0:
			HLOSS = round(float(HEALTH) / HLOSS,1)
	if 'CastArea' in result:
		CASTAREA = result['CastArea']
	if 'AOEAttackType' in result:
		AOE = 0 if result['AOEAttackType'] == 'No' else 1
	if 'AOERadius' in result:
		ARADIUS = result['AOERadius']
	if 'AOEDamagePercentage' in result:
		APERCENT = result['AOEDamagePercentage']
	if 'AOEAttackConeDegree' in result:
		ACONE = result['AOEAttackConeDegree']
	if 'Targeting' in result and 'Radius' in result['Targeting']:
		TRADIUS = result['Targeting']['Radius']
	if 'Requirements' in result and 'MinPVPArena' in result['Requirements']:
		MARENA = result['Requirements']['MinPVPArena']
	if 'ChargedPowerRadius' in result:
		CRADIUS = result['ChargedPowerRadius']
	if 'PhysicsProperties' in result and 'Weight' in result['PhysicsProperties']:
		WEIGHT = result['PhysicsProperties']['Weight']
	if 'KnockbackImpulse' in result:
		try:
			KNOCKBACK = round(float(result['KnockbackImpulse']),2)
		except: return None
	if 'ChargedPowerRegen' in result:
		if result['ChargedPowerRegen'] > 0:
			CREGEN = round(1/result['ChargedPowerRegen'],2)
	if 'TimeToReachMaxVelocity' in result:
		TVELOCITY = result['TimeToReachMaxVelocity']
	if 'MaxVelocity' in result:
		MVELOCITY = result['MaxVelocity']
	if 'AgroRangeMultiplier' in result:
		AGGRO = result['AgroRangeMultiplier']
	if 'Ingame' in result:
		asset_name = result['Ingame'].replace('PF','')
	if 'Image' in result:
		IMAGE = result['Image']
	elif CARD_ID == 1:
		IMAGE = "NewKid"
		
	if len(TAGS) == 0: TAGS = 'NULL'
	return [CARD_ID,NAME,RARITY,THEME,COST,TYPE,CHARTYPE,TAGS,RANG,TimeInBetweenAttacks,PreAttackDelay,HLOSS,CASTAREA,AOE,ARADIUS,APERCENT,ACONE,TRADIUS,MARENA,CRADIUS,WEIGHT,KNOCKBACK,CREGEN,TVELOCITY,MVELOCITY,AGGRO,asset_name,IMAGE]
	
def getAnimations(filename):
	attack_animation = -1
	charge_animation = -1
	charge_active = -1
	warcry_animation = -1
	deathwish_animation = -1
	source_radius = -1
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
		if 'sourceRadius' in result['data']:
			source_radius = result['data']['sourceRadius']
		for elem in result['data']['animations']['animationItems']:
			if 'name' not in elem : continue
			if elem['name']=='Attacking':
				attack_animation = elem['duration']
			elif elem['name']=='SuperPower':
				charge_animation = elem['duration'] 
				if 'triggers' in elem:
					for subelem in elem['triggers']:
						if 'name' not in subelem: continue
						if subelem['name'] == 'SuperPower':
							if 'time' not in subelem:
								print(filename)
								break
							charge_active = subelem['time']
							break
			elif elem['name']=='EnteringLevel' and 'triggers' in elem:
				for subelem in elem['triggers']:
					if 'name' not in subelem: continue
					if subelem['name'] == 'SpawnPower':
						if 'time' not in subelem:
							print(filename)
							break
						warcry_animation = subelem['time']
						break
			elif elem['name']=='Dying' and 'triggers' in elem:
				for subelem in elem['triggers']:
					if 'name' not in subelem: continue
					if subelem['name'] == 'DeathPower':
						if 'time' not in subelem:
							print(filename)
							break
						deathwish_animation = subelem['time']
						break
			
	return attack_animation,charge_animation,charge_active,warcry_animation,deathwish_animation,source_radius

onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
#squashed_cards_file = open('tbd.json',"w")
#squashed_cards_file.write('[\n')
all_castarea=[]
all_tags=[]
all_cards_static=[]
for filename in onlyfiles:
	split_fn = filename.split('_') #CardId_2251_StuartSciCard.json
	try:
		if len(split_fn) != 3 or \
		int(split_fn[1]) < 0: continue
		#(int(split_fn[1]) not in DATABASE.DECK_MAP and int(split_fn[1]) not in DATABASE.IGNORE_LIST): continue
		#if len(split_fn) != 3:
		#	test = int(split_fn[1])
	except:
		print(f'unknown cardid: {split_fn[1]}')
		continue
	#CARD_ID=int(split_fn[1])
	
	if 'json' not in filename: continue
	#Get the Static Data
	static_data = getStaticData(filename)
	if static_data == None: continue
	CARD_ID,NAME,RARITY,THEME,COST,TYPE,CHARTYPE,TAGS,RANG,TimeInBetweenAttacks,PreAttackDelay,HLOSS,CASTAREA,AOE,ARADIUS,APERCENT,ACONE,TRADIUS,MARENA,CRADIUS,WEIGHT,KNOCKBACK,CREGEN,TVELOCITY,MVELOCITY,AGGRO,asset_name,IMAGE = static_data
	if RARITY == 'NULL':
		print(f'RARITY does not exist {CARD_ID}')
		continue
	if NAME == 'NULL':
		print(f'NAME does not exist {CARD_ID}')
		continue
	if CASTAREA not in all_castarea: all_castarea.append(CASTAREA)
	if type(TAGS) != list:
		print(f'Tags are wrong {CARD_ID} {NAME}')
	else:
		NEW_TAGS = []
		for tag in TAGS:
			if tag not in all_tags: all_tags.append(tag)
			if tag in VALID_TAGS: NEW_TAGS.append(tag)
		TAGS=NEW_TAGS
				
	full_tba = 0
	attack_animation = 'NULL'
	CANIM = 'NULL'
	CACTIVE = 'NULL'
	WANIM = 'NULL'
	DANIM = 'NULL'
	SRADIUS = 'NULL'
	if asset_name == '':
		print(f'Unable to get Asset from {filename}')
	else:
		asset_filename = find(asset_name)
		if asset_filename == None:
			print(f'Unable to find file for asset {asset_filename}')
		else:
			attack_animation,charge_animation,charge_active,warcry_animation,deathwish_animation,source_radius = getAnimations(asset_filename)
			if attack_animation == -1:
				print(f'Unable to get attack animation from asset {asset_filename}')
				attack_animation = 'NULL'
			if charge_animation != -1: CANIM = charge_animation
			if charge_active != -1: CACTIVE = charge_active
			if warcry_animation != -1: WANIM = warcry_animation
			if deathwish_animation != -1: DANIM = deathwish_animation
			if source_radius != -1: SRADIUS = source_radius
	if attack_animation != 'NULL':
		full_tba += attack_animation
	if TimeInBetweenAttacks != 'NULL':
		full_tba += TimeInBetweenAttacks
	if PreAttackDelay != 'NULL':
		full_tba += PreAttackDelay
	
	
	units = 1
	if NAME == 'Chaos Hamsters': units = 2
	elif NAME == 'Visitors': units = 2
	elif NAME == 'Terrance and Phillip': units = 2
	elif NAME == 'Underpants Gnomes': units = 3
	elif NAME == 'Underpants gnomes mob': units = 3
	elif NAME == 'Rat Swarm': units = 4
	elif NAME == 'Pigeon Gang': units = 5
	if NAME == 'Hero': IMAGE = "NewKid"
	
	#CARD_ID,NAME,RARITY,THEME,COST,TYPE,CHARTYPE,TAGS,RANG,TBA,HLOSS,CASTAREA,AOE,ARADIUS,APERCENT,ACONE,TRADIUS,MARENA,CRADIUS,WEIGHT,KNOCKBACK,CREGEN,CANIM,CACTIVE,WANIM,DANIM,TVELOCITY,MVELOCITY,AGGRO,IMAGE
	all_cards_static.append([CARD_ID,NAME,RARITY,THEME,COST,TYPE,CHARTYPE,TAGS,RANG,full_tba,attack_animation,PreAttackDelay,TimeInBetweenAttacks,HLOSS,CASTAREA,AOE,ARADIUS,APERCENT,ACONE,TRADIUS,MARENA,CRADIUS,WEIGHT,KNOCKBACK,CREGEN,CANIM,CACTIVE,WANIM,DANIM,TVELOCITY,MVELOCITY,AGGRO,units,SRADIUS,IMAGE])
	
#print(all_tags)

insert_str = []
for elem in all_cards_static:
	print_result = []
	for word in elem:
		if type(word) == str:
			if word == 'NULL':
				print_result.append(f"{word}")
			else:
				if "'" in word: word = word.replace("'","''")
				print_result.append(f"'{word}'")
		elif type(word) == list:
			tmp_data = ','.join(x for x in word)
			print_result.append(f"'{tmp_data}'")
		else:
			print_result.append(f"{word}")
	print_result = ','.join(x for x in print_result)
	#print(print_result)
	insert_str.append(f'({print_result})')
	executeQuery(f"INSERT INTO CARDS_STATIC_STATS (ID,NAME,RARITY,THEME,COST,TYPE,CHARTYPE,TAGS,RANG,TBA,AttackAnimation,PreAttackDelay,TimeInBetweenAttacks,HLOSS,CASTAREA,AOE,ARADIUS,APERCENT,ACONE,TRADIUS,MARENA,CRADIUS,WEIGHT,KNOCKBACK,CREGEN,CANIM,CACTIVE,WANIM,DANIM,TVELOCITY,MVELOCITY,AGGRO,UNITS,SRADIUS,IMAGE) VALUES ({print_result});", True, quiet=True)
'''
insert_str = ','.join(x for x in insert_str)
executeQuery(f"INSERT INTO CARDS_STATIC_STATS (ID,NAME,RARITY,THEME,COST,TYPE,CHARTYPE,TAGS,RANG,TBA,HLOSS,CASTAREA,AOE,ARADIUS,APERCENT,ACONE,TRADIUS,MARENA,CRADIUS,WEIGHT,KNOCKBACK,CREGEN,CANIM,CACTIVE,WANIM,DANIM,TVELOCITY,MVELOCITY,AGGRO,UNITS,SRADIUS,IMAGE) VALUES {insert_str};", True, quiet=True)
'''
print('\tComplete')
