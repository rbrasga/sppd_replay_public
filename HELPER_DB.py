#DATABASE READ ONLY
'''
SELECT id FROM cards_static_stats WHERE tags LIKE '%Canadian%'

'Object'
'MovingObject'
'HasMovementSounds'

'Adults'
'Character'
'Goth'
'Female'
'Human'
'Indians'
'Male'
'Melee'
'Parent'
'Kids'
'Holy'
'Unholy'
'Pirates'
'Canadian'
'Kindergarteners'
'Animal'
'Cock'
'Alien'
'Disabled'
'Flying'
'Cowboys'
'Trap'
'HasReviveAbility'
'HasAoeOnTarget'
'HasAoeOnUnit'

'IgnoreDublicates'
'AbilityImmune'
'SpellImmune'
'AttackchangeImmune'
'AttractImmune'
'FreezeImmune'
'HealImmune'
'KillAbilityImmune'
'LifestealImmune'
'MAXHPchangeImmune'
'MindcontrolImmune'
'PoisonImmune'
'PowerbindImmune'
'PurifyImmune'
'ResurrectImmune'
'ShieldImmune'
'SpeedchangeImmune'
'TeleportImmune'
'TransformImmune'
'''
import mysql.connector as mariadb
import traceback
import time, sys
from decimal import *
import RESTFUL
import DATABASE
import LOCALIZATION

'''
Count active players since last month
SELECT Y.MMR, COUNT(DISTINCT X.USERID) FROM users_history X
	JOIN (SELECT DISTINCT MMR - (MMR % 1000) AS MMR FROM users_history) Y
WHERE X.MMR BETWEEN Y.MMR AND (Y.MMR + 1000) AND x.updated < 1693526400 and x.updated > 1693526400 - 30 * 24 * 3600 GROUP BY y.mmr;

modify current time variables to `SELECT UNIX_TIMESTAMP();`
'''

#Helper functions

def executeSanitize(query, name, debug=False):
	#Only allows SELECT
	result=None
	try:
		mariadb_connection = mariadb.connect(
								user='readonly',
								password='password',
								database='decktracker')
		cursor = mariadb_connection.cursor()
		name = "%" + name + "%"
		cursor.execute(query, { 'name': name })
		result = cursor.fetchall()
		if len(result) == 0: result=None
		elif len(result) == 1: result=result[0]
	except:
		print(f"[ERROR] Failed Query: {query}, where NAME = '{name}'")
		traceback.print_exc()
	finally:
		try: mariadb_connection.close()
		except: pass
	if debug: print(f"executeQuery query {query} -> result {result}")
	time.sleep(0.05)
	return result

def executeQuery(query, debug=False, multiple=False):
	#Only allows SELECT
	result=None
	try:
		mariadb_connection = mariadb.connect(
								user='readonly',
								password='password',
								database='decktracker')
		cursor = mariadb_connection.cursor()
		iterator = cursor.execute(query, multi=multiple)
		result = None
		if multiple:
			result = []
			for x in iterator:
				if x.with_rows:
					result.append(x.fetchall())
		else:
			result = cursor.fetchall()
		if len(result) == 0: result=None
		elif len(result) == 1: result=result[0]
	except:
		print(f"[ERROR] Failed Query: {query}")
		traceback.print_exc()
	finally:
		try: mariadb_connection.close()
		except: pass
	if debug: print(f"executeQuery query {query} -> result {result}")
	time.sleep(0.05)
	return result
	
def convertUpgrades(level,upgrades):
	min_upgrades,max_upgrades=DATABASE.WAL_MAP[level]
	cur_upgrades=min_upgrades+upgrades
	if cur_upgrades > max_upgrades: cur_upgrades = max_upgrades #Shouldn't be possible
	return f"{cur_upgrades}/{max_upgrades}"
	
def removeCharactersOutOfRange(word):
	char_list = [word[j] for j in range(len(word)) if ord(word[j]) in range(65536)]
	new_word=''
	for j in char_list:
		new_word=new_word+j
	return new_word

	
###CARDS

def findThemes(deck):
	themes=[]
	for id in deck:
		theme=getTheme(id)
		if theme not in themes and theme != "neu":
			themes.append(theme)
	themes.sort()
	while len(themes)<2:
		themes.append("neu")
	return themes
	
def findAvgCost(deck):
	costs=[]
	for id in deck:
		cost=getCost(id)
		if cost < 0: return -1
		costs.append(cost)
	avg_cost = 0
	if len(deck) > 0:
		avg_cost = round(float(sum(costs))/len(deck),1)
	return avg_cost
	
def getCardDetails(card_id):
	if card_id in DATABASE.DECK_MAP:
		NAME=DATABASE.DECK_MAP[card_id][0].upper()
		COST=DATABASE.DECK_MAP[card_id][1]
		TYPE=DATABASE.DECK_MAP[card_id][2]
		THEME=DATABASE.DECK_MAP[card_id][3]
		RARITY=DATABASE.DECK_MAP[card_id][4]
		KEYWORDS=""
		if len(DATABASE.DECK_MAP[card_id])>5:
			KEYWORDS=DATABASE.DECK_MAP[card_id][5]
			if len(DATABASE.DECK_MAP[card_id])>6:
				KEYWORDS+=","+DATABASE.DECK_MAP[card_id][6]
				if len(DATABASE.DECK_MAP[card_id])>7:
					KEYWORDS+=","+DATABASE.DECK_MAP[card_id][7]
		return [NAME, COST, TYPE, THEME, RARITY, KEYWORDS]
	result = executeQuery(f"SELECT NAME, COST, TYPE, THEME, RARITY, KEYWORDS from CARDS WHERE ID={card_id}")
	if result == None or len(result)<6: result=["Unknown",-1,'Unknown','Unknown','Unknown','Unknown']
	else: result=[result[0].upper(),result[1],result[2],result[3],result[4],result[5]]
	return result

def getAllCardIDs():
	all_card_ids=[]
	id_list = executeQuery(f"SELECT ID FROM CARDS")
	length=cursor.rowcount
	for id in id_list:
		test_result=type(id)
		tmp_id=-1
		if id == None:
			pass
		elif type(id) == int:
			pass
		else:
			tmp_id=id[0]
		all_card_ids.append(tmp_id)
	return all_card_ids

def getTheme(card_id):
	if card_id in DATABASE.DECK_MAP:
		return DATABASE.DECK_MAP[card_id][3]
	theme = executeQuery(f"SELECT THEME from CARDS WHERE ID={card_id}")
	if theme == None: theme="Unknown"
	else: theme=theme[0]
	return theme
	
def getCost(card_id):
	if card_id in DATABASE.DECK_MAP:
		return DATABASE.DECK_MAP[card_id][1]
	cost = executeQuery(f"SELECT COST from CARDS WHERE ID={card_id}")
	if cost == None: cost=-1
	else: cost=cost[0]
	return cost
	
def getCardType(card_id):
	if card_id in DATABASE.DECK_MAP:
		return DATABASE.DECK_MAP[card_id][2]
	card_type = executeQuery(f"SELECT TYPE from CARDS WHERE ID={card_id}")
	if card_type == None: card_type='fight'
	else: card_type=card_type[0]
	return card_type
	
def getCardName(card_id):
	if card_id in DATABASE.DECK_MAP:
		return DATABASE.DECK_MAP[card_id][0].upper()
	name = executeQuery(f"SELECT NAME from CARDS WHERE ID={card_id}")
	if name == None:
		name="Unknown"
		print(f"[Critical Error] {card_id} not found in database!")
	else: name=name[0].upper()
	return name
	
def getCardData(card_id):
	if card_id in DATABASE.DECK_MAP:
		name,cost,type,theme,rarity = DATABASE.DECK_MAP[card_id][:5]
		name = name.upper()
		return [name,cost,type,theme,rarity]
	result = executeQuery(f"SELECT NAME,COST,TYPE,THEME,RARITY from CARDS WHERE ID={card_id}")
	if result == None: return None
	name,cost,type,theme,rarity = [result[0],result[1],result[2],result[3],result[4]]
	name=name.upper()
	return [name,cost,type,theme,rarity]
	
def getCardDataAll(card_id):
	if card_id not in LOCALIZATION.ASSET: return None, None
	key = LOCALIZATION.ASSET[card_id]
	if type(key) == list:
		key = key[0]
	full_key = f'DF_NAME_{key}'
	if full_key not in LOCALIZATION.LOCAL: return None, None
	card_name = LOCALIZATION.LOCAL[full_key][0]
	if type(card_name) == str: card_name = card_name.upper()
	
	result = executeQuery(f"SELECT TAGS,RANG,TBA,AttackAnimation,PreAttackDelay,TimeInBetweenAttacks,HLOSS,CASTAREA,AOE,ARADIUS,APERCENT,ACONE,TRADIUS,MARENA,CRADIUS,\
		WEIGHT,KNOCKBACK,CREGEN,CANIM,CACTIVE,WANIM,DANIM,TVELOCITY,MVELOCITY,AGGRO,UNITS,COST,TYPE,CHARTYPE,THEME,RARITY\
		FROM cards_static_stats WHERE ID = {card_id}")
	if result == None: return None, None
	static_stats = [result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7],result[8],result[9],result[10],result[11],result[12],result[13],result[14],result[15],result[16],result[17],result[18],result[19],result[20],result[21],result[22],result[23],result[24],result[25]]
	#static_details = [result[23],result[24],result[25],result[26],result[27]]
	CHARTYPE = result[25]
	is_spell = CHARTYPE == None or CHARTYPE == 'Trap'
	
	TAGS,RANG,TBA,AttackAnimation,PreAttackDelay,TimeInBetweenAttacks,HLOSS,CASTAREA,AOE,ARADIUS,APERCENT,ACONE,TRADIUS,MARENA,CRADIUS,WEIGHT,KNOCKBACK,CREGEN,CANIM,CACTIVE,WANIM,DANIM,TVELOCITY,MVELOCITY,AGGRO,UNITS = static_stats
	charge_character=False
	long_response = "**Static Attributes**\n\n"
	if not is_spell:
		long_response += f'Time Between Attacks: {TBA}\n\n'
		long_response += f'\t-AttackAnimation: {AttackAnimation}\n\n'
		long_response += f'\t-PreAttackDelay: {PreAttackDelay}\n\n'
		long_response += f'\t-TimeInBetweenAttacks: {TimeInBetweenAttacks}\n\n'
		if UNITS != None and UNITS > 1:
			long_response += f'Units: {UNITS}\n\n'
		long_response += f'Range: {RANG}\n\n'
		if HLOSS != None and HLOSS != 0:
			long_response += f'Lifespan: {HLOSS} seconds\n\n'
	if AOE != None:
		AOE = int(AOE)
		if AOE != 0:
			long_response += f'AOE Radius: {ARADIUS}\n\n'
			if ACONE != None and ACONE != 0:
				if ACONE % 1 == 0: ACONE = int(ACONE)
				long_response += f'AOE Cone: {ACONE}°\n\n'
			if APERCENT != None:
				APERCENT = 100 * APERCENT
				if APERCENT % 1 == 0: APERCENT = int(APERCENT)
				long_response += f'AOE Percent: {APERCENT}%\n\n'
	if CREGEN != None:
		if CREGEN % 1 == 0: CREGEN = int(CREGEN)
		if CREGEN != 0:
			long_response += f'Charge Power Regen: {CREGEN} seconds\n\n'
			if CRADIUS != None:
				if CRADIUS % 1 == 0: CRADIUS = int(CRADIUS)
				if CRADIUS != 0:
					long_response += f'Charge Power Radius: {CRADIUS}\n\n'
			charge_character=True
	if CANIM != None:
		if CACTIVE != None:
			if CACTIVE % 1 == 0: CACTIVE = int(CACTIVE)
		if CANIM % 1 == 0: CANIM = int(CANIM)
		if CANIM != 0:
			if charge_character:
				long_response += f'Charge Entire Animation: {CANIM} seconds\n\n'
			else:
				long_response += f'Enrage Entire Animation: {CANIM} seconds\n\n'
		if CACTIVE != 0:
			if charge_character:
				long_response += f'Charge Activates During Animation: {CACTIVE} seconds\n\n'
			else:
				long_response += f'Enrage Activates During Animation: {CACTIVE} seconds\n\n'
	if WANIM != None:
		if WANIM % 1 == 0: WANIM = int(WANIM)
		if WANIM != 0:
			long_response += f'Warcry Animation: {WANIM} seconds\n\n'
	if DANIM != None:
		if DANIM % 1 == 0: DANIM = int(DANIM)
		if DANIM != 0:
			long_response += f'Deathwish Animation: {DANIM} seconds\n\n'
	if TVELOCITY != None and TVELOCITY != 0:
		long_response += f'Time to Max Velocity: {TVELOCITY}\n\n'
		if MVELOCITY != None and MVELOCITY != 0:
			long_response += f'Max Velocity: {MVELOCITY}\n\n'
	if AGGRO != None:
		if AGGRO % 1 == 0: AGGRO = int(AGGRO)
		if AGGRO != 0:
			long_response += f'Aggro Range Multiplier: {AGGRO}\n\n'
	if not is_spell and KNOCKBACK != None:
		if KNOCKBACK % 1 == 0: KNOCKBACK = int(KNOCKBACK)
		if KNOCKBACK != 0:
			long_response += f'Knockback: {KNOCKBACK}\n\n'
	if not is_spell and WEIGHT != None:
		if WEIGHT % 1 == 0: WEIGHT = int(WEIGHT)
		if WEIGHT != 0:
			long_response += f'Weight: {WEIGHT}\n\n'
	if TRADIUS != None and TRADIUS > 0:
		long_response += f'Targeting Radius: {TRADIUS}\n\n'
	long_response += f'Cast Area: {CASTAREA}\n\n'
	long_response += f'Unlocked Arena: {MARENA}\n\n'
	TAGS = ', '.join(str(x) for x in TAGS)
	long_response += f'Tags: {TAGS}\n\n'
	
	return card_name, long_response
	
	
	
	
	
def getCardsFromDeckID(deck_id):
	if deck_id == None: return None
	cards=[]
	card_ids = executeQuery(f"SELECT CARDID1,CARDID2,CARDID3,CARDID4,CARDID5,CARDID6,CARDID7,CARDID8,CARDID9,CARDID10,CARDID11,CARDID12 from DECKS_TWO WHERE ID={deck_id}")
	if card_ids == None: return cards
	if type(card_ids) == tuple and card_ids[0] != None:
		for i in range(12):
			actual_card_id = -1
			if card_ids[i] != None:
				actual_card_id=card_ids[i]
			cards.append(actual_card_id)
	return cards


###USERS
	
def isValidUserID(id):
	if id == "": return False
	USERID = executeQuery(f"SELECT USERID FROM USERS WHERE ID={id}")
	OPTOUT = executeQuery(f"SELECT OPTOUT FROM USER_LOGINS WHERE USERID = (SELECT USERID FROM USERS WHERE ID={id})")
	if type(OPTOUT) == tuple: OPTOUT = OPTOUT[0]
	return USERID != None and (OPTOUT == None or int(OPTOUT) == 0)
	
def getInGameUserIDfromUniqueUserID(user_id):
	result = executeQuery(f"SELECT USERID FROM USERS WHERE ID = {user_id}")
	ingame_user_id=None
	if result != None: ingame_user_id=result[0]
	return ingame_user_id
	
def getUniqueUserIDfromInGameUserID(user_id):
	result = executeQuery(f"SELECT ID FROM USERS WHERE USERID = '{user_id}'")
	unique_user_id=None
	if result != None: unique_user_id=result[0]
	return unique_user_id

def getUsersCollection(g_user, unique_user_id_override=None,access_level=0):
	user_collection={}
	unique_user_id=None
	if unique_user_id_override != None:
		unique_user_id=unique_user_id_override
		if access_level == -1:
			#Check if the target userid has opted out.
			result_optout = None
			if g_user == None:
				result_optout = executeQuery(f"SELECT OPTOUT FROM USER_LOGINS WHERE USERID = (SELECT USERID FROM USERS WHERE ID = {unique_user_id})")
			else:
				result_optout = executeQuery(f"SELECT OPTOUT FROM USER_LOGINS WHERE USERID = (SELECT USERID FROM USERS WHERE ID = {unique_user_id}) AND OKTAID != '{g_user.id}'")
			if result_optout != None:
				if type(result_optout) == tuple: result_optout = result_optout[0]
				OPTOUT=0
				if result_optout!=None: OPTOUT=int(result_optout)
				if OPTOUT==1: return None
	else:
		if g_user == None: return None
		user_id=getUserIDFromOktaID(g_user.id)
		if user_id == None: return None
		unique_user_id=getUniqueUserIDfromInGameUserID(user_id)
	if unique_user_id==None: return None #should never fail
	
	result = executeQuery(f"SELECT CARDID, LEVEL, UPGRADES FROM USER_COLLECTIONS WHERE USERID = {unique_user_id}")	
	if result == None: return user_collection
	elif type(result) == tuple: result=[result]
	for card_data in result:
		if card_data != None:
			card_id=card_data[0]
			level=card_data[1]
			upgrades=card_data[2]
			card_name=getCardName(card_id)
			user_collection[card_name]=[level,upgrades]
	return user_collection

def getUserName(user_id,platform=False):
	if platform:
		name = None
		plat = None
		result = executeQuery(f"SELECT NAME, PLATFORM FROM USERS WHERE USERID='{user_id}'")
		if type(result)==tuple:
			name=result[0]
			plat=result[1]
		if name != None and type(name) == str: name=name.upper()
		if plat != None and type(plat) == str: plat=plat.upper()
		return name, plat
	name = executeQuery(f"SELECT NAME FROM USERS WHERE USERID='{user_id}'")
	if type(name)==tuple: name=name[0]
	if name != None and type(name) == str: name=name.upper()
	return name
	
def getUserIDFromUniqueUserID(unique_user_id):
	userid = executeQuery(f"SELECT USERID FROM USERS WHERE ID={unique_user_id}")
	if userid != None: userid=userid[0]
	return userid
	
def getUserIDFromOktaID(okta_id):
	result = executeQuery(f"SELECT USERID, MAIN from USER_LOGINS WHERE OKTAID='{okta_id}'")
	if result == None: return None
	if type(result) == tuple: result=[result]
	USERID=None
	index = 0
	for row in result:
		user_id=row[0]
		primary=0
		if row[1] != None: primary=int(row[1])
		if index == 0 and user_id != None:
			USERID=user_id
		elif primary == 1:
			USERID=user_id
		index+=1
	return USERID
	
def getAccounts(g_user):
	accounts=[]
	if g_user == None: return accounts
	okta_id=g_user.id
	
	result = executeQuery(f"SELECT USERID, MAIN, OPTOUT from USER_LOGINS WHERE OKTAID='{okta_id}'")
	if result == None: return accounts
	if type(result) == tuple: result=[result]
	for row in result:
		user_id=row[0]
		primary=0
		if row[1] != None: primary=int(row[1])
		opt_out=0
		if row[2] != None: opt_out=int(row[2])
		name = executeQuery(f"SELECT NAME from USERS WHERE USERID='{user_id}'")
		if name == None: name = "Unknown..."
		accounts.append([name[0].upper(),primary==1,opt_out==1])
	#print(f'getAccounts: {accounts}')
	return accounts
	
def isPaidUser(g_user):
	if g_user == None: return False
	okta_id=g_user.id
	result = executeQuery(f"SELECT ID from USER_DONATED WHERE OKTAID='{okta_id}'")
	return result != None
	
def getPlayerNameLink(player_name):
	search_player_name=player_name.replace("'","''")
	unique_user_id = executeQuery(f"SELECT ID from USERS WHERE NAME='{search_player_name}'")
	if unique_user_id == None: return '/player'
	unique_user_id=unique_user_id[0]
	return f'/player/{unique_user_id}'

###TEAMS
def getPastNames(ingame_user_id, cur_name):
	past_names=[]
	result = executeQuery(f"SELECT NAME FROM USERS_NAMES_PAST WHERE USERID='{ingame_user_id}'")
	if result != None:
		for row in result:
			name = row
			if type(row) == tuple: name = row[0]
			if type(name) == str: name = name.upper()
			if name != cur_name: past_names.append(name)
	return past_names
	
def getPastTeams(ingame_user_id, cur_team):
	past_teams=[]
	result = executeQuery(f"SELECT NAME FROM TEAMS WHERE TEAMID IN (SELECT TEAMID FROM USERS_TEAMS_PAST WHERE USERID='{ingame_user_id}')")
	if result != None:
		for row in result:
			name = row
			if type(row) == tuple: name = row[0]
			if type(name) == str: name = name.upper()
			if name != cur_team: past_teams.append(name)
	return past_teams

def getUsersDeck(unique_user_id):
	result = executeQuery(f"SELECT DECKID FROM TEAM_MEMBERS WHERE USERID=(SELECT USERID FROM USERS WHERE ID = {unique_user_id})")
	deck=None
	theme=None
	if type(result) == tuple: result = result[0]
	if result == None: return deck, theme
	deck=getCardsFromDeckID(result)
	theme=findThemes(deck)
	theme=','.join(x for x in theme)
	return deck, theme

def getOneTeamMember(unique_user_id):
	ingame_user_id=getInGameUserIDfromUniqueUserID(unique_user_id)
	result = executeQuery(f"SELECT ROLE, JOINDATE, RANK, MMR, NKLEVEL, WINS_PVP, WINS_TW, WINS_CHLG, WINS_PVE, WINS_FF, WINS_FFP, WINS_PVPP, TW_TOKENS, DONATED_CUR, DONATED_ALL, TEAMID, DECKUPDATED, DECKID, MAXMMR, CHLG_CMP, CHLG_MAX_SCORE FROM TEAM_MEMBERS WHERE USERID='{ingame_user_id}'")
	deck=None
	theme=None
	if result != None:
		DECKID=result[17]
		if DECKID != None:
			deck=getCardsFromDeckID(DECKID)
			theme=findThemes(deck)
			theme=','.join(x for x in theme)
	else: return None, deck, theme
	role = result[0]
	joindate = result[1]
	rank = result[2]
	mmr = result[3]
	nklevel = result[4]
	wins_pvp = result[5]
	wins_tw = result[6]
	wins_chlg = result[7]
	wins_pve = result[8]
	wins_ff = result[9]
	wins_ffp = result[10]
	wins_pvpp = result[11]
	tw_tokens = result[12]
	donated_cur = result[13]
	donated_all = result[14]
	ingame_teamid = result[15]
	updated = result[16]
	max_mmr = result[18]
	chlg_runs = result[19]
	chlg_max_score = result[20]
	team_name=getTeamNameFromIngameTeamID(ingame_teamid)
	team_name_link=getTeamLinkFromInGameID(ingame_teamid)
	name,plat=getUserName(ingame_user_id,True)
	past_names=getPastNames(ingame_user_id, name)
	past_teams=getPastTeams(ingame_user_id, team_name)
	return [name,role,joindate,rank,mmr,nklevel,wins_pvp,wins_tw,wins_chlg,wins_pve,wins_ff,wins_ffp,wins_pvpp,donated_cur,donated_all,team_name,team_name_link,updated,max_mmr,chlg_runs,chlg_max_score,plat,past_names,past_teams], deck, theme

def getLastRefreshFromUniqueTeamID(unique_team_id):
	if not isValidTeamID(unique_team_id): return -1
	UPDATED = executeQuery(f"SELECT UPDATED FROM TEAMS_REPORT WHERE ID={unique_team_id}")
	if UPDATED == None: return -1 #Guaranteed to return a valid result, right? Yes.
	UPDATED=UPDATED[0]
	return UPDATED
	
def getAccessLevelTeam(g_user, unique_user_id, target_team_id=None):
	if g_user == None: return -1
	if g_user.id == '00u1ohryqc7QDSnq2357': return 1
	user_id=getUserIDFromOktaID(g_user.id)
	if user_id == None: return -1
	team_id=getInGameTeamIDFromUserID(user_id)
	if team_id == None: return -1
	if target_team_id == None:
		ingame_user_id=getInGameUserIDfromUniqueUserID(unique_user_id)
		this_team_id=getInGameTeamIDFromUserID(ingame_user_id)
	else:
		this_team_id=getInGameTeamID(target_team_id)
	#Are they on the same team?
	if this_team_id != team_id: return -1
	
	#get the role from the team
	ROLE = executeQuery(f"SELECT ROLE FROM TEAM_MEMBERS WHERE TEAMID={team_id} AND USERID='{user_id}'")	
	if ROLE == None: return -1 #Guaranteed to return a valid result, right?
	ROLE=ROLE[0]
	#Only leaders/co-leaders can modify, all other team members can only view.
	if ROLE == 'co_leader' or ROLE == 'leader': return 1
	return 0
	
def canRefreshTeam(g_user):
	if g_user == None: return False
	user_id=getUserIDFromOktaID(g_user.id)
	if user_id == None: return False
	team_id=getInGameTeamIDFromUserID(user_id)
	if team_id == None: return False
	
	#get the role from the team
	ROLE = executeQuery(f"SELECT ROLE FROM TEAM_MEMBERS WHERE TEAMID={team_id} AND USERID='{user_id}'")
	if ROLE == None: return False #Guaranteed to return a valid result, right?
	ROLE=ROLE[0]
	return True or ROLE == 'co_leader' or ROLE == 'leader'
	
def isValidTeamID(id):
	if id == None or id == "": return False
	TEAMID = executeQuery(f"SELECT TEAMID FROM TEAMS_REPORT WHERE ID={id}")	
	return TEAMID != None
	
def isValidMatch(id):
	if id == None or id == "": return False
	MATCHID = executeQuery(f"SELECT ID FROM USER_MATCHES WHERE ID={id}")	
	return MATCHID != None
	
def getChallengeName(id):
	if id == None or id == "": return "Challenge: Unknown..."
	NAME = executeQuery(f"SELECT NAME FROM EVENTS WHERE ID = (SELECT EVENTID FROM META_CHAL_REPORT WHERE ID={id})")
	if type(NAME) == tuple: NAME = NAME[0]
	return NAME
	
def getEventName(id):
	if id == None or id == "": return "Event: Unknown..."
	NAME = executeQuery(f"SELECT NAME FROM EVENTS WHERE ID = {id} AND TYPE = 5")
	if type(NAME) == tuple: NAME = NAME[0]
	return NAME

def getTeamFromUserID(user_id):
	TEAMID=getInGameTeamIDFromUserID(user_id)
	if TEAMID == None: return None
	
	ID = executeQuery(f"SELECT ID FROM TEAMS_REPORT WHERE TEAMID={TEAMID}")	
	if ID == None: return None
	ID=ID[0]
	return ID

def getInGameTeamIDFromUserID(user_id):
	TEAMID = executeQuery(f"SELECT TEAMID FROM TEAM_MEMBERS WHERE USERID='{user_id}'")
	if TEAMID == None: return None
	TEAMID=TEAMID[0]
	return TEAMID

def getInGameTeamID(team_id):
	if team_id == None or team_id == "": return None
	TEAMID = executeQuery(f"SELECT TEAMID from TEAMS_REPORT WHERE ID={team_id}")	
	if TEAMID != None: TEAMID=TEAMID[0]
	return TEAMID
	
def getInGameTeamIDFromName(team_name):
	clean_team_name=removeCharactersOutOfRange(team_name).replace("'","''").lower()
	TEAMID = executeQuery(f"SELECT TEAMID from TEAMS WHERE NAME='{clean_team_name}'")	
	if TEAMID != None: TEAMID=TEAMID[0]
	return TEAMID
	
def getTeamNameFromIngameTeamID(TEAMID):
	name = executeQuery(f"SELECT NAME from TEAMS WHERE TEAMID={TEAMID}")	
	if name == None: name="Unknown"
	else: name=name[0].upper()
	return name
	
def getTeamName(team_id):
	TEAMID=getInGameTeamID(team_id)
	if TEAMID == None: return "Unknown"
	name = getTeamNameFromIngameTeamID(TEAMID)
	return name
	
def getUniqueTeamIDFromInGameTeamID(ingame_teamid):
	if ingame_teamid == None: return None
	if type(ingame_teamid) == tuple: ingame_teamid=ingame_teamid[0]
	team_id = executeQuery(f"SELECT ID from TEAMS_REPORT WHERE TEAMID={ingame_teamid}")	
	if team_id != None: team_id=team_id[0]
	return team_id
	
def getTeamLinkFromInGameID(ingame_teamid):
	unique_team_id = getUniqueTeamIDFromInGameTeamID(ingame_teamid)
	if unique_team_id == None: return '/teams'
	return f'/teams/{unique_team_id}'

def getTeamNameLink(team_name):
	team_id=getInGameTeamIDFromName(team_name)
	if team_id == None: return '/teams'
	return getTeamLinkFromInGameID(team_id)
	
###Meta Report###

def getDistinctNamesFromMetaReport():
	names = executeQuery("SELECT DISTINCT NAME FROM META_REPORT ORDER BY NAME DESC")
	if type(names) == tuple: names=[names]
	if names == None: return ""
	names_list=[]
	for row in names:
		names_list.append(row[0])
	return names_list

def getCardsAndThemesByFilter(filter_rank_min = None, filter_mmr_min = None, filter_mmr_max = None):
	themes_dict={}
	cards_dict={}
	decks_dict={}
	set_of_decks=[]
	total_decks=0
	cost_map={}
	search="Last 1 day"
	search_radius=24*60*60 # Last 24 hours
	search_time=int(time.time())-search_radius
	
	deck_ids = None
	#All
	if filter_rank_min==None and filter_mmr_min==None and filter_mmr_max==None:
		deck_ids = executeQuery(f"SELECT DECKID, USERID from TEAM_MEMBERS WHERE UPDATED>={search_time}")
	elif filter_mmr_min!=None and filter_mmr_max!=None:
		deck_ids = executeQuery(f"SELECT DECKID, USERID from TEAM_MEMBERS WHERE MMR>={filter_mmr_min} AND MMR<={filter_mmr_max} AND UPDATED>={search_time}")
	elif filter_mmr_min!=None and filter_mmr_max==None:
		deck_ids = executeQuery(f"SELECT DECKID, USERID from TEAM_MEMBERS WHERE MMR>={filter_mmr_min} AND UPDATED>={search_time}")
	elif filter_rank_min!=None and filter_mmr_min==None and filter_mmr_max==None:
		deck_ids = executeQuery(f"SELECT DECKID, USERID from TEAM_MEMBERS WHERE RANK<={filter_rank_min} and RANK <> 0 AND UPDATED>={search_time}")
	else:
		print(f"Not supported, filter_rank_min: {filter_rank_min}, filter_mmr_min: {filter_mmr_min}, filter_mmr_max: {filter_mmr_max}")
	if type(deck_ids) == tuple:
		deck_ids=[deck_ids]
	if deck_ids == None: deck_ids=[]
	for deck_id in deck_ids:
		actual_deck_id=deck_id[0]
		if actual_deck_id == None:
			#print("Critical Error: Can't find Deck ID")
			continue
		cards=getCardsFromDeckID(actual_deck_id)
		set_of_decks.append(cards)
		for card in cards:
			if card not in cards_dict:
				cards_dict[card]=0
			cards_dict[card]+=1
		themes=findThemes(cards)
		themes=','.join(x for x in themes)
		if themes not in themes_dict:
			themes_dict[themes]=0
		themes_dict[themes]+=1
		avg_cost = findAvgCost(cards)
		if avg_cost > 0:
			value = "%.1f" % avg_cost
			if value not in cost_map:
				cost_map[value]=0
			cost_map[value]+=1
		total_decks+=1
	meta_decks=getMetaDecks(cards_dict, set_of_decks)
	return cards_dict, themes_dict, total_decks, meta_decks, cost_map

def needChallengeMetaReport():
	result = executeQuery("SELECT COUNT(*) >= 6 from USER_MATCHES WHERE MODE=6 AND TIME>(SELECT MAX(TIME) FROM META_CHAL_REPORT)")
	if type(result) == tuple: result = result[0]
	if result == None: return False
	return result == 1

def getChalCardsAndThemes():
	themes_dict={}
	cards_dict={}
	decks_dict={}
	set_of_decks=[]
	total_decks=0
	#MODE 6 -> Challenge Mode
	deck_ids = executeQuery("SELECT DECK2 from USER_MATCHES WHERE MODE=6 AND TIME>=(SELECT MAX(STARTTIME) FROM EVENTS WHERE TYPE=4) AND TIME<=(SELECT MAX(ENDTIME) FROM EVENTS WHERE TYPE=4)")
	if type(deck_ids) == tuple: deck_ids=[deck_ids]
	if deck_ids == None: deck_ids=[]
	for deck_id in deck_ids:
		actual_deck_id=deck_id[0]
		if actual_deck_id == None:
			#print("Critical Error: Can't find Deck ID")
			continue
		cards=getCardsFromDeckID(actual_deck_id)
		set_of_decks.append(cards)
		for card in cards:
			if card not in cards_dict:
				cards_dict[card]=0
			cards_dict[card]+=1
		themes=findThemes(cards)
		themes=','.join(x for x in themes)
		if themes not in themes_dict:
			themes_dict[themes]=0
		themes_dict[themes]+=1
		total_decks+=1
	meta_decks=getMetaDecks(cards_dict, set_of_decks)
	top_three_themes=[]
	for i in range(3):
		high_theme = None
		max_count = 0
		for key in themes_dict.keys():
			if key not in top_three_themes and themes_dict[key] > max_count:
				max_count = themes_dict[key]
				high_theme = key
		if high_theme != None:
			top_three_themes.append(high_theme)
	tmp_meta_decks={}
	for themes in top_three_themes:
		if themes in meta_decks.keys():
			tmp_meta_decks[themes]=meta_decks[themes]
	return cards_dict, themes_dict, total_decks, tmp_meta_decks
	
def getChalReportTotalDecks():
	total_decks = executeQuery("SELECT TOTALDECKS FROM META_CHAL_REPORT WHERE EVENTID = (SELECT ID FROM EVENTS WHERE TYPE=4 AND STARTTIME=(SELECT MAX(STARTTIME) FROM EVENTS WHERE TYPE=4))")
	if type(total_decks) == tuple: total_decks=total_decks[0]
	return total_decks

def getHighestPairedCard(card_name,set_of_decks):
	META_DECK_LEN=12
	filter_list=[]
	filter_list.append(card_name)
	while len(filter_list) < META_DECK_LEN:
		set_of_pairs={}
		for deck in set_of_decks:
			valid=True
			for card in filter_list:
				if card not in deck:
					valid=False
			if valid:
				for card in deck:
					if card not in filter_list:
						if card not in set_of_pairs:
							set_of_pairs[card]=0
						set_of_pairs[card]+=1
		max_card=""
		max_seen=0
		for card in set_of_pairs:
			tmp_max=set_of_pairs[card]
			if tmp_max>max_seen:
				max_seen=tmp_max
				max_card=card
		filter_list.append(max_card)
	return filter_list
	
def convertDeckNameToIDs(deck):
	deck_ids=[]
	for card in deck:
		if card == '': continue
		deck_ids.append(DATABASE.LOWER_NAME_TO_ID[card])
	return deck_ids
	
def getMetaDecks(cards_dict, set_of_decks):
	meta_decks={}
	if len(cards_dict) == 0 or len(set_of_decks) == 0: return meta_decks
	sorted_collection=[]
	for card in cards_dict.keys():
		sorted_collection.append([card, round((100*float(cards_dict[card])/len(set_of_decks)),2)])
		#print( getCardName(card)+ "| %.2f" % (100*float(cards_dict[card])/len(set_of_decks)))
	sorted_l = sorted(sorted_collection, key=lambda x: (x[1], x[0]), reverse=True)
	for line in sorted_l:
		percent = float(line[1])
		card_name=line[0]
		if percent > 4:
			meta_deck=getHighestPairedCard(card_name,set_of_decks)
			themes=findThemes(meta_deck)
			themes=','.join(x for x in themes)
			if themes not in meta_decks:
				meta_decks[themes]=meta_deck
	#print("\nMeta Decks:")
	#for theme in meta_decks:
	#	deck=meta_decks[theme]
	#	print(theme+"|"+','.join(getCardName(x) for x in deck))
	return meta_decks
	
def getCardsAndThemesByFilter_Report(NAME, search_radius=24*60*60):
	themes_dict={}
	cards_dict={}
	cost_map={}
	total_decks=0
	search="Last 1 day" #because we are combining reports
	search_time=int(time.time())-search_radius
	
	result = executeQuery(f"SELECT THEMESID,CARDSID,TOTALDECKS from META_REPORT WHERE TIME>={search_time} AND NAME='{NAME}' AND SEARCH='{search}'")
	if result == None: return cards_dict, themes_dict, total_decks
	if type(result) == tuple:
		result=[result]
	for row in result:
		THEMESID=row[0]
		CARDSID=row[1]
		TOTALDECKS=row[2]
		themes = executeQuery(f"SELECT THEMES, PERCENT from META_THEMES WHERE THEMESID={THEMESID}")
		if type(themes) == tuple: themes=[themes]
		for row_themes in themes:
			theme=row_themes[0]
			percent=row_themes[1]
			if theme not in themes_dict:
				themes_dict[theme]=0
			themes_dict[theme]+=int(TOTALDECKS*float(percent)/100)
			if int(TOTALDECKS*float(percent)/100) > TOTALDECKS:
				print(f"themes error {THEMESID}, {CARDSID}, {TOTALDECKS}")
				sys.exit()
		cards = executeQuery(f"SELECT CARDID, PERCENT from META_CARDS WHERE CARDSID={CARDSID}")
		if type(cards) == tuple: cards=[cards]
		for row_cards in cards:
			card=row_cards[0]
			percent=row_cards[1]
			if card not in cards_dict:
				cards_dict[card]=0
			cards_dict[card]+=int(TOTALDECKS*float(percent)/100)
			if int(TOTALDECKS*float(percent)/100) > TOTALDECKS:
				print(f"cards error {THEMESID}, {CARDSID}, {TOTALDECKS}")
				sys.exit()
		total_decks+=TOTALDECKS
	return cards_dict, themes_dict, total_decks
	
def findOldTeams():
	TwoDaysAgo = int(time.time()) - 3600 * 24 * 2
	old_teams = executeQuery(f"SELECT TEAMID from TEAMS_REPORT WHERE UPDATED < {TwoDaysAgo} AND RANK <= 2000 AND MEMBERS > 0")
	old_teams_list=[]
	if type(old_teams) == tuple: old_teams = [old_teams]
	if old_teams == None: old_teams = []
	for row in old_teams:
		old_teams_list.append(row[0])
	return old_teams_list
	
def getPlayersWithNull(limit=4000, arena=None):
	result=None
	if arena == None:
		result = executeQuery(f"SELECT USERID from TEAM_MEMBERS WHERE TEAMID <> 0 AND DECKUPDATED IS NULL LIMIT {limit};")
	else:
		min_mmr, max_mmr=DATABASE.ARENA_MAP[arena]
		if max_mmr==None:
			result = executeQuery(f"SELECT USERID from TEAM_MEMBERS WHERE TEAMID <> 0 AND MMR >= {min_mmr} AND DECKUPDATED IS NULL LIMIT {limit};")
		else:
			result = executeQuery(f"SELECT USERID from TEAM_MEMBERS WHERE TEAMID <> 0 AND MMR >= {min_mmr} AND MMR < {max_mmr} AND DECKUPDATED IS NULL LIMIT {limit};")
	if type(result) == tuple: result=[result]
	if result == None: result=[]
	return result
	
def getPlayersWithOldUpdated(limit=4000, arena=None):
	result=None
	if arena == None:
		result = executeQuery(f"SELECT USERID, MAX(DECKUPDATED) AS DECKUPDATED from TEAM_MEMBERS WHERE TEAMID <> 0 AND DECKUPDATED IS NOT NULL GROUP BY USERID ORDER BY DECKUPDATED LIMIT {limit};")
	else:
		min_mmr, max_mmr=DATABASE.ARENA_MAP[arena]
		if max_mmr==None:
			result = executeQuery(f"SELECT USERID, MAX(DECKUPDATED) AS DECKUPDATED from TEAM_MEMBERS WHERE TEAMID <> 0 AND USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE MMR >= {min_mmr}) AND DECKUPDATED IS NOT NULL GROUP BY USERID ORDER BY DECKUPDATED LIMIT {limit};")
		else:
			result = executeQuery(f"SELECT USERID, MAX(DECKUPDATED) AS DECKUPDATED from TEAM_MEMBERS WHERE TEAMID <> 0 AND USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE MMR >= {min_mmr} AND MMR < {max_mmr}) AND DECKUPDATED IS NOT NULL GROUP BY USERID ORDER BY DECKUPDATED LIMIT {limit};")
	if type(result) == tuple: result=[result]
	if result == None: result=[]
	return result
	
def getMetaCardsTableData(search, rank, limit):
	LIMIT=""
	if limit != None: LIMIT = f'LIMIT {limit}'
	#print(f"Cards Table Data, Rank: {rank}, Search: {search}")
	result=None
	if search == "Last 1 day":
		result = executeQuery(f"SELECT CARDSID, TIME, TOTALDECKS from META_REPORT WHERE SEARCH='{search}' AND NAME='{rank}' AND TIME IN (select MAX(TIME) from META_REPORT WHERE SEARCH='{search}' AND NAME='{rank}')")
	else:
		result = executeQuery(f"SELECT CARDSID, TIME, TOTALDECKS from META_REPORT WHERE SEARCH='{search}' AND NAME='{rank}'")
	updated=None
	total_decks=0
	if result != None:
		if len(result) != 3: result = result[0]
		cards_id = result[0]
		updated = result[1]
		total_decks = result[2]
		result = executeQuery(f"SELECT CARDID, PERCENT from META_CARDS WHERE CARDSID={cards_id} ORDER BY PERCENT DESC {LIMIT}")
		if type(result) == tuple: result=[result]
	return result, updated, total_decks
	
def getAllCardsTableData():
	result = executeQuery(f"SELECT ID FROM CARDS")
	return result
	
def getMetaCardstatsTableData():
	#print("Cardstats Table Data")
	result = executeQuery("SELECT ID,NAME,COST,UNITS,TYPE,THEME,RARITY,TBA,RANG,AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7 from CARDS_STATS")
	return result
	
def getMetaCardDetailsTableData(card_id):
	if card_id == None or card_id == '': return None
	#print("Cardstats Table Data")
	result = executeQuery(f"SELECT ID,NAME,COST,UNITS,TYPE,THEME,RARITY,TBA,RANG,\
							HB1,HM1,HB2,HM2,HB3,HM3,HB4,HM4,HB5,HM5,HB6,HM6,HB7,\
							AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7\
							FROM CARDS_STATS WHERE ID = {card_id}")
	return result
	
def getMetaCardDetailsTableData_multiple(card_ids):
	if card_ids == None or card_ids == '' or len(card_ids) == 0: return None
	#print("Cardstats Table Data")
	card_ids = ','.join(str(x) for x in card_ids)
	result = executeQuery(f"SELECT ID,NAME,COST,UNITS,TYPE,THEME,RARITY,TBA,RANG,\
							HB1,HM1,HB2,HM2,HB3,HM3,HB4,HM4,HB5,HM5,HB6,HM6,HB7,\
							AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7\
							FROM CARDS_STATS WHERE ID IN ({card_ids})")
	if type(result) == tuple: result = [result]
	return result
	
def getMetaCardFullDetailsTableData(card_id):
	if card_id == None or card_id == '': return None
	result = executeQuery(f"SELECT LEVEL,UPGRADE,HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2 FROM CARDS_DYNAMIC_STATS WHERE CARDID = {card_id}")
	return result
	
def getMetaCardFullDetailsTableData_multiple(card_ids):
	if card_ids == None or card_ids == '' or len(card_ids) == 0: return None
	card_ids = ','.join(str(x) for x in card_ids)
	result = executeQuery(f"SELECT CARDID,LEVEL,UPGRADE,HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2 FROM CARDS_DYNAMIC_STATS WHERE CARDID in ({card_ids})")
	return result
	
def getWinRateCardsTableData(card_id):
	if card_id == None or card_id == '': return None
	#print("Cardstats Table Data")
	result = executeQuery(f"SELECT CARDID2,WIN,DRAW,LOSE\
							FROM WINRATE_CARDS WHERE CARDID1 = {card_id}")
	return result
	
def getMetaChalCardsTableData(chal_id):
	#print(f"Cards Table Data, chal_id: {chal_id}")
	result = executeQuery(f"SELECT CARDSID, TIME, TOTALDECKS from META_CHAL_REPORT WHERE ID={chal_id}")
	updated=None
	total_decks=0
	if result != None:
		cards_id = result[0]
		updated = result[1]
		total_decks = result[2]
		result = executeQuery(f"SELECT CARDID, PERCENT from META_CARDS WHERE CARDSID={cards_id} ORDER BY PERCENT DESC")
		if type(result) == tuple: result=[result]
	return result, updated, total_decks

# For every team within that league with team war upgrades
# - Get their average win rate
# - Attribute that to their choices
# { Cardid1: [112.2,111.1,110.9,etc] }
# The build out the table:
# Choice 1 | avg 1 | Choice 2 | avg 2
# [[2443]] | avg([112.2,111.1,110.9,etc]) | ...
def getWinRateTVTByCard(eventid,league):
	TROPHIES = [0,None]
	if league == 'gold': TROPHIES=[3500,None]
	elif league == 'silver': TROPHIES=[1500,3500]
	elif league == 'bronze': TROPHIES=[500,1500]
	T_SEARCH = f"TROPHIES >= {TROPHIES[0]}"
	if TROPHIES[1] != None:
		T_SEARCH+=f" AND TROPHIES < {TROPHIES[1]}"
	result = executeQuery(f"SELECT x.CARDID, AVG(y.SCORE/y.RUNS) FROM teamwar_upgrade_cards X\
		JOIN teamwar_bracket y\
		JOIN teams z\
		WHERE y.RUNS > 0\
			AND x.updated > (SELECT STARTTIME + 48 * 3600 FROM EVENTS WHERE TYPE = 5 AND ID = {eventid})\
			AND x.updated < (SELECT ENDTIME FROM EVENTS WHERE TYPE = 5 AND ID = {eventid})\
			AND x.TEAMID = z.TEAMID AND y.TEAMNAME = z.NAME\
			AND x.TEAMID IN (SELECT TEAMID FROM TEAMS_REPORT WHERE {T_SEARCH})\
		GROUP BY CARDID")
	count_tracker = {}
	if result != None:
		for row in result:
			CARDID = row[0]
			AVG = row[1]
			count_tracker[CARDID] = AVG
	FINAL_RESULT = []
	result = executeQuery(f"SELECT CARDID1, CARDID2 FROM TEAMWAR_PAIRS WHERE PAIRID IN (SELECT PAIRID FROM TEAMWAR_CARDS WHERE TIME IN\
		( SELECT TIME FROM TEAMWAR_CARDS WHERE TIME > (SELECT STARTTIME FROM EVENTS WHERE TYPE = 5 AND ID = {eventid}) \
		AND TIME < (SELECT STARTTIME + 96 * 3600 FROM EVENTS WHERE TYPE = 5 AND ID = {eventid}) ) )")
	if type(result) == tuple: result=[result]
	for row in result:
		card1=row[0]
		card2=row[1]
		avg1 = 0
		avg2 = 0
		if card1 in count_tracker:
			avg1 = count_tracker[card1]
		if card2 in count_tracker:
			avg2 = count_tracker[card2]
		FINAL_RESULT.append([card1,avg1,card2,avg2])
	return FINAL_RESULT
	
def getMetaTWCardsTableData(eventid,league):
	TROPHIES = [0,None]
	if league == 'gold': TROPHIES=[3500,None]
	elif league == 'silver': TROPHIES=[1500,3500]
	elif league == 'bronze': TROPHIES=[500,1500]
	T_SEARCH = f"TROPHIES >= {TROPHIES[0]}"
	if TROPHIES[1] != None:
		T_SEARCH+=f" AND TROPHIES < {TROPHIES[1]}"
	#print(f"META TW Table Data, eventid: {eventid}")
	total_decks = executeQuery(f"SELECT COUNT(DISTINCT TEAMID) AS TOTAL FROM teamwar_upgrade_cards\
		WHERE updated > (SELECT STARTTIME + 48 * 3600 FROM EVENTS WHERE TYPE = 5 AND ID = {eventid})\
		AND TEAMID IN (SELECT TEAMID FROM TEAMS_REPORT WHERE {T_SEARCH})")
	if type(total_decks) == tuple: total_decks = total_decks[0]
	result = executeQuery(f"SELECT CARDID, COUNT(DISTINCT TEAMID) AS CHOICE FROM teamwar_upgrade_cards\
		WHERE updated > (SELECT STARTTIME + 48 * 3600 FROM EVENTS WHERE TYPE = 5 AND ID = {eventid})\
		AND TEAMID IN (SELECT TEAMID FROM TEAMS_REPORT WHERE {T_SEARCH})\
		GROUP BY CARDID")
	if type(result) == tuple: result = [result]
	count_tracker = {}
	if result != None:
		for row in result:
			CARDID = row[0]
			COUNT = row[1]
			count_tracker[CARDID] = COUNT
	FINAL_RESULT = []
	result = executeQuery(f"SELECT CARDID1, CARDID2 FROM TEAMWAR_PAIRS WHERE PAIRID IN (SELECT PAIRID FROM TEAMWAR_CARDS WHERE TIME IN\
		( SELECT TIME FROM TEAMWAR_CARDS WHERE TIME > (SELECT STARTTIME FROM EVENTS WHERE TYPE = 5 AND ID = {eventid}) \
		AND TIME < (SELECT STARTTIME + 96 * 3600 FROM EVENTS WHERE TYPE = 5 AND ID = {eventid}) ) )")
	if type(result) == tuple: result=[result]
	for row in result:
		card1=row[0]
		card2=row[1]
		count1 = 0
		count2 = 0
		if card1 in count_tracker:
			count1 = count_tracker[card1]
		if card2 in count_tracker:
			count2 = count_tracker[card2]
		FINAL_RESULT.append([card1,count1,card2,count2])
	return FINAL_RESULT, total_decks
	
def getMetaThemesTableData(search, rank):
	#print(f"Themes Table Data, Rank: {rank}, Search: {search}")
	result=None
	if search == "Last 1 day":
		result = executeQuery(f"SELECT THEMESID, TIME, TOTALDECKS from META_REPORT WHERE SEARCH='{search}' AND NAME='{rank}' AND TIME IN (select MAX(TIME) from META_REPORT WHERE SEARCH='{search}' AND NAME='{rank}')")
	else:
		result = executeQuery(f"SELECT THEMESID, TIME, TOTALDECKS from META_REPORT WHERE SEARCH='{search}' AND NAME='{rank}'")
	updated=None
	total_decks=0
	if result != None:
		themes_id = result[0]
		updated = result[1]
		total_decks = result[2]
		result = executeQuery(f"SELECT THEMES, PERCENT from META_THEMES WHERE THEMESID={themes_id} ORDER BY PERCENT DESC")
		if type(result) == tuple: result=[result]
	return result, updated, total_decks
	
def getMetaDecksData(rank):
	#print(f"Decks Data, Rank: {rank}")
	search = "Last 1 day"
	result = executeQuery(f"SELECT THEMESID, TIME, TOTALDECKS, COSTID from META_REPORT WHERE SEARCH='{search}' AND NAME='{rank}' AND TIME IN (select MAX(TIME) from META_REPORT WHERE SEARCH='{search}' AND NAME='{rank}')")
	updated=None
	meta_decks=None
	total_decks=0
	cost_data=None
	if result != None:
		themes_id = result[0]
		updated = result[1]
		total_decks = result[2]
		costid = result[3]
		result = executeQuery(f"SELECT THEMES, PERCENT, DECKID from META_THEMES WHERE THEMESID={themes_id} ORDER BY PERCENT DESC")
		if type(result) == tuple: result=[result]
		if result != None:
			result_two = executeQuery(f"SELECT ID,CARDID1,CARDID2,CARDID3,CARDID4,CARDID5,CARDID6,CARDID7,CARDID8,CARDID9,CARDID10,CARDID11,CARDID12 from DECKS_TWO WHERE ID IN (SELECT DECKID from META_THEMES WHERE THEMESID={themes_id})")
			if type(result_two) == tuple: result_two = [result_two]
			if result_two != None:
				meta_decks={}
				for elem in result_two:
					deckid = elem[0]
					meta_decks[deckid]=[]
					for i in range(1,13):
						meta_decks[deckid].append(elem[i])
		if costid != None:
			cost_data = executeQuery(f"SELECT COST, TOTAL from META_COST WHERE COSTID={costid}")
	return result, updated, total_decks, meta_decks, cost_data
	
def getMetaChalDecksData(chal_id):
	result = executeQuery(f"SELECT THEMESID from META_CHAL_REPORT WHERE ID={chal_id}")
	meta_decks=None
	if result != None:
		themes_id = result[0]
		result = executeQuery(f"SELECT THEMES, PERCENT, DECKID from META_THEMES WHERE THEMESID={themes_id} ORDER BY PERCENT DESC")
		if type(result) == tuple: result=[result]
		if result != None:
			result_two = executeQuery(f"SELECT ID,CARDID1,CARDID2,CARDID3,CARDID4,CARDID5,CARDID6,CARDID7,CARDID8,CARDID9,CARDID10,CARDID11,CARDID12 from DECKS_TWO WHERE ID IN (SELECT DECKID from META_THEMES WHERE THEMESID={themes_id})")
			if type(result_two) == tuple: result_two = [result_two]
			if result_two != None:
				meta_decks={}
				for elem in result_two:
					deckid = elem[0]
					meta_decks[deckid]=[]
					for i in range(1,13):
						meta_decks[deckid].append(elem[i])
	return result, meta_decks
	
def getTeamDetailsTableData(unique_team_id,access_level=-1):
	#print(f"Team Details Table Data, ingame_team_id {ingame_team_id}")
	collection_details_map={}
	if unique_team_id == None: return None,collection_details_map
	team_table_data = executeQuery(f"SELECT y.ID, y.NAME, y.PLATFORM, x.ROLE, x.MMR, x.NKLEVEL, x.DONATED_CUR, x.JOINDATE FROM TEAM_MEMBERS x\
		JOIN USERS y\
	WHERE x.TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) AND x.USERID = y.USERID ORDER BY x.MMR DESC")
	if type(team_table_data) == tuple: team_table_data=[team_table_data]
	if access_level != -1:
		result = executeQuery(f"SELECT USERID, COUNT(*) FROM USER_COLLECTIONS WHERE USERID IN (SELECT ID FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))) GROUP BY USERID")
		if type(result) == tuple: result=[result]
		if result != None:
			for row in result:
				ID=row[0]
				COUNT=row[1]
				collection_details_map[ID]=COUNT
	return team_table_data,collection_details_map
	
def getMyMatchesTableData(g_user):
	oppname_map={}
	oppteam_map={}
	if g_user == None:
		return None,oppname_map,oppteam_map
	USERID = getUserIDFromOktaID(g_user.id)
	mymatches_table_data = executeQuery(f"SELECT ID, TIME, USERID2, NK2, TEAM2, MODE, RESULT1, SCORE1, SCORE2, MMR2 FROM USER_MATCHES WHERE USERID1='{USERID}' OR USERID2='{USERID}' ORDER BY TIME DESC")
	if type(mymatches_table_data) == tuple: mymatches_table_data=[mymatches_table_data]
	if mymatches_table_data == None:
		return None,oppname_map,oppteam_map
	#Grab Opponent's User Names
	result = executeQuery(f"SELECT USERID, NAME, ID FROM USERS WHERE USERID IN (SELECT USERID2 FROM USER_MATCHES WHERE USERID1='{USERID}' OR USERID2='{USERID}')")
	if type(result) == tuple: result=[result]
	if result != None:
		for row in result:
			USERID2=row[0]
			NAME=row[1]
			ID=row[2]
			oppname_map[USERID2]=[ID,NAME]
	#Grab Opponent's Team Names
	result = executeQuery(f"SELECT TEAMID, NAME FROM TEAMS WHERE TEAMID IN (SELECT TEAM2 FROM USER_MATCHES WHERE USERID1='{USERID}' OR USERID2='{USERID}')")
	if type(result) == tuple: result=[result]
	if result != None:
		for row in result:
			TEAMID=row[0]
			NAME=row[1]
			oppteam_map[TEAMID]=NAME
	return mymatches_table_data,oppname_map,oppteam_map
	
def getSpecificPlayerMatchesTableData(unique_user_id):
	mymatches_table_data = executeQuery(f"SET @USERID = (SELECT USERID FROM USERS WHERE ID = {unique_user_id});\
		SET @OPTOUT = (SELECT COUNT(*) FROM USER_LOGINS WHERE OPTOUT = 1 AND USERID=@USERID) = 0;\
		SELECT x.ID, x.TIME, y.ID, y.NAME, x.NK2, z.NAME, x.MODE, x.RESULT1, x.SCORE1, x.SCORE2, x.MMR2 FROM USER_MATCHES x\
			JOIN (SELECT USERID, NAME, ID FROM USERS WHERE USERID IN (SELECT USERID2 FROM USER_MATCHES WHERE USERID1=@USERID OR USERID2=@USERID)) y\
			JOIN (SELECT TEAMID, NAME FROM TEAMS WHERE TEAMID IN (SELECT TEAM2 FROM USER_MATCHES WHERE USERID1=@USERID OR USERID2=@USERID)) z\
		WHERE x.USERID2 = y.USERID\
			AND z.TEAMID = x.TEAM2\
			AND @OPTOUT AND (SELECT COUNT(*) FROM USER_LOGINS WHERE OPTOUT = 1 AND USERID=x.USERID2) = 0\
		ORDER BY TIME DESC",multiple=True)
	if type(mymatches_table_data) == tuple: mymatches_table_data=[mymatches_table_data]
	return mymatches_table_data
	
def getLiveMatchesTableData(QUERY):
	live_matches_table_data = executeQuery(f"SELECT ID, TIME, MMR1, NK1, MMR2, NK2, MODE, SCORE1, SCORE2, RESULT1 FROM USER_MATCHES {QUERY} ORDER BY TIME DESC LIMIT 500")
	if type(live_matches_table_data) == tuple: live_matches_table_data=[live_matches_table_data]
	return live_matches_table_data
	
def getChalTableData():
	chal_table_data = executeQuery("SELECT x.ID, x.TIME, y.NAME FROM meta_chal_report x JOIN (SELECT ID, NAME FROM EVENTS) y WHERE x.EVENTID=y.ID ORDER BY x.ID DESC")
	if type(chal_table_data) == tuple: chal_table_data=[chal_table_data]
	return chal_table_data
	
def getTeamwarsTableData():
	tw_table_data = executeQuery("SELECT ID, STARTTIME, NAME FROM EVENTS WHERE TYPE=5 AND STARTTIME + 48 * 3600 < UNIX_TIMESTAMP() ORDER BY ID DESC ")
	if type(tw_table_data) == tuple: tw_table_data=[tw_table_data]
	return tw_table_data
	
def getTeamApplicationsTableData(unique_team_id,access_level=-1):
	if access_level == -1: return None
	team_table_data = executeQuery(f"SELECT y.ID, y.NAME, x.STATUS, x.ROLE FROM TEAM_ACCEPT x\
	JOIN USERS y\
	WHERE x.TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) AND x.USERID = y.USERID")
	if type(team_table_data) == tuple: team_table_data=[team_table_data]
	return team_table_data
	
def getTeamApplicationsData(ingame_team_id):
	application_data={}
	result = executeQuery(f"SELECT USERID, STATUS, ROLE FROM TEAM_ACCEPT WHERE TEAMID={ingame_team_id}")	
	if result == None: return application_data
	elif type(result) == tuple: result=[result]
	for card_data in result:
		userid=card_data[0]
		status=card_data[1]
		role=card_data[2]
		application_data[userid]=[status,role]
	return application_data
	
def getCardRequestTableData(ingame_team_id,access_level=-1):
	if access_level == -1: return None
	#print(f"Request Details Table Data, ingame_team_id {ingame_team_id}")
	last_two_weeks = int(time.time()) - 3600 * 24 * 14
	request_table_data = executeQuery(f"SELECT UPDATED, USERID, CARDID FROM TEAM_REQUESTS WHERE TEAMID={ingame_team_id} AND UPDATED > {last_two_weeks} ORDER BY UPDATED DESC LIMIT 1000")
	if type(request_table_data) == tuple: request_table_data=[request_table_data]
	return request_table_data
	
def getCardRequestTableDataTime(ingame_team_id,timeframe=7): #timeframe in days
	search_timeframe = int(time.time()) - 3600 * 24 * timeframe
	#print(f"Request Details Table Data, ingame_team_id {ingame_team_id}")
	request_table_data = executeQuery(f"SELECT UPDATED, USERID, CARDID FROM TEAM_REQUESTS WHERE TEAMID={ingame_team_id} AND UPDATED > {search_timeframe}")
	if type(request_table_data) == tuple: request_table_data=[request_table_data]
	return request_table_data
	
def getCardDonationTableData(ingame_team_id,access_level=-1):
	if access_level == -1: return None
	#print(f"Donation Details Table Data, ingame_team_id {ingame_team_id}")
	last_two_weeks = int(time.time()) - 3600 * 24 * 14
	donation_table_data = executeQuery(f"SELECT UPDATED, RECEIVER, SENDER, CARDID FROM TEAM_DONATIONS WHERE TEAMID={ingame_team_id} AND UPDATED > {last_two_weeks} ORDER BY UPDATED DESC LIMIT 1000")
	if type(donation_table_data) == tuple: donation_table_data=[donation_table_data]
	return donation_table_data
	
def getCardDonationTableDataTime(ingame_team_id,timeframe=7): #timeframe in days
	#print(f"Donation Details Table Data, ingame_team_id {ingame_team_id}")
	search_timeframe = int(time.time()) - 3600 * 24 * timeframe
	donation_table_data = executeQuery(f"SELECT UPDATED, RECEIVER, SENDER, CARDID FROM TEAM_DONATIONS WHERE TEAMID={ingame_team_id} AND UPDATED > {search_timeframe}")
	if type(donation_table_data) == tuple: donation_table_data=[donation_table_data]
	return donation_table_data
	
def getTeamsTableData(rank,members,nklevel,status):
	WHERE='WHERE x.RANK <= 1000'
	if rank == 'Top 50': WHERE='WHERE x.RANK <= 50'
	elif rank == 'Top 250': WHERE='WHERE x.RANK <= 250'
	elif rank == '1000 to 2000': WHERE='WHERE x.RANK > 1000 AND x.RANK <= 2000'
	elif rank == '>2000': WHERE='WHERE x.RANK > 2000'	
	WHERE+=f" AND x.NKLEVEL <= {nklevel}"
	WHERE+=f" AND x.MEMBERS <= {members}"
	if status!='All' and "'" not in status:
		if status == 'Open': status='AutoAccepted'
		WHERE+=f" AND x.STATUS = '{status}'"
	result = executeQuery(f"SELECT x.ID, y.NAME, x.RANK, x.LASTRANK, x.TROPHIES, x.COUNTRY, x.MEMBERS, x.STATUS, x.NKLEVEL, z.MMR, x.UPDATED from TEAMS_REPORT x\
		JOIN (SELECT TEAMID, NAME FROM TEAMS) y\
		JOIN (SELECT TEAMID, AVG(MMR) AS MMR FROM TEAM_MEMBERS GROUP BY TEAMID) z\
		{WHERE} AND x.TEAMID = y.TEAMID AND y.TEAMID = z.TEAMID\
		ORDER BY TROPHIES DESC, RANK ASC")
	if type(result) == tuple: result=[result]
	return result
	
def getPlayersByName(name):
	name = removeCharactersOutOfRange(name)
	result = executeSanitize(f"SELECT y.ID, y.NAME, z.ID, z.NAME, x.RANK, x.LASTRANK, x.MMR, x.NKLEVEL, x.DONATED_ALL, x.TW_TOKENS, x.WINS_PVP, x.WINS_PVPP, x.WINS_CHLG, x.WINS_TW, x.WINS_FF, x.WINS_FFP, x.UPDATED from TEAM_MEMBERS x\
		JOIN (SELECT ID, USERID, NAME FROM USERS) y\
		JOIN (SELECT a.ID, a.TEAMID, b.NAME FROM TEAMS_REPORT a JOIN TEAMS b WHERE a.TEAMID = b.TEAMID) z\
	WHERE x.USERID IN (SELECT USERID FROM USERS WHERE NAME LIKE %(name)s) AND\
		x.USERID = y.USERID AND\
		x.TEAMID = z.TEAMID\
	ORDER BY MMR DESC LIMIT 250", name)
	if type(result) == tuple: result=[result]
	return result
	
def getLeaderboardUserNamesByName(name):
	user_name_map={}
	result = executeSanitize(f"SELECT USERID, NAME FROM USERS WHERE NAME LIKE %(name)s", name)
	if result == None: return user_name_map
	if type(result) == tuple: result=[result]
	for row in result:
		userid=row[0]
		user_name=row[1]
		user_name_map[userid]=user_name
	return user_name_map
	
def getLeaderboardTeamsByName(name):
	team_name_map={}
	result = executeSanitize(f"SELECT TEAMID, NAME from TEAMS WHERE TEAMID IN (SELECT TEAMID FROM TEAM_MEMBERS WHERE USERID IN (SELECT USERID FROM USERS WHERE NAME LIKE %(name)s))", name)
	if result == None: return team_name_map
	if type(result) == tuple: result=[result]
	for row in result:
		teamid=row[0]
		team_name=row[1]
		team_name_map[teamid]=team_name
	return team_name_map
	
def getPlayersTableData(query,sort="RANK",name=None):
	if name != None: return getPlayersByName(name)
	#cols = ['id', 'Team', 'Rank', 'Trend', 'MMR', 'NK', 'Donated', 'TW Caps', 'PVP', 'CHLG', 'TW', 'FF', 'PVP', 'FREE', 'SHOP', 'Lockers']
	updated = executeQuery(f"SELECT MAX(UPDATED) from TEAM_MEMBERS WHERE {query}")
	if type(updated)==tuple: updated=updated[0]
	result = None
	if sort == "RANK":
		result = executeQuery(f"SELECT y.ID, y.NAME, z.ID, z.NAME, x.RANK, x.LASTRANK, x.MMR, x.NKLEVEL, x.DONATED_ALL, x.TW_TOKENS, x.WINS_PVP, x.WINS_PVPP, x.WINS_CHLG, x.WINS_TW, x.WINS_FF, x.WINS_FFP, x.UPDATED from TEAM_MEMBERS x\
			JOIN (SELECT ID, USERID, NAME FROM USERS) y\
			JOIN (SELECT a.ID, a.TEAMID, b.NAME FROM TEAMS_REPORT a JOIN TEAMS b WHERE a.TEAMID = b.TEAMID) z\
		WHERE x.USERID IN (SELECT USERID FROM USERS WHERE {query}) AND\
			x.USERID = y.USERID AND\
			x.TEAMID = z.TEAMID\
		ORDER BY RANK ASC")
	else:
		TARGET=""
		if sort=='DONATED': TARGET = "DONATED_ALL"
		elif sort=='TW CAPS': TARGET = "TW_TOKENS"
		elif sort=='PVP WINS': TARGET = "WINS_PVP"
		elif sort=='PVP WINS PERFECT': TARGET = "WINS_PVPP"
		elif sort=='CHLG WINS': TARGET = "WINS_CHLG"
		elif sort=='TW WINS': TARGET = "WINS_TW"
		elif sort=='FF WINS': TARGET = "WINS_FF"
		elif sort=='FF WINS PERFECT': TARGET = "WINS_FFP"
		else: TARGET = "MMR"
		result = executeQuery(f"SELECT y.ID, y.NAME, z.ID, z.NAME, x.RANK, x.LASTRANK, x.MMR, x.NKLEVEL, x.DONATED_ALL, x.TW_TOKENS, x.WINS_PVP, x.WINS_PVPP, x.WINS_CHLG, x.WINS_TW, x.WINS_FF, x.WINS_FFP, x.UPDATED from TEAM_MEMBERS x\
			JOIN (SELECT ID, USERID, NAME FROM USERS) y\
			JOIN (SELECT a.ID, a.TEAMID, b.NAME FROM TEAMS_REPORT a JOIN TEAMS b WHERE a.TEAMID = b.TEAMID) z\
		WHERE x.USERID IN (SELECT USERID FROM USERS) AND\
			x.USERID = y.USERID AND\
			x.TEAMID = z.TEAMID\
		ORDER BY {TARGET} DESC LIMIT 1000")
	return result
	
def getSpecificTeamTableData(team_id):
	#print(f"Specific Team Table Data, TeamID: {team_id}")
	ingame_team_id = executeQuery(f"SELECT TEAMID from TEAMS_REPORT WHERE ID={team_id}")
	if ingame_team_id == None: return None
	ingame_team_id=ingame_team_id[0]
	return executeQuery(f"SELECT RANK, TROPHIES, MEMBERS, NKLEVEL, COUNTRY, STATUS, DESCRIPTION from TEAMS_REPORT WHERE TEAMID={ingame_team_id}")
	
def getAllUserNames(ingame_team_id, unique_user_id=False):
	user_name_map={}
	if ingame_team_id == None: return user_name_map
	result=None
	if unique_user_id:
		result = executeQuery(f"SELECT ID, NAME FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID={ingame_team_id})")
	else:
		result = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID={ingame_team_id})")
	if type(result) == tuple: result=[result]
	if result == None: return user_name_map
	for row in result:
		userid=row[0]
		user_name=row[1]
		if type(user_name) == str: user_name=user_name.upper()
		user_name_map[userid]=user_name
	return user_name_map
	
def getAllUserNamesFromUniqueTeamID(unique_team_id):
	user_name_map={}
	if unique_team_id == None: return user_name_map
	result = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))")
	if type(result) == tuple: result=[result]
	if result == None: return user_name_map
	for row in result:
		userid=row[0]
		user_name=row[1]
		if type(user_name) == str: user_name=user_name.upper()
		user_name_map[userid]=user_name
	return user_name_map
	
def getAllUserNamesApplications(ingame_team_id):
	user_name_map={}
	result = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_ACCEPT WHERE TEAMID={ingame_team_id}) OR USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID={ingame_team_id})")
	if type(result) == tuple: result=[result]
	if result == None: return user_name_map
	for row in result:
		userid=row[0]
		user_name=row[1]
		if type(user_name) == str: user_name=user_name.upper()
		user_name_map[userid]=user_name
	return user_name_map
	
def getAllUserNamesReverse(ingame_team_id):
	user_name_map={}
	if ingame_team_id == None: return user_name_map
	result = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID={ingame_team_id})")
	if type(result) == tuple: result=[result]
	if result == None: return user_name_map
	for row in result:
		userid=row[0]
		user_name=row[1]
		if type(user_name) == str: user_name = user_name.upper()
		user_name_map[user_name]=userid
	return user_name_map
	
def getAllUserNamesReverseApplications(userid_list_string):
	user_name_map={}
	if len(userid_list_string) == 0: return user_name_map
	result = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE ID IN ({userid_list_string})")
	if type(result) == tuple: result=[result]
	if result == None: return user_name_map
	for row in result:
		userid=row[0]
		user_name=row[1]
		if type(user_name) == str: user_name = user_name.upper()
		user_name_map[user_name]=userid
	return user_name_map
	
def getLeaderboardUserNames(limit, WHERE=None):
	user_name_map={}
	result=None
	if WHERE == None:
		result = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE USERID IN (SELECT USERID from TEAM_MEMBERS WHERE RANK <= {limit} AND RANK <> 0)")
	else:
		result = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE USERID IN (SELECT USERID from TEAM_MEMBERS WHERE {WHERE})")
	if result == None: return user_name_map
	if type(result) == tuple: result=[result]
	for row in result:
		userid=row[0]
		user_name=row[1]
		user_name_map[userid]=user_name
	return user_name_map
	
def getLeaderboardTeams(limit, WHERE=None):
	team_name_map={}
	result=None
	if WHERE == None:
		result = executeQuery(f"SELECT TEAMID, NAME from TEAMS WHERE TEAMID IN (SELECT TEAMID FROM TEAM_MEMBERS WHERE RANK <= {limit} AND RANK <> 0)")
	else:
		result = executeQuery(f"SELECT TEAMID, NAME from TEAMS WHERE TEAMID IN (SELECT TEAMID FROM TEAM_MEMBERS WHERE {WHERE})")
	if result == None: return team_name_map
	if type(result) == tuple: result=[result]
	for row in result:
		teamid=row[0]
		team_name=row[1]
		team_name_map[teamid]=team_name
	return team_name_map
	
###TEAMWAR###

def getTeamwarBracketData(unique_team_id):
	bracket_data=[]
	updated = None
	if unique_team_id == None: return bracket_data, updated
	result = executeQuery(f"SELECT y.ID, y.RANK, x.TEAMNAME, x.RUNS, x.MEMBERS, x.SCORE, x.UPDATED FROM TEAMWAR_BRACKET x\
		JOIN (SELECT DISTINCT a.ID, a.RANK, a.TEAMID, b.NAME FROM TEAMS_REPORT a\
				JOIN (SELECT TEAMID, NAME FROM TEAMS) b\
				JOIN (SELECT TEAMNAME, BRACKETID FROM TEAMWAR_BRACKET) c\
			WHERE a.TEAMID = b.TEAMID AND c.BRACKETID = (SELECT MAX(BRACKETID) FROM TEAMWAR_BRACKET WHERE TEAMNAME = (SELECT NAME FROM TEAMS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))) AND (c.TEAMNAME = b.NAME OR (a.TEAMID = 0 AND c.TEAMNAME NOT IN (SELECT NAME FROM TEAMS)))) y\
	WHERE x.BRACKETID = (SELECT MAX(BRACKETID) FROM TEAMWAR_BRACKET WHERE TEAMNAME = (SELECT NAME FROM TEAMS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))) AND (y.NAME = x.TEAMNAME OR (x.TEAMNAME NOT IN (SELECT NAME FROM TEAMS) AND y.TEAMID = 0))")
	#result = executeQuery(f"SELECT x.ID, x.RANK, y.NAME, z.RUNS, z.MEMBERS, z.SCORE, z.UPDATED FROM TEAMS_REPORT x\
	#	JOIN (SELECT TEAMID, NAME FROM TEAMS) y\
	#	JOIN (SELECT TEAMNAME, RUNS, MEMBERS, SCORE, UPDATED FROM TEAMWAR_BRACKET WHERE BRACKETID = (SELECT MAX(BRACKETID) FROM TEAMWAR_BRACKET WHERE TEAMNAME = (SELECT NAME FROM TEAMS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id})))) z\
	#WHERE y.TEAMID = x.TEAMID AND y.NAME = z.TEAMNAME")
	if result == None: return bracket_data, updated
	if type(result) == tuple: result=[result]
	for row in result:
		ID=row[0]
		RANK=row[1]
		TEAMNAME=row[2]
		RUNS=row[3]
		MEMBERS=row[4]
		SCORE=row[5]
		if updated == None or updated < row[6]: updated=row[6]
		bracket_data.append([ID,RANK,TEAMNAME,RUNS,MEMBERS,SCORE])
	return bracket_data, updated

def getTeamwarBracketHistoryData(unique_team_id):
	bracket_data=[]
	result = executeQuery(f"SELECT BRACKETID, UPDATED, TEAMNAME, RUNS, SCORE FROM TEAMWAR_BRACKET\
		WHERE TEAMNAME = (SELECT NAME FROM TEAMS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))\
		ORDER BY UPDATED DESC")
	if result == None: return bracket_data
	if type(result) == tuple: result=[result]
	for row in result:
		BRACKETID=row[0]
		UPDATED=row[1]
		TEAMNAME=row[2]
		if type(TEAMNAME) == str: TEAMNAME = TEAMNAME.upper()
		RUNS=row[3]
		SCORE=row[4]
		bracket_data.append([BRACKETID,UPDATED,TEAMNAME,RUNS,SCORE])
	return bracket_data

def getSpecificBracketData(unique_bracket_id):
	bracket_data=[]
	updated = None
	if unique_bracket_id == None: return bracket_data, updated
	result = executeQuery(f"SELECT y.ID, y.RANK, x.TEAMNAME, x.RUNS, x.MEMBERS, x.SCORE, x.UPDATED FROM TEAMWAR_BRACKET x\
		JOIN (SELECT DISTINCT a.ID, a.RANK, a.TEAMID, b.NAME FROM TEAMS_REPORT a\
				JOIN (SELECT TEAMID, NAME FROM TEAMS) b\
				JOIN (SELECT TEAMNAME, BRACKETID FROM TEAMWAR_BRACKET) c\
			WHERE a.TEAMID = b.TEAMID AND c.BRACKETID = {unique_bracket_id} AND (c.TEAMNAME = b.NAME OR (a.TEAMID = 0 AND c.TEAMNAME NOT IN (SELECT NAME FROM TEAMS)))) y\
	WHERE x.BRACKETID = {unique_bracket_id} AND (y.NAME = x.TEAMNAME OR (x.TEAMNAME NOT IN (SELECT NAME FROM TEAMS) AND y.TEAMID = 0))")
	#result = executeQuery(f"SELECT x.ID, x.RANK, y.NAME, z.RUNS, z.MEMBERS, z.SCORE, z.UPDATED FROM TEAMS_REPORT x\
	#	JOIN (SELECT TEAMID, NAME FROM TEAMS) y\
	#	JOIN (SELECT TEAMNAME, RUNS, MEMBERS, SCORE, UPDATED FROM TEAMWAR_BRACKET WHERE BRACKETID = {unique_bracket_id}) z\
	#WHERE y.TEAMID = x.TEAMID AND y.NAME = z.TEAMNAME")
	if result == None: return bracket_data, updated
	if type(result) == tuple: result=[result]
	for row in result:
		ID=row[0]
		RANK=row[1]
		TEAMNAME=row[2]
		RUNS=row[3]
		MEMBERS=row[4]
		SCORE=row[5]
		if updated == None or updated < row[6]: updated=row[6]
		bracket_data.append([ID,RANK,TEAMNAME,RUNS,MEMBERS,SCORE])
	return bracket_data, updated
	
def getAllTeamwarBracketData(league,limit=None):
	TROPHIES=[3500,None] #min, max
	if league == 'gold': TROPHIES=[3500,None]
	elif league == 'silver': TROPHIES=[1500,3500]
	elif league == 'bronze': TROPHIES=[500,1500]
	elif league == 'wood': TROPHIES=[None,500]
	LIMIT=''
	if limit != None: LIMIT = f'LIMIT {limit}'
	bracket_data=[]
	updated = None
	FILTER = "WHERE"
	MINT,MAXT=TROPHIES
	min_set=False
	if MINT != None:
		FILTER+=f" TROPHIES >= {MINT}"
		min_set=True
	if MAXT != None:
		if min_set: FILTER+=f" AND TROPHIES < {MAXT}"
		else: FILTER+=f" TROPHIES < {MAXT}"
	result = executeQuery(f"SELECT x.BRACKETID, z.RANK, x.TEAMNAME, x.RUNS, x.MEMBERS, x.SCORE, x.UPDATED FROM TEAMWAR_BRACKET x\
		JOIN (SELECT TEAMID, NAME FROM TEAMS) y\
		JOIN (SELECT RANK, TEAMID FROM TEAMS_REPORT {FILTER}) z\
	WHERE x.TEAMNAME = y.NAME AND y.TEAMID = z.TEAMID AND x.UPDATED > (SELECT MAX(STARTTIME)+3600*24*5-3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME+3600*24*5-3600 < UNIX_TIMESTAMP()) ORDER BY x.SCORE DESC {LIMIT}")
	if result == None: return bracket_data, updated
	if type(result) == tuple: result=[result]
	for row in result:
		BRACKETID=row[0]
		RANK=row[1]
		TEAMNAME=row[2].upper()
		RUNS=row[3]
		MEMBERS=row[4]
		SCORE=row[5]
		if updated == None or updated < row[6]: updated=row[6]
		if RANK == None: RANK=">2000"
		bracket_data.append([BRACKETID,RANK,TEAMNAME,RUNS,MEMBERS,SCORE])
	return bracket_data, updated
	
def getAllTeamwarBracketSummary():
	full_summary=[]
	result = executeQuery(f"SELECT MEMBERS, TROPHIES FROM TEAMS_REPORT WHERE TROPHIES > 0 AND MEMBERS >= 10")
	if result == None: return full_summary
	if type(result) == tuple: result=[result]
	for row in result:
		MEMBERS=row[0]
		TROPHIES=row[1]
		full_summary.append([TROPHIES,MEMBERS])
	return full_summary
	
def getEventData(search_time):
	eventid_to_result={}
	result = executeQuery(f"SELECT X.ID, X.NAME, X.TEAM, X.TYPE, X.STARTTIME, X.ENDTIME, Y.SCORE FROM EVENTS_TWO X\
			JOIN EVENT_PACKS Y\
		WHERE X.ENDTIME > {search_time} AND X.PACKSID=Y.PACKSID AND Y.TEAM=0 ORDER BY ID DESC")
	if result == None: return eventid_to_result
	if type(result) == tuple: result=[result]
	for row in result:
		ID=row[0]
		NAME=row[1]
		TEAM=int(row[2])
		TYPE=row[3]
		STARTTIME=row[4]
		ENDTIME=row[5]
		SCORE=row[6]
		if "TW_" in NAME:
			tw_split = NAME.split('_')
			if len(tw_split) == 3:
				NAME="Team War - Week "
				NAME+=tw_split[1]
				NAME+=" - " + tw_split[2]
		if ID not in eventid_to_result:
			eventid_to_result[ID] = [NAME, TEAM, TYPE, STARTTIME, ENDTIME, 1, SCORE]
		else:
			eventid_to_result[ID][5]+=1
			if len(eventid_to_result[ID]) < 14:
				eventid_to_result[ID].append(SCORE)
	for key in eventid_to_result.keys():
		while len(eventid_to_result[key]) < 14:
			eventid_to_result[key].append(0)
	return eventid_to_result
	
def getSpecificEventData(event_id):
	NAME = "Unknown"
	TYPE = "Unknown"
	START = 0
	END = 0
	pack_data = []
	
	#Get the initial event data
	result = executeQuery(f"SELECT NAME, TYPE, STARTTIME, ENDTIME, PACKSID FROM EVENTS_TWO X WHERE ID = {event_id}")
	if result == None: return NAME,TYPE,START,END,pack_data
	NAME=result[0]
	TYPE=result[1]
	START=result[2]
	END=result[3]
	PACKSID=result[4]
	if PACKSID == None: return NAME,TYPE,START,END,pack_data
	
	#get the pack details
	packid_to_result={}
	result = executeQuery(f"SELECT x.ID,x.TEAM,x.PACKNUM,x.SCORE,\
							x.CARDS0,x.CARDSP0,\
							x.CARDS1,x.CARDSP1,\
							x.CARDS2,x.CARDSP2,\
							x.CARDS3,x.CARDSP3,\
							x.CUR1,x.CUR2,x.CUR3,x.CUR4,\
							x.UPS0,x.UPSP0,\
							x.UPS1,x.UPSP1,\
							x.UPS2,x.UPSP2,\
							y.CARDID,y.QUANTITY,\
							y.CODE,y.VALUE\
							FROM EVENT_PACKS x\
			JOIN REWARD_PACKS y\
		WHERE x.PACKSID = {PACKSID} AND x.SUBPACK=y.PACKSID")
	if result == None: return NAME,TYPE,START,END,pack_data
	if type(result) == tuple: result=[result]
	for row in result:
		ID=row[0]
		if ID not in packid_to_result:
			packid_to_result[ID]=[]
			for i in range(1,22):
				packid_to_result[ID].append(row[i])
			packid_to_result[ID].append([])
		CARDID=row[22]
		QUANTITY=row[23]
		CODE=row[24]
		VALUE=row[25]
		if CARDID != None:
			packid_to_result[ID][-1].append({CARDID:QUANTITY})
		if CODE != None and CODE != 255:
			packid_to_result[ID][-1].append({CODE:VALUE})
	for key in packid_to_result.keys():
		pack_data.append(packid_to_result[key])
	if "TW_" in NAME:
		tw_split = NAME.split('_')
		if len(tw_split) == 3:
			NAME="Team War - Week "
			NAME+=tw_split[1]
			NAME+=" - " + tw_split[2]
	return NAME,TYPE,START,END,pack_data
	
def getTeamwarHistoryData(unique_team_id,weeks_ago):
	history_data={}
	all_dates=[]
	if unique_team_id == None: return history_data,all_dates
	#print(f"Teamwar Bracket Table Data, Team Name {team_name}")
	result = executeQuery(f"SELECT X.USERID, X.SCORE, X.CAPS, Y.STARTTIME FROM TEAMWAR_HISTORY_TWO X\
			JOIN EVENTS Y\
		WHERE X.EVENTID = Y.EVENTID AND Y.ENDTIME > UNIX_TIMESTAMP() - 3600*24*7*{weeks_ago} AND\
			X.USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))\
			ORDER BY Y.STARTTIME DESC")
	if result == None: return history_data,all_dates
	if type(result) == tuple: result=[result]
	usernames_map = getAllUserNamesFromUniqueTeamID(unique_team_id)
	for row in result:
		USERID=row[0]
		SCORE=row[1]
		CAPS=row[2]
		STARTTIME=row[3]
		timestamp=time.strftime('%W_%Y', time.localtime(STARTTIME))
		WEEK=int(timestamp.split('_')[0])
		if WEEK < 10:
			WEEK = f"0{WEEK}"
		YEAR=int(timestamp.split('_')[1])
		cur_week=f"{YEAR}-{WEEK}"
		if cur_week not in all_dates:
			all_dates.append(cur_week)
		if SCORE == None: SCORE = "X"
		if CAPS == None or CAPS == 0: SCORE = "N/A"
		username="Unknown-"+USERID[:4]
		if USERID in usernames_map:
			username=usernames_map[USERID]
		if username not in history_data:
			history_data[username]={}
		history_data[username][cur_week]=SCORE
	all_dates=sorted(all_dates, reverse=True)
	return history_data,all_dates
	
def getTeamwarHistoryCapsData(unique_team_id,weeks_ago):
	history_data={}
	all_dates=[]
	if unique_team_id == None: return history_data,all_dates
	result = executeQuery(f"SELECT X.USERID, X.CAPS, Y.STARTTIME FROM TEAMWAR_HISTORY_TWO X\
			JOIN EVENTS Y\
		WHERE X.EVENTID = Y.EVENTID AND Y.ENDTIME > UNIX_TIMESTAMP() - 3600*24*7*{weeks_ago} AND\
			X.USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))\
			ORDER BY Y.STARTTIME DESC")
	if result == None: return history_data,all_dates
	if type(result) == tuple: result=[result]
	usernames_map = getAllUserNamesFromUniqueTeamID(unique_team_id)
	for row in result:
		USERID=row[0]
		CAPS=row[1]
		STARTTIME=row[2]
		timestamp=time.strftime('%W_%Y', time.localtime(STARTTIME))
		WEEK=int(timestamp.split('_')[0])
		if WEEK < 10:
			WEEK = f"0{WEEK}"
		YEAR=int(timestamp.split('_')[1])
		cur_week=f"{YEAR}-{WEEK}"
		if cur_week not in all_dates:
			all_dates.append(cur_week)
		if CAPS == None: CAPS = "X"
		username="Unknown-"+USERID[:4]
		if USERID in usernames_map:
			username=usernames_map[USERID]
		if username not in history_data:
			history_data[username]={}
		history_data[username][cur_week]=CAPS
	all_dates=sorted(all_dates, reverse=True)
	return history_data,all_dates
	
def getTeamEventHistoryData(unique_team_id):
	history_data={}
	all_events={}
	result = executeQuery(f"SELECT USERID, EVENTID, SCORE FROM TEAM_EVENT_PARTICIPATION WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))")
	if result == None: return history_data,all_events
	if type(result) == tuple: result=[result]
	usernames_map = getAllUserNamesFromUniqueTeamID(unique_team_id)
	for row in result:
		USERID=row[0]
		EVENTID=row[1]
		SCORE=row[2]
		if EVENTID not in all_events:
			all_events[EVENTID]=None
		username="Unknown-"+USERID[:4]
		if USERID in usernames_map:
			username=usernames_map[USERID]
		if username not in history_data:
			history_data[username]={}
		history_data[username][EVENTID]=SCORE
	EVENT_LIST=",".join(str(x) for x in all_events.keys())
	result = executeQuery(f"SELECT EVENTID,NAME,PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8,FINALPACK,STARTTIME FROM EVENTS WHERE EVENTID IN ({EVENT_LIST})")
	if result == None: return history_data,all_events
	if type(result) == tuple: result=[result]
	for row in result:
		EVENTID=row[0]
		NAME=row[1]
		PACK1=row[2]
		PACK2=row[3]
		PACK3=row[4]
		PACK4=row[5]
		PACK5=row[6]
		PACK6=row[7]
		PACK7=row[8]
		PACK8=row[9]
		FINALPACK=row[10]
		STARTTIME=row[11]
		all_events[EVENTID]=[NAME,PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8,FINALPACK,STARTTIME]
	return history_data,all_events
	
def getTeamsMMR(unique_team_id, getRole=False):
	userid_to_mmr={}
	ingame_team_id=getInGameTeamID(unique_team_id)
	if ingame_team_id==None: return userid_to_mmr
	result = executeQuery(f"SELECT USERID, MMR, ROLE FROM TEAM_MEMBERS WHERE TEAMID={ingame_team_id}")
	if result == None: return userid_to_mmr
	if type(result) == tuple: result=[result]
	for row in result:
		if getRole: userid_to_mmr[row[0]]=[row[1],row[2]]
		else: userid_to_mmr[row[0]]=row[1]
	return userid_to_mmr

def getUpgradeTabData(unique_team_id):
	ordered_cards=[]
	if unique_team_id == None: return ordered_cards,None
	result = executeQuery("SELECT CARDID1, CARDID2 FROM TEAMWAR_PAIRS WHERE PAIRID IN (SELECT PAIRID FROM TEAMWAR_CARDS WHERE TIME IN (SELECT MAX(TIME) FROM TEAMWAR_CARDS))")
	if type(result) == tuple: result=[result]
	for row in result:
		card1=row[0]
		card2=row[1]
		ordered_cards.append(card1)
		ordered_cards.append(card2)
	card_choices_str=",".join(str(x) for x in ordered_cards)
	leader_choice = executeQuery(f"SELECT CARDID, VOTE, LEVEL FROM TEAMWAR_CHOICE WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) AND CARDID IN ({card_choices_str})")
	if type(leader_choice) == tuple: leader_choice=[leader_choice]
	return ordered_cards, leader_choice
	
def getTeamWarChoices(unique_team_id):
	if not isValidTeamID(unique_team_id): return None
	card_results={}
	leader_choice = executeQuery(f"SELECT CARDID, VOTE, LEVEL FROM TEAMWAR_CHOICE WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) AND UPDATED > (SELECT MAX(STARTTIME) FROM EVENTS WHERE TYPE=5)")
	if leader_choice == None: return card_results
	elif type(leader_choice) == tuple: leader_choice=[leader_choice]
	for card_data in leader_choice:
		card_id=card_data[0]
		vote=int(card_data[1])
		level=card_data[2]
		card_results[card_id]=[vote,level]
	return card_results
	
def getBracketSubscribe(email):
	subscribe_results={}
	OneWeekAgo=int(time.time()) - 3600 * 24 * 4
	subscriptions = executeQuery(f"SELECT TEAMNAME, SUBSCRIBED FROM BRACKET_SUBSCRIBE WHERE EMAIL = '{email}' AND BRACKETID IN (SELECT BRACKETID FROM TEAMWAR_BRACKET WHERE UPDATED > {OneWeekAgo})")
	if subscriptions == None: return subscribe_results
	elif type(subscriptions) == tuple: subscriptions=[subscriptions]
	for sub_data in subscriptions:
		team_name=sub_data[0]
		is_subscribed=int(sub_data[1])
		subscribe_results[team_name]=is_subscribed
	return subscribe_results
	
def getCardComparisonTableData(unique_team_id):
	ordered_cards=[]
	result = executeQuery("SELECT CARDID1, CARDID2 FROM TEAMWAR_PAIRS WHERE PAIRID IN (SELECT PAIRID FROM TEAMWAR_CARDS WHERE TIME IN (SELECT MAX(TIME) FROM TEAMWAR_CARDS))")
	if type(result) == tuple: result=[result]
	for row in result:
		card1=row[0]
		card2=row[1]
		ordered_cards.append(card1)
		ordered_cards.append(card2)
	SEARCH_CARDS=",".join(str(x) for x in ordered_cards)
	card_comparison = executeQuery(f"SELECT CARDID, LEVEL, UPGRADES FROM USER_COLLECTIONS WHERE USERID IN (SELECT ID FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id})) AND CARDID IN ({SEARCH_CARDS}))")
	if type(card_comparison) == tuple: card_comparison=[card_comparison]	
	leader_choice = executeQuery(f"SELECT CARDID, VOTE, LEVEL FROM TEAMWAR_CHOICE WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id} AND UPDATED > (SELECT MAX(STARTTIME) FROM EVENTS WHERE TYPE=5))")
	if type(leader_choice) == tuple: leader_choice=[leader_choice]
	return ordered_cards, card_comparison, leader_choice
	
def getTeamWarUpgradesSpentTableData(unique_team_id):
	cur_time = int(time.time())
	table_data={} # { blobid: [{userid: spent, userid: spent},{cardid: spent, cardid: spent} ], ...}
	blobid_to_time={}
	if not isValidTeamID(unique_team_id): return table_data,blobid_to_time
	#Merge these 4 into a single SQL query
	usernames_map = getAllUserNamesFromUniqueTeamID(unique_team_id)
	cards_spent = executeQuery(f"SELECT CARDID, SPENT, TOTAL, UPDATED, BLOBID FROM TEAMWAR_UPGRADE_CARDS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) and UPDATED > (SELECT MAX(STARTTIME) + 3600 * 24 * 2 - 3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME + 3600 * 24 * 2 < {cur_time}) ORDER BY UPDATED")
	users_spent = executeQuery(f"SELECT USERID, SPENT, TOTAL, UPDATED, BLOBID FROM TEAMWAR_UPGRADE_USERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) and UPDATED > (SELECT MAX(STARTTIME) + 3600 * 24 * 2 - 3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME + 3600 * 24 * 2 < {cur_time}) ORDER BY UPDATED")
	'''
	cards_spent = executeQuery(f"SELECT CARDID, SPENT, TOTAL, UPDATED, BLOBID FROM TEAMWAR_UPGRADE_CARDS\
		WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) AND\
			UPDATED > (SELECT MAX(STARTTIME) + 3600 * 24 * 2 - 3600 FROM EVENTS WHERE TYPE=5)\
		ORDER BY UPDATED")
	users_spent = executeQuery(f"SELECT y.NAME, x.USERID, x.SPENT, x.TOTAL, x.UPDATED, x.BLOBID FROM TEAMWAR_UPGRADE_USERS x\
			JOIN (SELECT USERID, NAME FROM USERS) y\
		WHERE x.USERID = y.USERID AND\
			x.TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) AND\
			UPDATED > (SELECT MAX(STARTTIME) + 3600 * 24 * 2 - 3600 FROM EVENTS WHERE TYPE=5)\
			ORDER BY x.UPDATED")
	'''
	if type(cards_spent) == tuple: cards_spent=[cards_spent]
	if cards_spent == None: return table_data,blobid_to_time
	if type(users_spent) == tuple: users_spent=[users_spent]
	if users_spent == None: return table_data,blobid_to_time
	for row in cards_spent:
		CARDID, SPENT, TOTAL, UPDATED, BLOBID = [row[0],row[1],row[2],row[3],row[4]]
		blobid_to_time[BLOBID]=UPDATED
		if BLOBID not in table_data:
			table_data[BLOBID]=[{},{}]
		card_name=getCardName(CARDID)
		table_data[BLOBID][1][card_name]=SPENT
	USERS_LAST_SPENT={}
	for row in users_spent:
		USERID, SPENT, TOTAL, UPDATED, BLOBID = [row[0],row[1],row[2],row[3],row[4]]
		if SPENT == 0: continue
		if USERID in USERS_LAST_SPENT and SPENT <= USERS_LAST_SPENT[USERID]: continue
		blobid_to_time[BLOBID]=UPDATED
		if BLOBID not in table_data:
			table_data[BLOBID]=[{},{}]
		username="Unknown-"+USERID[:4]
		if USERID in usernames_map: username=usernames_map[USERID]
		LAST_SPENT=0
		if USERID in USERS_LAST_SPENT:
			LAST_SPENT=USERS_LAST_SPENT[USERID]
		else: USERS_LAST_SPENT[USERID]=0
		table_data[BLOBID][0][username]=SPENT-LAST_SPENT
		USERS_LAST_SPENT[USERID]=SPENT
	return table_data, blobid_to_time
	
def getTeamWarUpgradesCardsTableData(unique_team_id):
	table_data={} # { cardid: total, ...}
	if unique_team_id == None: return table_data
	cards_spent = executeQuery(f"SELECT CARDID, MAX(TOTAL) FROM TEAMWAR_UPGRADE_CARDS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) and UPDATED > (SELECT MAX(STARTTIME)+3600*24*2-3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME+3600*24*2-3600 < UNIX_TIMESTAMP()) GROUP BY CARDID")
	if cards_spent == None: return table_data
	if type(cards_spent) == tuple: cards_spent=[cards_spent]
	for row in cards_spent:
		CARDID = row[0]
		TOTAL = row[1]
		table_data[CARDID]=TOTAL
	return table_data
	
def getTeamWarStartTime():
	START_TIME = executeQuery("SELECT MAX(STARTTIME) FROM EVENTS WHERE TYPE=5")	
	if type(START_TIME) == tuple: START_TIME=START_TIME[0]
	return START_TIME
	
def getTeamWarUpgradesPlayerTableData(unique_team_id):
	table_data={} # { userid: [spent, total], ...}
	earned_data={}
	if unique_team_id == None: return table_data, earned_data
	cur_time = int(time.time())
	usernames_map = getAllUserNamesFromUniqueTeamID(unique_team_id)
	users_spent = executeQuery(f"SELECT USERID, MAX(SPENT), MAX(TOTAL) FROM TEAMWAR_UPGRADE_USERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) and UPDATED > (SELECT MAX(STARTTIME)+3600*24*2-3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME+3600*24*2-3600 < {cur_time}) GROUP BY USERID")
	if users_spent == None: return table_data, earned_data
	if type(users_spent) == tuple: users_spent=[users_spent]
	for row in users_spent:
		USERID = row[0]
		username="Unknown-"+USERID[:4]
		if USERID in usernames_map: username=usernames_map[USERID]
		SPENT = row[1]
		TOTAL = row[2]
		table_data[username]=[SPENT,TOTAL]
	time_earned = executeQuery(f"SELECT USERID, TOTAL, UPDATED FROM TEAMWAR_UPGRADE_USERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) and UPDATED > (SELECT MAX(STARTTIME)+3600*24*2-3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME+3600*24*2-3600 < {cur_time}) GROUP BY USERID, TOTAL;")
	if time_earned == None: return table_data, earned_data
	UPGRADE_START = getTeamWarStartTime() + 3600 * 24 * 2
	if UPGRADE_START > cur_time: UPGRADE_START = UPGRADE_START - 3600 * 24 * 7
	UPGRADE_DAY1_START = UPGRADE_START
	UPGRADE_DAY2_START = UPGRADE_DAY1_START + 3600 * 24
	UPGRADE_DAY3_START = UPGRADE_DAY2_START + 3600 * 24
	UPGRADE_DAY3_END = UPGRADE_DAY3_START + 3600 * 24
	if type(time_earned) == tuple: time_earned=[time_earned]
	for row in time_earned:
		USERID = row[0]
		username="Unknown-"+USERID[:4]
		if USERID in usernames_map: username=usernames_map[USERID]
		TOTAL = row[1]
		UPDATED = row[2]
		if username not in earned_data:
			earned_data[username]=[0,0,0]
		if UPDATED < UPGRADE_DAY1_START: continue
		elif UPGRADE_DAY2_START > UPDATED > UPGRADE_DAY1_START:
			earned_data[username][0]=TOTAL
		elif UPGRADE_DAY3_START > UPDATED > UPGRADE_DAY2_START:
			earned_data[username][1]=TOTAL-earned_data[username][0]
		elif UPGRADE_DAY3_END > UPDATED > UPGRADE_DAY3_START:
			earned_data[username][2]=TOTAL-(earned_data[username][1]+earned_data[username][0])
	for username in table_data.keys():
		if username not in earned_data:
			earned_data[username]=[0,0,0]
		result = earned_data[username]
		if result[0] == 0 and cur_time < UPGRADE_DAY2_START:
			earned_data[username][0]="Pending"
		if result[1] == 0 and cur_time < UPGRADE_DAY3_START:
			earned_data[username][1]="Pending"
		if result[2] == 0 and cur_time < UPGRADE_DAY3_END:
			earned_data[username][2]="Pending"
	return table_data, earned_data
	
def getTeamWarUpgradesPlayerTableData_nocaps(unique_team_id):
	table_data=[] # [USERNAME, ...]
	if unique_team_id == None: return table_data
	cur_time = int(time.time())
	usernames_map = getAllUserNamesFromUniqueTeamID(unique_team_id)
	users_spent = executeQuery(f"SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) AND\
		USERID NOT IN (SELECT USERID FROM TEAMWAR_UPGRADE_USERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) and UPDATED > (SELECT MAX(STARTTIME)+3600*24*2-3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME+3600*24*2-3600 < {cur_time}))")
	if users_spent == None: return table_data
	if type(users_spent) == tuple: users_spent=[users_spent]
	for row in users_spent:
		USERID = row[0]
		username="Unknown-"+USERID[:4]
		if USERID in usernames_map: username=usernames_map[USERID]
		table_data.append(username)
	return table_data
	
def getSummaryCardTableData(unique_team_id):
	user_cards_map={} #{ userid: {cardid : [level,upgrades], ...}, ... }
	if unique_team_id == None: return user_cards_map
	CARD_DATA = executeQuery(f"SELECT USERID, CARDID, LEVEL, UPGRADES FROM USER_COLLECTIONS WHERE USERID IN \
		(SELECT ID FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id})))")
	if type(CARD_DATA) == tuple: CARD_DATA=[CARD_DATA]
	if CARD_DATA == None: return user_cards_map
	for row in CARD_DATA:
		USERID, CARDID, LEVEL, UPGRADES = [row[0],row[1],row[2],row[3]]
		if USERID not in user_cards_map:
			user_cards_map[USERID]={}
		user_cards_map[USERID][CARDID]=[LEVEL, UPGRADES]
	return user_cards_map
	
def getSummaryCardTableData_all(unique_team_id):
	user_cards_map={} #{ userid: {cardid : [level,upgrades], ...}, ... }
	username_map={} #{ userid: [NAME,MMR,NKLEVEL], ... }
	if unique_team_id == None: return user_cards_map, username_map
	CARD_DATA = executeQuery(f"SELECT y.ID, y.NAME, z.MMR, z.NKLEVEL, x.CARDID, x.LEVEL, x.UPGRADES FROM USER_COLLECTIONS x\
		JOIN (SELECT ID, USERID, NAME FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))) y\
		JOIN (SELECT USERID, NKLEVEL, MMR FROM TEAM_MEMBERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}))) z\
	WHERE x.USERID = y.ID AND y.USERID = z.USERID")
	#CARD_DATA = executeQuery(f"SELECT USERID, CARDID, LEVEL, UPGRADES FROM USER_COLLECTIONS WHERE USERID IN \
	#	(SELECT ID FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID={ingame_team_id}))")
	if type(CARD_DATA) == tuple: CARD_DATA=[CARD_DATA]
	if CARD_DATA == None: return user_cards_map, username_map
	for row in CARD_DATA:
		USERID, CARDID, LEVEL, UPGRADES = [row[0],row[4],row[5],row[6]]
		if USERID not in username_map:
			NAME = row[1]
			if type(NAME) == str: NAME=NAME.upper()
			username_map[USERID] = [NAME,row[2],row[3]]
		if USERID not in user_cards_map:
			user_cards_map[USERID]={}
		user_cards_map[USERID][CARDID]=[LEVEL, UPGRADES]
	return user_cards_map, username_map
	
def getTeamWarUpgradesSummary(unique_team_id):
	SUMMARY=[0,0,0,0] #TOTAL CARDS CAPS, UNSPENT, TOTAL USERS COLLECTED, UPDATED
	if unique_team_id == None: return SUMMARY
	if not isValidTeamID(unique_team_id): return SUMMARY
	cards_spent = executeQuery(f"SELECT CARDID, MAX(TOTAL), MAX(UPDATED) FROM TEAMWAR_UPGRADE_CARDS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) and UPDATED > (SELECT MAX(STARTTIME)+3600*24*2-3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME+3600*24*2-3600 < UNIX_TIMESTAMP()) GROUP BY CARDID")
	users_spent = executeQuery(f"SELECT USERID, MAX(TOTAL) AS TOTAL, MAX(UPDATED) FROM TEAMWAR_UPGRADE_USERS WHERE TEAMID=(SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {unique_team_id}) and UPDATED > (SELECT MAX(STARTTIME)+3600*24*2-3600 FROM EVENTS WHERE TYPE=5 AND STARTTIME+3600*24*2-3600 < UNIX_TIMESTAMP()) GROUP BY USERID;")
	if type(cards_spent) == tuple: cards_spent=[cards_spent]
	if cards_spent == None: return SUMMARY
	if type(users_spent) == tuple: users_spent=[users_spent]
	if users_spent == None: return SUMMARY
	for row in cards_spent:
		TOTAL, UPDATED = [row[1],row[2]]
		if UPDATED > SUMMARY[3]: SUMMARY[3]=UPDATED
		SUMMARY[0]+=TOTAL
	for row in users_spent:
		TOTAL, UPDATED = [row[1],row[2]]
		if UPDATED > SUMMARY[3]: SUMMARY[3]=UPDATED
		SUMMARY[2]+=TOTAL
	SUMMARY[1] = SUMMARY[2]-SUMMARY[0]
	return SUMMARY
	
def generate_mmr_history(unique_user_id):
	if unique_user_id == None: return [],[]
	one_year_ago=int(time.time()) - 3600 * 24 * 365
	mmr_history = executeQuery(f"SELECT MMR, UPDATED FROM USERS_HISTORY WHERE USERID=(SELECT USERID FROM USERS WHERE ID={unique_user_id}) and UPDATED > {one_year_ago} ORDER BY UPDATED")
	if type(mmr_history) == tuple: mmr_history=[mmr_history]
	x=[] # Unique NK Levels (ordered)
	y=[] # % of total NKs
	if mmr_history == None: return x,y
	for row in mmr_history:
		mmr=row[0]
		updated=row[1]
		#convert to date: 2015-02-17
		timestamp=time.strftime('%Y-%m-%d', time.localtime(updated))
		x.append(timestamp)
		y.append(mmr)
	return x,y
	
def generate_card_history(card_id):
	data=[]
	target_list=[
		#"Top 250",
		"Top 1000",
		#"MMR 8000-8500",
		"MMR 7000-7500",
		"MMR 6000-6500",
		"MMR 5300-6000",
		"MMR 3900-4600",
		"MMR 2500-3200"
	]
	one_year_ago=int(time.time()) - 3600 * 24 * 365
	card_history = executeQuery(f"SELECT x.TIME, x.NAME, y.PERCENT FROM META_REPORT x \
		JOIN (SELECT CARDSID, PERCENT FROM META_CARDS WHERE CARDID = {card_id}) y \
		WHERE x.TIME > {one_year_ago} AND x.SEARCH = 'Last 1 day' AND x.CARDSID = y.CARDSID")
	if type(card_history) == tuple: card_history=[card_history]
	if card_history == None: return data
	interim_data={} # {NAME : [x_array, y_array], ...}
	for row in card_history:
		cur_time=row[0]
		name=row[1]
		percent=float(row[2])
		if name not in target_list: continue
		#convert to date: 2015-02-17
		timestamp=time.strftime('%Y-%m-%d', time.localtime(cur_time))
		if name not in interim_data:
			interim_data[name]=[[],[]] #[x_array, y_array]
		interim_data[name][0].append(timestamp)
		interim_data[name][1].append(percent)
	for data_name in sorted(interim_data.keys(), reverse=True):
		x_array,y_array=interim_data[data_name]
		data.append(
			dict(
				x=x_array,
				y=y_array,
				name=data_name,
				#marker=dict(
				#	color='rgb(55, 83, 109)'
				#)
			)
		)
	return data
	
def generate_bracket_history(gmtOffset,bracket_id,isTeamID=False):
	data=[]
	if bracket_id == None: return data
	one_year_ago=int(time.time()) - 3600 * 24 * 365
	b_history=None
	if isTeamID:
		b_history = executeQuery(f"SELECT TEAMNAME, RUNS, UPDATED FROM TEAMWAR_BRACKET_HISTORY \
			WHERE BRACKETID = (SELECT MAX(BRACKETID) FROM TEAMWAR_BRACKET WHERE TEAMNAME = (SELECT NAME FROM TEAMS WHERE TEAMID = (SELECT TEAMID FROM TEAMS_REPORT WHERE ID = {bracket_id})))")
	else:
		b_history = executeQuery(f"SELECT TEAMNAME, RUNS, UPDATED FROM TEAMWAR_BRACKET_HISTORY \
			WHERE BRACKETID = {bracket_id}")
	if type(b_history) == tuple: b_history=[b_history]
	if b_history == None: return data
	interim_data={} # {NAME : [x_array, y_array], ...}
	for row in b_history:
		TEAMNAME, RUNS, UPDATED = [row[0],row[1],row[2]]
		if type(TEAMNAME)==str: TEAMNAME = TEAMNAME.upper()
		if type(gmtOffset) == int: UPDATED = UPDATED - gmtOffset * 60
		#convert to datetime: Sat 12:30
		#timestamp=time.strftime('%a %H:%M', time.gmtime(UPDATED))
		#convert to date: 2015-02-17
		timestamp=time.strftime('%Y-%m-%d %H:%M', time.gmtime(UPDATED))
		if TEAMNAME not in interim_data:
			interim_data[TEAMNAME]=[[],[]] #[x_array, y_array]
		interim_data[TEAMNAME][0].append(timestamp)
		interim_data[TEAMNAME][1].append(RUNS)
	#For Each Team - Map the Runs over time, bucket by the hour or minute?
	for data_name in sorted(interim_data.keys(), reverse=True):
		x_array,y_array=interim_data[data_name]
		data.append(
			dict(
				x=x_array,
				y=y_array,
				name=data_name,
				#marker=dict(
				#	color='rgb(55, 83, 109)'
				#)
			)
		)
	return data
	
def getMatchFromID(match_id,my_id):
	match_data=[]
	deck1 = {}
	deck2 = {}
	opt_out = []
	result = executeQuery(f"SELECT TIME, TIMELEFT, MODE, USERID1, NK1, TEAM1, MMR1, SCORE1, RESULT1, DECK1, USERID2, NK2, TEAM2, MMR2, SCORE2, RESULT2, DECK2, DISCONNECT, REGION FROM USER_MATCHES WHERE ID={match_id}")
	if result == None: return match_data
	TIME = result[0]
	TIMELEFT = result[1]
	MODE = result[2]
	USERID1 = result[3]
	NK1 = result[4]
	TEAM1 = result[5]
	MMR1 = result[6]
	SCORE1 = result[7]
	RESULT1 = result[8]
	DECK1 = result[9]
	USERID2 = result[10]
	NK2 = result[11]
	TEAM2 = result[12]
	MMR2 = result[13]
	SCORE2 = result[14]
	RESULT2 = result[15]
	DECK2 = result[16]
	DISCONNECT = result[17]
	REGION = result[18]
	result_deck1 = executeQuery(f"SELECT CARDID1,LEVEL1,CARDID2,LEVEL2,CARDID3,LEVEL3,CARDID4,LEVEL4,CARDID5,LEVEL5,CARDID6,LEVEL6,\
		CARDID7,LEVEL7,CARDID8,LEVEL8,CARDID9,LEVEL9,CARDID10,LEVEL10,CARDID11,LEVEL11,CARDID12,LEVEL12 FROM DECKS_TWO WHERE ID={DECK1}")
	for i in range(12):
		deck1[result_deck1[2*i]]=result_deck1[2*i+1]
	result_deck2 = executeQuery(f"SELECT CARDID1,LEVEL1,CARDID2,LEVEL2,CARDID3,LEVEL3,CARDID4,LEVEL4,CARDID5,LEVEL5,CARDID6,LEVEL6,\
		CARDID7,LEVEL7,CARDID8,LEVEL8,CARDID9,LEVEL9,CARDID10,LEVEL10,CARDID11,LEVEL11,CARDID12,LEVEL12 FROM DECKS_TWO WHERE ID={DECK2}")
	for i in range(12):
		deck2[result_deck2[2*i]]=result_deck2[2*i+1]
	
	#Check for opt-out
	result_optout = executeQuery(f"SELECT USERID, OPTOUT FROM USER_LOGINS WHERE USERID IN ('{USERID1}','{USERID2}')")
	if result_optout != None:
		if type(result_optout)==tuple: result_optout=[result_optout]
		for row in result_optout:
			USERID=row[0]
			OPTOUT=0
			if row[1]!=None: OPTOUT=int(row[1])
			if OPTOUT==1: opt_out.append(USERID)
	users_search=[]
	teams_search=[]
	if USERID1 not in opt_out or my_id == USERID1:
		users_search.append(f"'{USERID1}'")
		teams_search.append(TEAM1)
	if USERID2 not in opt_out or my_id == USERID2:
		users_search.append(f"'{USERID2}'")
		teams_search.append(TEAM2)
	users_map={}
	teams_map={}
	if len(users_search) > 0:
		users_search = ",".join(x for x in users_search)
		result_users = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE USERID IN ({users_search})")
		if result_users != None:
			if type(result_users)==tuple: result_users=[result_users]
			for row in result_users:
				users_map[row[0]]=row[1]
	if len(teams_search) > 0:
		teams_search = ",".join(str(x) for x in teams_search)
		result_teams = executeQuery(f"SELECT TEAMID, NAME FROM TEAMS WHERE TEAMID IN ({teams_search})")
		if result_teams != None:
			if type(result_teams)==tuple: result_teams=[result_teams]
			for row in result_teams:
				teams_map[row[0]]=row[1]
	#General Match Data
	if MODE == 1: MODE="PVP"
	elif MODE == 5: MODE="FF"
	elif MODE == 6: MODE="Challenge"
	elif MODE == 7: MODE="TVT"
	elif MODE == 0: MODE="PVE"
	if DISCONNECT==None: DISCONNECT="No"
	elif DISCONNECT==1: DISCONNECT="Yes"
	else: DISCONNECT="No"
	if REGION==None: REGION="Unknown"
	else: REGION=REGION.upper()
	match_data.append([TIME,TIMELEFT,MODE,DISCONNECT,REGION,SCORE1,SCORE2])
	#User Specific Match Data
	if RESULT1==1: RESULT1 = "WIN"
	elif RESULT1==0: RESULT1 = "LOSS"
	elif RESULT1==3: RESULT1 = "DISCONNECT"
	else: RESULT1 = "DRAW"
	username1="Hidden"
	if USERID1 in users_map:
		username1 = users_map[USERID1]
		if type(username1) == str: username1 = username1.upper()
	teamname1="Hidden"
	if TEAM1 in teams_map:
		teamname1 = teams_map[TEAM1]
		if type(teamname1) == str: teamname1 = teamname1.upper()
	match_data.append([username1,teamname1,NK1,MMR1,RESULT1,deck1])
	if RESULT2==1: RESULT2 = "WIN"
	elif RESULT2==0: RESULT2 = "LOSS"
	elif RESULT2==3: RESULT2 = "DISCONNECT"
	else: RESULT2 = "DRAW"
	username2="Hidden"
	if USERID2 in users_map:
		username2 = users_map[USERID2]
		if type(username2) == str: username2 = username2.upper()
	teamname2="Hidden"
	if TEAM2 in teams_map:
		teamname2 = teams_map[TEAM2]
		if type(teamname2) == str: teamname2 = teamname2.upper()
	match_data.append([username2,teamname2,NK2,MMR2,RESULT2,deck2])
	return match_data
	
def getBestDeck(myThemes=[],myCards=[],oppThemes=[],oppCards=[],myBlacklist=[]):
	FIGHT = 0 #3-6 fighters
	TANK = 0 #0-2 tank
	ASS = 0 #1-2 assassins
	RANGE = 0 #3-4 range
	SPELL = 0 #1-3 spells
	TOWER = 0
	counter_themes = []
	if len(oppCards) > 0:
		counter_themes=findThemes(myCards)
		if 'neu' in counter_themes: counter_themes.remove('neu')
		if 'neu' in counter_themes: counter_themes.remove('neu')
	for theme in oppThemes:
		if len(counter_themes) == 2: break
		counter_themes.append(theme)
	best_themes = []
	if len(myCards) > 0:
		best_themes=findThemes(myCards)
		if 'neu' in best_themes: best_themes.remove('neu')
		if 'neu' in best_themes: best_themes.remove('neu')
	for theme in myThemes:
		if len(best_themes) == 2: break
		best_themes.append(theme)
	if len(best_themes) < 2:
		result = None
		if len(counter_themes) > 0:
			SEARCH = " OR ".join(f"THEME2 = '{theme}'" for theme in counter_themes)
			result = executeQuery(f"SELECT THEME1,WIN,THEME2 FROM WINRATE_THEMES WHERE {SEARCH} ORDER BY WIN DESC")
		else:
			result = executeQuery("SELECT THEME1,WIN FROM WINRATE_THEMES WHERE THEME2 IS NULL ORDER BY WIN DESC")
		for row in result:
			theme,win = [row[0],row[1]]
			if theme == 'neu' or theme in best_themes: continue
			best_themes.append(theme)
			if len(best_themes) == 2: break
	best_themes.append('neu')
	result = None
	SEARCH = " OR ".join(f"THEME = '{theme}'" for theme in best_themes)
	failed_search = True
	if len(oppCards) > 0:
		#BUILD A COUNTER DECK
		COUNTER_SEARCH = " OR ".join(f"CARDID2 = {card_id}" for card_id in oppCards)
		interim_result = executeQuery(f"SELECT CARDID1,WIN,CARDID2 FROM WINRATE_CARDS WHERE ({COUNTER_SEARCH}) AND CARDID1 IN (SELECT ID FROM CARDS WHERE {SEARCH})")
		card_winrate_map = {} # {card_id : [winrate1, winrate2, ...], ...}
		if result != None: 
			for row in interim_result:
				card_id, win = [row[0],row[1]]
				if card_id not in card_winrate_map:
					card_winrate_map[card_id]=[]
				card_winrate_map[card_id].append(float(win))
			card_win_rates=[]
			for key in card_winrate_map.keys():
				avg_win_rate = round(sum(card_winrate_map[key]) / len(card_winrate_map[key]),2)
				card_win_rates.append([key,avg_win_rate])
			#result = [[card_id, avg win rate], ...] -- SORTED by win rate
			result = sorted(card_win_rates, key=lambda x: (x[1], x[0]), reverse=True)
			failed_search=False
	if failed_search:
		#BUILD A GENERAL DECK
		result = executeQuery(f"SELECT CARDID1,WIN FROM WINRATE_CARDS WHERE CARDID2 IS NULL AND CARDID1 IN (SELECT ID FROM CARDS WHERE {SEARCH}) ORDER BY WIN DESC")

	#If they added cards already
	for card_id in myCards:
		card_type = getCardType(card_id)
		if card_type == 'fight': FIGHT+=1
		elif card_type == 'tank': TANK+=1
		elif card_type == 'ass': ASS+=1
		elif card_type == 'range': RANGE+=1
		elif card_type == 'spell': SPELL+=1
		elif card_type == 'tower': TOWER+=1
		
	if result == None: return myCards
	
	for row in result:
		card_id, win = [row[0],row[1]]
		if card_id in myCards or card_id in myBlacklist: continue
		card_type = getCardType(card_id)
		if card_type == 'fight' and FIGHT < 7:
			FIGHT+=1
			myCards.append(card_id)
		elif card_type == 'tank' and TANK < 2:
			TANK+=1
			myCards.append(card_id)
		elif card_type == 'ass' and ASS < 3:
			ASS+=1
			myCards.append(card_id)
		elif card_type == 'range' and RANGE < 4:
			RANGE+=1
			myCards.append(card_id)
		elif card_type == 'spell' and SPELL < 3:
			SPELL+=1
			myCards.append(card_id)
		elif card_type == 'tower':
			TOWER+=1
			myCards.append(card_id)
		if len(myCards) == 12: break
	return myCards
	
def get_home_live_match_data():
	QUERIES = ''
	QUERIES+="SELECT COUNT(DISTINCT userid1) FROM user_matches;"
	QUERIES+="SELECT COUNT(*) FROM user_matches WHERE TIME > UNIX_TIMESTAMP() - 3600 * 24 * 7;"
	QUERIES+="SELECT COUNT(*) FROM user_matches WHERE TIME > UNIX_TIMESTAMP() - 3600 * 24;"
	QUERIES+="SELECT x.ID,x.MMR1,x.MMR2,y.CARDID1,y.CARDID2,y.CARDID3,y.CARDID4,y.CARDID5,y.CARDID6,y.CARDID7,y.CARDID8,y.CARDID9,y.CARDID10,y.CARDID11,y.CARDID12,\
			z.CARDID1,z.CARDID2,z.CARDID3,z.CARDID4,z.CARDID5,z.CARDID6,z.CARDID7,z.CARDID8,z.CARDID9,z.CARDID10,z.CARDID11,z.CARDID12 FROM user_matches x\
			JOIN DECKS_TWO y\
			JOIN DECKS_TWO z\
		WHERE x.DECK1 = y.ID AND x.DECK2 = z.ID ORDER BY x.TIME DESC LIMIT 7;"
	result = executeQuery(QUERIES,multiple=True)
	index = 0
	match_data=[]
	for elem in result:
		if len(elem) == 1:
			if index == 0: CONTRIBUTORS=elem[0][0]
			elif index == 1: LASTSEVENDAYS=elem[0][0]
			elif index == 2: TODAYS=elem[0][0]
		else:
			for row in elem:
				ID = row[0]
				MMR1 = row[1]
				MMR2 = row[2]
				deck1=[]
				deck2=[]
				for i in range(3,27):
					if i > 14: deck2.append(row[i])
					else: deck1.append(row[i])
				themes1=findThemes(deck1)
				themes2=findThemes(deck2)
				match_data.append([ID,MMR1,themes1,MMR2,themes2])
		index+=1
	return [LASTSEVENDAYS,TODAYS,CONTRIBUTORS,match_data]
	
def getThemeMatchupsData():
	result = executeQuery("SELECT THEME1, THEME2, WIN FROM WINRATE_THEMES WHERE THEME2 IS NOT NULL")
	data_set={}
	columns=[]
	for row in result:
		THEME1, THEME2, WIN = row[0],row[1],row[2]
		if THEME1 not in columns: columns.append(THEME1)
		VERSUS = f"{THEME1} vs {THEME2}"
		data_set[VERSUS]=WIN
	return data_set,columns
	
def getHomeBestDeck(meta_name):
	search = "Last 1 day"
	result = executeQuery(f"SELECT z.CARDID1,z.CARDID2,z.CARDID3,z.CARDID4,z.CARDID5,z.CARDID6,z.CARDID7,z.CARDID8,z.CARDID9,z.CARDID10,z.CARDID11,z.CARDID12 from META_REPORT x\
			JOIN META_THEMES y\
			JOIN DECKS_TWO z\
		WHERE x.SEARCH='{search}' AND x.NAME='{meta_name}' AND x.TIME IN \
			(select MAX(TIME) from META_REPORT WHERE SEARCH='{search}' AND NAME='{meta_name}') AND y.THEMESID = x.THEMESID AND z.ID = y.DECKID ORDER BY y.PERCENT DESC LIMIT 1")
	return [result[i] for i in range(12)]
	
def getOutfitData(unique_user_id):
	if unique_user_id == None or unique_user_id == '': return None,None,None
	result = executeQuery(f"SELECT SKIN,FEMALE,GEAR1,A1,B1,GEAR2,A2,B2,GEAR3,A3,B3,OUTFIT1,C1,OUTFIT2,C2,OUTFIT3,C3,OUTFIT4,C4,OUTFIT5,C5,OUTFIT6,C6,OUTFIT7,C7 FROM USERS WHERE ID = {unique_user_id}")
	if result[0] == None: return None,None,None
	SKIN = "%x" % result[0]
	FEMALE = int(result[1]) == 1
	GEAR_DATA=[]
	OUTFIT_DATA=[]
	for i in range(2,11,3):
		if result[i] == None: continue
		GEAR_DATA.append([result[i],result[i+1],result[i+2]])
	for i in range(11,25,2):
		if result[i] == None: continue
		OUTFIT_DATA.append([result[i],result[i+1]])
	return OUTFIT_DATA,GEAR_DATA,SKIN
	
def getMissingFromMatchesToUsers():
	missing_users = []
	result = executeQuery("SELECT DISTINCT USERID2 FROM USER_MATCHES\
		WHERE USERID2 NOT IN (SELECT USERID FROM USERS)")
	if result == None: return missing_users
	if type(result) == tuple: result = [result]
	for row in result:
		missing_users.append(row[0])
	return missing_users
	
def getMissingFromUsersToTeamMembers():
	missing_users = []
	result = executeQuery("SELECT DISTINCT USERID FROM USERS WHERE USERID NOT IN (SELECT USERID FROM TEAM_MEMBERS)")
	if result == None: return missing_users
	if type(result) == tuple: result = [result]
	for row in result:
		missing_users.append(row[0])
	return missing_users
	
def getMissingFromTeamMembersToUsers():
	missing_users = []
	result = executeQuery("SELECT DISTINCT USERID FROM TEAM_MEMBERS WHERE USERID NOT IN (SELECT USERID FROM USERS)")
	if result == None: return missing_users
	if type(result) == tuple: result = [result]
	for row in result:
		missing_users.append(row[0])
	return missing_users
	
def weeklyBackupDatabase():
	cur_time = time.strftime('%Y%m%d_%H%M', time.localtime(time.time()))
	backupName = f"decktracker_weekly_{cur_time}"
	executeQuery(f"BACKUP DATABASE decktracker TO DISK = 'C:\\backups\\{backupName}'")
	
def dailyBackupDatabase():
	backupName = "decktracker_daily"
	executeQuery(f"BACKUP DATABASE decktracker TO DISK = 'C:\\backups\\{backupName}' WITH DIFFERENTIAL")
	