import datetime
from dateutil import relativedelta
### Each user-id can only be registered to 1 account.


from flask import Flask, request, make_response
from waitress import serve
import mysql.connector as mariadb
import threading
import json
import DATABASE
import time, sys
import traceback
import EMAILER
import math

"""
>>> print(dir(sqlite3.Cursor))
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__lt__', '__ne__', '__new__', '__next__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'arraysize', 'close', 'connection', 'description', 'execute', 'executemany', 'executescript', 'fetchall', 'fetchmany', 'fetchone', 'lastrowid', 'row_factory', 'rowcount', 'setinputsizes', 'setoutputsize']
"""

DeckLock = threading.Condition()
BracketLock = threading.Condition()

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
	mariadb_connection.close()
	query=query.replace('\t',' ').replace('\n',' ')
	if debug: print(f"executeQuery query {query} -> result {result}")
	elif not quiet: print(f"executeQuery query {query}")
	time.sleep(0.05)
	return result
	
def executeSanitize(query, name, name2, commit=False, debug=False, quiet = False):
	mariadb_connection = mariadb.connect(
							user='root',
							password='password',
							database='decktracker')
	cursor = mariadb_connection.cursor()
	result=None
	try:
		cursor.execute(query, { 'name': name, 'name2': name2 })
		if commit: mariadb_connection.commit()
		else:
			result = cursor.fetchall()
			if len(result) == 0: result=None
			elif len(result) == 1: result=result[0]
	except:
		print(f"[ERROR] Failed Query: {query}, where NAME = '{name}'")
		traceback.print_exc()
	mariadb_connection.close()
	query=query.replace('\t',' ').replace('\n',' ')
	if debug: print(f"executeQuery query {query} -> result {result}")
	elif not quiet: print(f"executeQuery query {query}")
	time.sleep(0.05)
	return result
	
def executeMany(query, commit=False):
	mariadb_connection = mariadb.connect(
							user='root',
							password='password',
							database='decktracker')
	cursor = mariadb_connection.cursor()
	result_list=[]
	for q in query:
		result=None
		try:
			cursor.execute(q)
			if commit: mariadb_connection.commit()
			else:
				result = cursor.fetchall()
				if len(result) == 0: result=None
				elif len(result) == 1: result=result[0]
		except:
			print(f"[ERROR] Failed Query: {query}")
			traceback.print_exc()
		q = q.replace('\t',' ').replace('\n',' ')
		#print(f"executeMany query {q} -> result {result}")
		print(f"executeMany query {q}")
		result_list.append(result)
	mariadb_connection.close()
	time.sleep(0.05)
	return result_list
	
def removeCharactersOutOfRange(word):
	char_list = [word[j] for j in range(len(word)) if ord(word[j]) in range(65536)]
	new_word=''
	for j in char_list:
		new_word=new_word+j
	return new_word
	
def insertDeck(deck):
	if deck == None: return None
	deck_id=0
	deck_length=len(deck)
	deck_str=",".join(str(x) for x in deck)
	#Check if the deck is already in the table!
	result=executeQuery(f"select DECKID from DECKS\
		where CARDID in ({deck_str})\
		group by DECKID\
		having count(distinct CARDID) = {deck_length};\
		")
	if result != None:
		deck_id=result[0]
		if type(deck_id) == tuple: deck_id=deck_id[0]
		#Because we can have multiple decks now, with matches having levels.
	else: #Insert the deck
		global DeckLock
		DeckLock.acquire()
		deck_id=getNewIndex("DECKS","DECKID")
		#(SELECT MAX(y.DECKID)+1 FROM DECKS y)
		ALL_DECK_DATA=[]
		for card_id in deck:
			ALL_DECK_DATA.append(f"({deck_id},{card_id})")
		ALL_DECK_DATA=",".join(x for x in ALL_DECK_DATA)
		executeQuery(f"INSERT INTO DECKS (\
			DECKID,CARDID\
			) VALUES {ALL_DECK_DATA}", True)
		DeckLock.notify_all()
		DeckLock.release()
	return deck_id
		
def insertDeckWithLevels(deck):
	if deck == None: return None
	deck_length=len(deck)
	if len(deck) != 12: return None
	#Insert the deck
	global DeckLock
	DeckLock.acquire()
	deck_id=getNewIndex("DECKS","DECKID")
	#(SELECT MAX(y.DECKID)+1 FROM DECKS y)
	ALL_DECK_DATA=[]
	for card_id in deck.keys():
		level = "%.2f" % deck[card_id]
		ALL_DECK_DATA.append(f"({deck_id},{card_id},{level})")
	ALL_DECK_DATA=",".join(x for x in ALL_DECK_DATA)
	executeQuery(f"INSERT INTO DECKS (\
		DECKID,CARDID,LEVEL\
		) VALUES {ALL_DECK_DATA}", True)
	DeckLock.notify_all()
	DeckLock.release()
	return deck_id

#Update all META_THEMES.DECKID AND USER_MATCHES.DECK1 AND USER_MATCHES.DECK2
def deepUpdateDecks():
	for TABLE, COLUMN in [["META_THEMES","DECKID"],["USER_MATCHES","DECK1"],["USER_MATCHES","DECK2"],["TEAM_MEMBERS","DECKID"]]:
		print(f"[INFO]: {TABLE} In Progress...")
		already_updated=[]
		ALL_UPDATED_DECKIDS=[]
		result=executeQuery(f"SELECT DISTINCT {COLUMN} FROM {TABLE} WHERE {COLUMN} IS NOT NULL",quiet=True)
		index=0
		for row in result:
			#grab the deck's cards + levels
			old_deckid = row[0]
			result_two=executeQuery(f"SELECT CARDID, LEVEL FROM DECKS WHERE DECKID = {old_deckid}",quiet=True)
			if result_two == None:
				print(f"[ERROR]: DECK FROM {TABLE} not found in DECKS, DECKID={old_deckid}")
				continue
			deck = {}
			for row in result_two:
				cardid=row[0]
				level=row[1]
				deck[cardid]=level
			#get the new deckid with insertDeckWithLevelsTwo
			new_deckid = insertDeckWithLevelsTwo(deck)
			if new_deckid == None:
				print(f"[ERROR]: DECK FROM {TABLE} is not 12 cards, DECKID={old_deckid}")
				continue
			#update the TABLE to point to the new DECKID.
			if old_deckid not in already_updated:
				already_updated.append(old_deckid)
				ALL_UPDATED_DECKIDS.append(f"UPDATE {TABLE} SET {COLUMN}={new_deckid} WHERE {COLUMN}={old_deckid}")
			percent_complete = int(100 * float(index) / len(result))
			if percent_complete % 5 == 0:
				print(f"{percent_complete} percent...")
			index+=1
		executeMany(ALL_UPDATED_DECKIDS,True)
		print(f"[INFO]: {TABLE} Complete.")
		
def insertDeckWithLevelsTwo(deck,isList=False):
	if deck == None: return None
	deck_length=len(deck)
	if len(deck) < 12: return None
	if isList: deck = { i : None for i in deck }
	if len(deck) > 12:
		tmp_deck = {}
		index = 0
		for key in deck:
			if index < 12:
				tmp_deck[key]=deck[key]
			index+=1
		deck = tmp_deck
	#Sort the deck numerically
	sorted_keys = sorted(deck.keys())
	SEARCH = "WHERE"
	index = 1
	for key in sorted_keys:
		if index != 1:
			SEARCH += " AND"
		LEVEL = "IS NULL"
		if deck[key] != None:
			LEVEL = "= %.2f" % deck[key]
		SEARCH += f" CARDID{index} = {key} AND LEVEL{index} {LEVEL}"
		index+=1
	result=executeQuery(f"SELECT ID FROM DECKS_TWO {SEARCH}",quiet=True)
	deck_id=0
	if result != None:
		if type(result) == tuple: result = result[0]
		deck_id=result
	else: #Insert the deck
		global DeckLock
		DeckLock.acquire()
		deck_id=getNewIndex("DECKS_TWO")
		cardid_and_levels=[]
		for key in sorted_keys:
			LEVEL = "NULL"
			if deck[key] != None:
				LEVEL = "%.2f" % deck[key]
			cardid_and_levels.extend([key,LEVEL])
		INSERT_STRING = "INSERT INTO DECKS_TWO (ID,"
		INSERT_STRING += ",".join(f"CARDID{i},LEVEL{i}" for i in range(1,13))
		INSERT_STRING += f") VALUES ({deck_id},"
		INSERT_STRING += ",".join(f"{i}" for i in cardid_and_levels)
		INSERT_STRING += ")"
		executeQuery(INSERT_STRING, True, quiet=True)
		DeckLock.notify_all()
		DeckLock.release()
	return deck_id
	
def getBracketID(team_names):
	if len(team_names) == 0: return None
	bracket_id=None
	bracket_length=len(team_names)
	team_names_cleaned=[]
	for team in team_names:
		clean_team_name=removeCharactersOutOfRange(team).replace("'","''").lower()
		team_names_cleaned.append(clean_team_name)
	bracket_str=",".join("'"+x+"'" for x in team_names_cleaned)
	OLDEST=int(time.time()) - 3600 * 24 * 3 # Within 3 days
	#Check if the teams are already in the table!
	result=executeQuery(f"select BRACKETID from TEAMWAR_BRACKET\
		where UPDATED > {OLDEST} AND\
		TEAMNAME in ({bracket_str}) group by BRACKETID\
		having count(distinct TEAMNAME) = {bracket_length};")
	if result != None: bracket_id=result[0]
	return bracket_id
	
def insertAllCards():
	#Insert all the cards
	ALL_CARD_DATA=[]
	for key in DATABASE.DECK_MAP.keys():
		ID=key
		result=executeQuery(f"SELECT NAME from CARDS WHERE ID={ID}")
		if result != None: continue #Skip it. It's already added
		NAME=DATABASE.DECK_MAP[key][0].replace("'","''")
		COST=DATABASE.DECK_MAP[key][1]
		TYPE=DATABASE.DECK_MAP[key][2]
		THEME=DATABASE.DECK_MAP[key][3]
		RARITY=DATABASE.DECK_MAP[key][4]
		KEYWORDS=""
		if len(DATABASE.DECK_MAP[key])>5:
			KEYWORDS=DATABASE.DECK_MAP[key][5]
			if len(DATABASE.DECK_MAP[key])>6:
				KEYWORDS+=","+DATABASE.DECK_MAP[key][6]
				if len(DATABASE.DECK_MAP[key])>7:
					KEYWORDS+=","+DATABASE.DECK_MAP[key][7]
		ALL_CARD_DATA.append(f"({ID},'{NAME}',{COST},'{TYPE}','{THEME}','{RARITY}','{KEYWORDS}')")
	ALL_CARD_DATA=",".join(x for x in ALL_CARD_DATA)
	executeQuery(f"INSERT INTO CARDS (ID,NAME,COST,TYPE,THEME,RARITY,KEYWORDS) VALUES {ALL_CARD_DATA};", True)

def getNewIndex(table, target="ID"):
	index=executeQuery(f"SELECT max({target}) from {table}",quiet=True)
	what_type=type(index)
	if index == None: index=0
	elif type(index) == tuple:
		index=index[0]
		if index == None:
			index=1
		else:
			index+=1
	elif type(index) == int: index=index+1
	else:
		print(f"Critical Error: Unknown max {target} from {table}")
		sys.exit(1)
	return index
	
	
###USERS###

def insertUsers(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	USERIDS=result["USERIDS"]
	HINT=result["HINT"]
	WHERE=None
	if HINT != None:
		if "RANK" in HINT:
			rank=HINT["RANK"]
			WHERE=f"WHERE RANK <= {rank} AND RANK <> 0"
		if "TEAM" in HINT:
			team=HINT["TEAM"]
			WHERE=f"WHERE TEAMID = {team}"
	user_name_map={}
	if WHERE != None:
		result = executeQuery(f"SELECT USERID, NAME FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS {WHERE})")
		if type(result) == tuple: result=[result]
		if result != None:
			for row in result:
				user_id=row[0]
				name=row[1]
				user_name_map[user_id]=name
	ALL_UPDATED_NAMES=[]
	ALL_NEW_NAMES=[]
	for USERID in USERIDS.keys():
		NAME=removeCharactersOutOfRange(USERIDS[USERID]).lower()
		cur_name=None
		if USERID in user_name_map:
			cur_name=user_name_map[USERID]
		else:
			result = executeQuery(f"SELECT NAME FROM USERS WHERE USERID = '{USERID}'")
			if result != None: cur_name=result[0]
		if cur_name == None: #Add if they don't exist
			NAME=NAME.replace("'","''")
			ALL_NEW_NAMES.append(f"('{USERID}','{NAME}')")
		elif cur_name != NAME: #Update Name if it doesn't match
			NAME=NAME.replace("'","''")
			ALL_UPDATED_NAMES.append(f"UPDATE USERS \
				SET NAME = '{NAME}'\
				WHERE USERID = '{USERID}'\
				")
	if len(ALL_UPDATED_NAMES) > 0:
		executeMany(ALL_UPDATED_NAMES, True)
	if len(ALL_NEW_NAMES) > 0:
		ALL_NEW_NAMES = ",".join(x for x in ALL_NEW_NAMES)
		executeQuery(f"INSERT INTO USERS (\
			USERID,NAME\
			) VALUES {ALL_NEW_NAMES}", True)		
	return getNewIndex("USERS")
	
def insertUsersPlatform(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	USERIDS=result["USERIDS"]
	HINT=result["HINT"]
	WHERE=None
	if HINT != None:
		if "RANK" in HINT:
			rank=HINT["RANK"]
			WHERE=f"WHERE RANK <= {rank} AND RANK <> 0"
		if "TEAM" in HINT:
			team=HINT["TEAM"]
			WHERE=f"WHERE TEAMID = {team}"
	user_name_map={}
	user_plat_map={}
	if WHERE != None:
		result = executeQuery(f"SELECT USERID, NAME, PLATFORM FROM USERS WHERE USERID IN (SELECT USERID FROM TEAM_MEMBERS {WHERE})")
		if type(result) == tuple: result=[result]
		if result != None:
			for row in result:
				user_id=row[0]
				name=row[1]
				plat=row[2]
				user_name_map[user_id]=name
				user_plat_map[user_id]=plat
	ALL_UPDATED_NAMES=[]
	ALL_NEW_NAMES=[]
	for USERID in USERIDS.keys():
		NAME,PLATFORM=USERIDS[USERID]
		NAME=removeCharactersOutOfRange(NAME).lower()
		cur_name=None
		cur_plat=None
		if USERID in user_name_map:
			cur_name=user_name_map[USERID]
			cur_plat=user_plat_map[USERID]
		else:
			result = executeQuery(f"SELECT NAME,PLATFORM FROM USERS WHERE USERID = '{USERID}'")
			if result != None:
				cur_name=result[0]
				cur_plat=result[1]
		if cur_name == None: #Add if they don't exist
			NAME=NAME.replace("'","''")
			ALL_NEW_NAMES.append(f"('{USERID}','{NAME}','{PLATFORM}')")
		elif cur_name != NAME or cur_plat != PLATFORM: #Update Name if it doesn't match
			NAME=NAME.replace("'","''")
			ALL_UPDATED_NAMES.append(f"UPDATE USERS \
				SET NAME = '{NAME}', PLATFORM = '{PLATFORM}'\
				WHERE USERID = '{USERID}'\
				")
	if len(ALL_UPDATED_NAMES) > 0:
		executeMany(ALL_UPDATED_NAMES, True)
	if len(ALL_NEW_NAMES) > 0:
		ALL_NEW_NAMES = ",".join(x for x in ALL_NEW_NAMES)
		executeQuery(f"INSERT INTO USERS (\
			USERID,NAME,PLATFORM\
			) VALUES {ALL_NEW_NAMES}", True)
	return getNewIndex("USERS")
	
def updatePastUserNames():
	executeQuery(f"INSERT INTO USERS_NAMES_PAST (USERID,NAME)\
		SELECT DISTINCT st.USERID, st.NAME\
		FROM USERS st WHERE NOT EXISTS\
			(SELECT 1 FROM USERS_NAMES_PAST t2\
			WHERE t2.USERID = st.USERID\
			AND t2.NAME = st.NAME)", True)
	return getNewIndex("USERS_NAMES_PAST")
	
def updatePastTeams():
	executeQuery(f"INSERT INTO USERS_TEAMS_PAST (USERID,TEAMID)\
		SELECT DISTINCT st.USERID, st.TEAMID\
		FROM TEAM_MEMBERS st WHERE st.TEAMID <> 0 AND NOT EXISTS\
			(SELECT 1 FROM USERS_TEAMS_PAST t2\
			WHERE t2.USERID = st.USERID\
			AND t2.TEAMID = st.TEAMID)", True)
	return getNewIndex("USERS_TEAMS_PAST")
	
def insertUserDetails(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	TEAMID=result["TEAMID"] #May or may not be right
	if TEAMID == None: TEAMID = 0
	USERID=result["USERID"]
	USER_DETAILS=result["USER_DETAILS"] # { role: role, mmr: mmr, ... }
	DECK=result["DECK"] # [ CARDIDS, ...]
	UPDATED=int(time.time())
	DECKID=insertDeckWithLevelsTwo(DECK,True)
	if DECKID == None: DECKID = 'NULL'
	LASTRANK=None
	if "RANK" in USER_DETAILS:
		LASTRANK=USER_DETAILS["RANK"]
	
	found_user=False
	result = executeQuery(f"SELECT TEAMID, RANK FROM TEAM_MEMBERS WHERE USERID = '{USERID}'")
	if result != None:
		if TEAMID == 0: TEAMID=result[0]
		CUR_RANK=result[1]
		if CUR_RANK != None and LASTRANK != CUR_RANK: LASTRANK=CUR_RANK
		found_user=True
	if found_user:
		UPDATES=[]
		UPDATES.append(f"DECKID = {DECKID}")
		UPDATES.append(f"UPDATED = {UPDATED}")
		UPDATES.append(f"DECKUPDATED = {UPDATED}")
		UPDATES.append(f"TEAMID = {TEAMID}")
		UPDATES.append(f"LASTRANK = {LASTRANK}")
		for key in USER_DETAILS.keys():
			if key == 'OUTFIT': continue
			value=USER_DETAILS[key]
			UPDATES.append(f"{key} = {value}")
		UPDATES=",".join(x for x in UPDATES)
		executeQuery(f"UPDATE TEAM_MEMBERS \
			SET {UPDATES}\
			WHERE USERID='{USERID}'\
			", True)
	else:
		COLUMNS=[]
		VALUES=[]
		COLUMNS.append("DECKID")
		VALUES.append(DECKID)
		COLUMNS.append("UPDATED")
		VALUES.append(UPDATED)
		COLUMNS.append("DECKUPDATED")
		VALUES.append(UPDATED)
		COLUMNS.append("LASTRANK")
		VALUES.append(LASTRANK)
		for key in USER_DETAILS.keys():
			if key == 'OUTFIT': continue
			COLUMNS.append(key)
			VALUES.append(USER_DETAILS[key])
		COLUMNS=",".join(x for x in COLUMNS)
		VALUES=",".join(str(x) for x in VALUES)
		executeQuery(f"INSERT INTO TEAM_MEMBERS (\
			TEAMID,USERID,{COLUMNS}\
			) VALUES (\
			{TEAMID},'{USERID}',{VALUES}\
			)", True)
	#Add to the user history
	COLUMNS=[]
	VALUES=[]
	COLUMNS.append("UPDATED")
	VALUES.append(UPDATED)
	for key in USER_DETAILS.keys():
		if key in ["JOINDATE","MMR","MAXMMR","NKLEVEL","WINS_PVP","WINS_TW","WINS_CHLG","WINS_PVE","WINS_FF","WINS_FFP","WINS_PVPP","TW_TOKENS","DONATED_ALL"]:
			COLUMNS.append(key)
			VALUES.append(USER_DETAILS[key])
	COLUMNS=",".join(x for x in COLUMNS)
	VALUES=",".join(str(x) for x in VALUES)
	executeQuery(f"INSERT INTO USERS_HISTORY (\
		TEAMID,USERID,{COLUMNS}\
		) VALUES (\
		{TEAMID},'{USERID}',{VALUES}\
		)", True)
	if "OUTFIT" in USER_DETAILS and 'skin_color' in USER_DETAILS["OUTFIT"] and\
		'outfit' in USER_DETAILS["OUTFIT"] and 'active_gear' in USER_DETAILS["OUTFIT"] and\
		'female' in USER_DETAILS["OUTFIT"] and len(USER_DETAILS["OUTFIT"]['active_gear']) > 0 and\
		len(USER_DETAILS["OUTFIT"]['outfit']) > 0:
		skin = USER_DETAILS["OUTFIT"]['skin_color']
		female = 1 if USER_DETAILS["OUTFIT"]['female'] else 0
		UPDATES=[]
		UPDATES.append(f"SKIN = {skin}")
		UPDATES.append(f"FEMALE = {female}")
		gear_count = 0
		for i in range(len(USER_DETAILS["OUTFIT"]['active_gear'])):
			result = USER_DETAILS["OUTFIT"]['active_gear'][i]
			UPDATES.append(f"GEAR{i+1} = {result[0]}")
			UPDATES.append(f"A{i+1} = {result[1]}")
			UPDATES.append(f"B{i+1} = {result[2]}")
			gear_count += 1
		#CLEAR the remaining slots
		for i in range(gear_count, 3):
			UPDATES.append(f"GEAR{i+1} = NULL")
			UPDATES.append(f"A{i+1} = NULL")
			UPDATES.append(f"B{i+1} = NULL")
		outfit_count = 0
		for i in range(len(USER_DETAILS["OUTFIT"]['outfit'])):
			result = USER_DETAILS["OUTFIT"]['outfit'][i]
			UPDATES.append(f"OUTFIT{i+1} = {result[0]}")
			UPDATES.append(f"C{i+1} = {result[1]}")
			outfit_count += 1
		#CLEAR the remaining slots
		for i in range(outfit_count, 7):
			UPDATES.append(f"OUTFIT{i+1} = NULL")
			UPDATES.append(f"C{i+1} = NULL")
		
		UPDATES=",".join(x for x in UPDATES)
		executeQuery(f"UPDATE USERS SET {UPDATES} \
			WHERE USERID='{USERID}'", True)
	return getNewIndex("TEAM_MEMBERS")
	
def insertLoginUsers(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	USERID=result["USERID"]
	OKTAID=result["OKTAID"]
	found_userid = executeQuery(f"SELECT * FROM USERS WHERE USERID = '{USERID}'")
	#Only add if the userid was verified first!
	if found_userid != None:
		#Only add if the userid is not already claimed!
		userid_claimed = executeQuery(f"SELECT OKTAID FROM USER_LOGINS WHERE USERID = '{USERID}'")
		if userid_claimed == None: #No Duplicates!
			userid_count = executeQuery(f"SELECT COUNT(USERID) FROM USER_LOGINS WHERE OKTAID = '{OKTAID}'")
			userid_count=userid_count[0]
			MAIN=0
			if userid_count == 0: MAIN=1
			executeQuery(f"INSERT INTO USER_LOGINS (\
				OKTAID,USERID,MAIN\
				) VALUES (\
				'{OKTAID}','{USERID}',{MAIN}\
				)", True)
		else: return "userid_claimed"
	return getNewIndex("USER_LOGINS")

def setPrimaryAccount(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	INDEX=result["INDEX"]
	OKTAID=result["OKTAID"]
	
	found = executeQuery(f"SELECT USERID, MAIN FROM USER_LOGINS WHERE OKTAID = '{OKTAID}'")
	if type(found) == tuple: found = [found]
	if found != None and len(found) > INDEX: #Update only
		index=0
		for row in found:
			USERID=row[0]
			MAIN=0
			if row[1] != None: MAIN=int(row[1])
			if index == INDEX:
				executeQuery(f"UPDATE USER_LOGINS \
					SET MAIN = 1\
					WHERE OKTAID = '{OKTAID}' AND USERID='{USERID}'\
					", True)
			elif MAIN == 1:
				executeQuery(f"UPDATE USER_LOGINS \
					SET MAIN = 0\
					WHERE OKTAID = '{OKTAID}' AND USERID='{USERID}'\
					", True)
			index+=1
	return getNewIndex("USER_LOGINS")
	
def deleteAccount(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	INDEX=result["INDEX"]
	OKTAID=result["OKTAID"]
	
	found = executeQuery(f"SELECT USERID FROM USER_LOGINS WHERE OKTAID = '{OKTAID}'")
	if type(found) == tuple: found=[found]
	if found != None and len(found) > INDEX: #Delete only
		index=0
		for row in found:
			USERID=row[0]
			if index == INDEX:
				executeQuery(f"DELETE FROM USER_LOGINS \
					WHERE OKTAID = '{OKTAID}' AND USERID='{USERID}'\
					", True)
			index+=1
	return getNewIndex("USER_LOGINS")
	
def doCleanup():
	CUR_TIME = int(time.time())
	SIXTY_DAYS_AGO = CUR_TIME - 3600 * 24 * 60
	executeQuery(f"DELETE FROM TEAM_DONATIONS WHERE UPDATED < {SIXTY_DAYS_AGO}",True)
	executeQuery(f"DELETE FROM TEAM_REQUESTS WHERE UPDATED < {SIXTY_DAYS_AGO}",True)
	executeQuery(f"DELETE FROM TEAMWAR_UPGRADE_CARDS WHERE UPDATED < {SIXTY_DAYS_AGO}",True)
	executeQuery(f"DELETE FROM TEAMWAR_UPGRADE_USERS WHERE UPDATED < {SIXTY_DAYS_AGO}",True)
	
	#Cleanup Meta Report
	executeQuery(f"DELETE FROM META_REPORT WHERE TIME < {SIXTY_DAYS_AGO}",True)
	executeQuery(f"DELETE FROM META_CARDS WHERE CARDSID NOT IN (SELECT CARDSID FROM META_REPORT)",True)
	executeQuery(f"DELETE FROM META_COST WHERE COSTID NOT IN (SELECT COSTID FROM META_REPORT)",True)
	executeQuery(f"DELETE FROM META_THEMES WHERE THEMESID NOT IN (SELECT THEMESID FROM META_REPORT)",True)
	
def optoutAccount(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	INDEX=result["INDEX"]
	OKTAID=result["OKTAID"]
	
	found = executeQuery(f"SELECT USERID, OPTOUT FROM USER_LOGINS WHERE OKTAID = '{OKTAID}'")
	if type(found) == tuple: found=[found]
	if found != None and len(found) > INDEX: #Update only
		index=0
		for row in found:
			USERID=row[0]
			OPTOUT=0
			if row[1] != None: OPTOUT=int(row[1])
			if index == INDEX:
				target_opt = 1
				if OPTOUT==1: target_opt = 0
				executeQuery(f"UPDATE USER_LOGINS \
					SET OPTOUT = {target_opt}\
					WHERE OKTAID = '{OKTAID}' AND USERID='{USERID}'\
					", True)
				break
			index+=1
	return getNewIndex("USER_LOGINS")
	
def insertCollections(raw_data,is_string=False):
	json_string = raw_data
	if not is_string:
		json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	USERID=result["USERID"]
	CARDS=result["CARDS"] #card_id : {'l': level, 'u': upgrades}, ...
	
	#grab the user's `ID` from the database and use that instead.
	result = executeQuery(f"SELECT ID FROM USERS WHERE USERID = '{USERID}'")
	if result == None: return "Critical: User was not found in the database!"
	USER=result[0]
	result = executeQuery(f"SELECT CARDID, LEVEL, UPGRADES FROM USER_COLLECTIONS WHERE USERID = {USER}")
	FOUND_CARDS={}
	if result != None:
		if type(result)==tuple: result=[result]
		for card in result:
			FOUND_CARDS[int(card[0])]=[int(card[1]),int(card[2])]
	#Add the new cards
	ALL_QUERIES=[]
	ALL_VALUES=[]
	cards_ids_already_seen=[]
	for card_id in CARDS.keys():
		true_cardid=int(card_id)
		LEVEL=CARDS[card_id]["l"]
		UPGRADES=0
		if "u" in CARDS[card_id]:
			UPGRADES=CARDS[card_id]["u"]
		#Update cards if they were already in the database
		if true_cardid in FOUND_CARDS:
			old_level,old_upgrades=FOUND_CARDS[true_cardid]
			if old_level != LEVEL or old_upgrades != UPGRADES:
				ALL_QUERIES.append(f"UPDATE USER_COLLECTIONS \
					SET LEVEL = {LEVEL}, UPGRADES = {UPGRADES}\
					WHERE USERID={USER} AND CARDID={card_id}")
		#Otherwise insert them
		elif true_cardid not in cards_ids_already_seen:
			ALL_VALUES.append(f"({USER},{card_id},{LEVEL},{UPGRADES})")
			cards_ids_already_seen.append(true_cardid)
	if len(ALL_VALUES)>0:
		ALL_VALUES=",".join(x for x in ALL_VALUES)
		ALL_QUERIES.append(f"INSERT INTO USER_COLLECTIONS (\
			USERID,CARDID,LEVEL,UPGRADES\
			) VALUES {ALL_VALUES}")
	if len(ALL_QUERIES) > 0:
		executeMany(ALL_QUERIES, True)
	return getNewIndex("USER_COLLECTIONS")
	
def insertCardComparisonData(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	TEAMID=result["TEAMID"]
	CARDS=result["CARDS"] #card_id : {'l': level, 'v': vote}, ...
	
	#grab the user's `ID` from the database and use that instead.
	result = executeQuery(f"SELECT ID FROM TEAMS WHERE TEAMID = {TEAMID}")
	if result == None: return "Critical: User was not found in the database!"
	result = executeQuery(f"SELECT CARDID FROM TEAMWAR_CHOICE WHERE TEAMID = {TEAMID}")
	FOUND_CARDS=[]
	if result != None:
		if type(result)==tuple: result=[result]
		for card in result:
			card_id=card[0]
			FOUND_CARDS.append(int(card_id))
			
	ALL_NEW_CARDS=[]
	ALL_UPDATED_CARDS=[]
	UPDATED=int(time.time())
	#Add the new cards
	for card_id in CARDS.keys():
		LEVEL=CARDS[card_id]["l"]
		VOTE=CARDS[card_id]["v"]
		#Update cards if they were already in the database
		if int(card_id) in FOUND_CARDS:
			ALL_UPDATED_CARDS.append(f"UPDATE TEAMWAR_CHOICE \
				SET LEVEL = {LEVEL}, VOTE = {VOTE}, UPDATED = {UPDATED}\
				WHERE TEAMID = {TEAMID} AND CARDID={card_id}\
				")
		#Otherwise insert them
		else:
			ALL_NEW_CARDS.append(f"({TEAMID},{card_id},{LEVEL},{VOTE},{UPDATED})")
	if len(ALL_UPDATED_CARDS) > 0:
		executeMany(ALL_UPDATED_CARDS, True)
	if len(ALL_NEW_CARDS) > 0:
		ALL_NEW_CARDS = ",".join(x for x in ALL_NEW_CARDS)
		executeQuery(f"INSERT INTO TEAMWAR_CHOICE (\
				TEAMID,CARDID,LEVEL,VOTE,UPDATED\
				) VALUES {ALL_NEW_CARDS}", True)
	return getNewIndex("TEAMWAR_CHOICE")
	
def processBracketForEmail(BRACKETID):
	bracket_data=[]
	UPDATED=int(time.time()) - 3600 * 24 * 4 #Last 4 days
	result = executeQuery(f"SELECT TEAMNAME, RUNS, MEMBERS, SCORE, UPDATED FROM TEAMWAR_BRACKET WHERE BRACKETID = {BRACKETID}")
	if result == None: return bracket_data, updated
	if type(result) == tuple: result=[result]
	for row in result:
		TEAMNAME=row[0].upper()
		RUNS=row[1]
		MEMBERS=row[2]
		SCORE=row[3]
		bracket_data.append([TEAMNAME,RUNS,MEMBERS,SCORE])
	sorted_bracket_data=[]
	for team_data in bracket_data: #[TEAMNAME,RUNS,MEMBERS,SCORE]
		TEAMNAME,RUNS,MEMBERS,SCORE = team_data
		avg = 0
		if RUNS > 0:
			avg="%.2f" % (float(SCORE) / RUNS)
		projected="%d" % int(float(avg) * MEMBERS)
		maximum="%d" % ( SCORE + (114 * (MEMBERS - RUNS)))
		if MEMBERS < 50:
			projected+=" / %d" % int(float(avg) * 50)
			maximum+=" / %d" % ( SCORE + (114 * (50 - RUNS)))
		sorted_bracket_data.append([TEAMNAME,SCORE,RUNS,float(avg),MEMBERS,projected,maximum,BRACKETID])
	sorted_bracket_data = sorted(sorted_bracket_data, key=lambda x: (x[3]), reverse=True)
	return sorted_bracket_data

def insertBracketDouglasSubscriptions(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	TEAM=result["TEAM"] #team_name : subscribe, ...
	CHANNELID=result["CHANNELID"]
	DELETE = False
	WSID = "NULL"
	WSTOKEN = "NULL"
	if "DELETE" in result:
		DELETE=result["DELETE"]
	if "WSID" in result:
		WSID=result["WSID"]
	if "WSTOKEN" in result:
		WSTOKEN="'%s'" % result["WSTOKEN"]
	
	TEAMNAME = None
	SUBSCRIBED = None
	clean_team_name=removeCharactersOutOfRange(TEAM).replace("'","''").lower()
	result = executeQuery(f"SELECT TEAMNAME,SUBSCRIBED FROM BRACKET_SUBSCRIBE WHERE EMAIL = '{CHANNELID}' AND TEAMNAME = '{clean_team_name}' AND BRACKETID = 0")
	if DELETE and result == None: return 0
	if type(result) == list: return "ERROR"
	if type(result) == tuple:
		TEAMNAME=result[0]
		SUBSCRIBED=int(result[1])
	
	if TEAMNAME != None:
		sub = None
		#Update subscribed to 0
		if DELETE: sub = 0
		elif SUBSCRIBED == 0: sub = 1
		else:
			#They are already subscribed! Do nothing.
			return 0
		executeQuery(f"UPDATE BRACKET_SUBSCRIBE \
				SET SUBSCRIBED = {sub}, WSID = {WSID}, WSTOKEN = {WSTOKEN}\
				WHERE EMAIL = '{CHANNELID}' AND TEAMNAME = '{clean_team_name}'",True)
		return 0
	
	#Not found. Add them.
	executeQuery(f"INSERT INTO BRACKET_SUBSCRIBE (\
		EMAIL,TEAMNAME,BRACKETID,SUBSCRIBED,WSID,WSTOKEN\
		) VALUES ('{CHANNELID}','{clean_team_name}',0,1,{WSID},{WSTOKEN})", True)
	return getNewIndex("BRACKET_SUBSCRIBE")

def insertBracketSubscriptions(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	TEAMS=result["TEAMS"] #team_name : subscribe, ...
	EMAIL=result["EMAIL"]
	
	past_subscriptions = {}
	fourdaysago=int(time.time())-3600*24*4
	clean_team_list=[]
	for team in TEAMS.keys():
		clean_team_name=removeCharactersOutOfRange(team).replace("'","''").lower()
		clean_team_list.append(clean_team_name)
	VALUES=''.join(f"'{x}'" for x in clean_team_list)
	result = executeQuery(f"SELECT TEAMNAME,SUBSCRIBED FROM BRACKET_SUBSCRIBE WHERE EMAIL = '{EMAIL}' AND TEAMNAME IN ({VALUES}) AND BRACKETID IN (SELECT BRACKETID FROM TEAMWAR_BRACKET WHERE UPDATED > {fourdaysago})")
	if result == None: result =[]
	if type(result) == tuple: result = [result]
	for row in result:
		TEAMNAME=row[0]
		SUBSCRIBED=int(row[1])
		past_subscriptions[TEAMNAME]=SUBSCRIBED
	
	ALL_UPDATED_SUBS=[]
	ALL_NEW_SUBS=[]
	for team in TEAMS.keys():
		sub=int(TEAMS[team])
		clean_team_name=removeCharactersOutOfRange(team).replace("'","''").lower()
		if team in past_subscriptions:
			if sub != past_subscriptions[team]:
				ALL_UPDATED_SUBS.append(f"UPDATE BRACKET_SUBSCRIBE \
					SET SUBSCRIBED = {sub}\
					WHERE EMAIL = '{EMAIL}' AND TEAMNAME = '{clean_team_name}'\
					")
		else:
			result = executeQuery(f"SELECT BRACKETID FROM TEAMWAR_BRACKET ")
			ALL_NEW_SUBS.append(f"('{EMAIL}','{clean_team_name}',(SELECT y.BRACKETID FROM TEAMWAR_BRACKET y WHERE y.TEAMNAME = '{clean_team_name}' AND y.UPDATED > {fourdaysago}),{sub})")
	if len(ALL_UPDATED_SUBS) > 0:
		executeMany(ALL_UPDATED_SUBS, True)
	if len(ALL_NEW_SUBS) > 0:
		ALL_NEW_SUBS = ",".join(x for x in ALL_NEW_SUBS)
		executeQuery(f"INSERT INTO BRACKET_SUBSCRIBE (\
			EMAIL,TEAMNAME,BRACKETID,SUBSCRIBED\
			) VALUES {ALL_NEW_SUBS}", True)
	return getNewIndex("BRACKET_SUBSCRIBE")
	
###TEAMS###
	
def insertTeams(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	TEAMID=result["TEAMID"]
	NAME=result["NAME"]
	NAME=removeCharactersOutOfRange(NAME).lower()
	
	result = executeQuery(f"SELECT NAME FROM TEAMS WHERE TEAMID = {TEAMID}")
	if type(result) == tuple: result=result[0]
	if result == None:
		NAME=NAME.replace("'","''")
		executeQuery(f"INSERT INTO TEAMS (\
			TEAMID,NAME\
			) VALUES (\
			{TEAMID},'{NAME}'\
			)", True)
	elif result != NAME:
		NAME=NAME.replace("'","''")
		executeQuery(f"UPDATE TEAMS \
			SET NAME = '{NAME}'\
			WHERE TEAMID={TEAMID}\
			", True)
	return getNewIndex("TEAMS")
	
def insertTeamMembers(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	TEAMID=result["TEAMID"]
	if TEAMID == None: TEAMID = 0
	USERIDS=result["USERIDS"] # { userid1 : { role: role, mmr: mmr, ... }, ... }
	FOUND_USERS=[]
	
	UPDATED=int(time.time())
	###if it's not in the top 1000, return
	result = executeQuery(f"SELECT USERID FROM TEAM_MEMBERS WHERE TEAMID = {TEAMID}")
	if result != None:
		for row in result:
			user_id=row[0]
			FOUND_USERS.append(user_id)
	#Delete users in FOUND_USERS that were not in USERIDS
	ALL_UPDATED_MEMBERS=[]
	for user_id in FOUND_USERS:
		if user_id not in USERIDS.keys():
			ALL_UPDATED_MEMBERS.append(f"UPDATE TEAM_MEMBERS \
				SET TEAMID=0\
				WHERE USERID='{user_id}'")
	if len(ALL_UPDATED_MEMBERS) > 0:
		executeMany(ALL_UPDATED_MEMBERS, True)
	#Add users in USERIDS (only update the ROLE if they exist in FOUND_USERS)
	SEARCH_STR=",".join(f"'{x}'" for x in USERIDS.keys())
	result = executeQuery(f"SELECT USERID FROM TEAM_MEMBERS WHERE USERID IN ({SEARCH_STR})")
	if type(result)==tuple: result=[result]
	userid_list=[]
	if result != None:
		for row in result:
			user_id=row[0]
			userid_list.append(user_id)
	ALL_VALUES=[]
	COLUMNS=[]
	ALL_UPDATED_MEMBERS=[]
	USERID_TO_MMR={}
	for user_id in USERIDS.keys():
		user_exists = user_id in userid_list
		if user_exists:
			UPDATES=[]
			UPDATES.append(f"UPDATED = {UPDATED}")
			UPDATES.append(f"TEAMID = {TEAMID}")
			for key in USERIDS[user_id].keys():
				if key == "MMR":
					USERID_TO_MMR[user_id]=USERIDS[user_id][key]
				value=USERIDS[user_id][key]
				UPDATES.append(f"{key} = {value}")
			UPDATES=",".join(x for x in UPDATES)
			ALL_UPDATED_MEMBERS.append(f"UPDATE TEAM_MEMBERS \
				SET {UPDATES}\
				WHERE USERID='{user_id}'")
		else:
			if len(COLUMNS) == 0:
				COLUMNS.append("TEAMID")
				COLUMNS.append("USERID")
				COLUMNS.append("UPDATED")
				for key in USERIDS[user_id].keys():
					COLUMNS.append(key)
			VALUES=[]
			VALUES.append(TEAMID)
			VALUES.append(f"'{user_id}'")
			VALUES.append(UPDATED)
			for key in USERIDS[user_id].keys():
				VALUES.append(USERIDS[user_id][key])
			VALUES=",".join(str(x) for x in VALUES)
			ALL_VALUES.append("("+VALUES+")")
	if len(ALL_UPDATED_MEMBERS) > 0:
		executeMany(ALL_UPDATED_MEMBERS, True)
	if len(COLUMNS) > 0 and len(ALL_VALUES) > 0:
		COLUMNS=",".join(x for x in COLUMNS)
		ALL_VALUES=",".join(x for x in ALL_VALUES)
		executeQuery(f"INSERT INTO TEAM_MEMBERS (\
			{COLUMNS}\
			) VALUES {ALL_VALUES}", True)
			
	#Add to the user history
	ALL_VALUES=[]
	for USERID in USERID_TO_MMR.keys():
		MMR=USERID_TO_MMR[USERID]
		ALL_VALUES.append(f"({TEAMID},'{USERID}',{MMR},{UPDATED})")
	if len(ALL_VALUES)> 0:
		ALL_VALUES = ",".join(x for x in ALL_VALUES)
		executeQuery(f"INSERT INTO USERS_HISTORY (\
			TEAMID,USERID,MMR,UPDATED\
			) VALUES {ALL_VALUES}", True)
	return getNewIndex("TEAM_MEMBERS")
		
###REPORTS

def insertMetaReport(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	TIME=int(time.time())
	SEARCH=result["SEARCH"]
	NAME=result["NAME"]
	THEMES=result["THEMES"] #{ "adv,fan" : 12.3 }
	CARDS=result["CARDS"] #{ 123 : 12.3 }
	TOTALDECKS=result["TOTALDECKS"]
	METADECKS=None
	DECKMATCH="NULL"
	if "METADECKS" in result: METADECKS=result["METADECKS"]
	COSTS=None
	if "COSTS" in result: COSTS=result["COSTS"] #{ 3.3 : 100 }
	
	ALL_VALUES=[]
	THEMESID=getNewIndex("META_THEMES","THEMESID")
	for theme in THEMES.keys():
		percent=THEMES[theme]
		DECKID="NULL"
		if METADECKS != None and theme in METADECKS:
			DECKID=insertDeckWithLevelsTwo(METADECKS[theme],True)
			DECKMATCH=executeQuery(f"SELECT COUNT(USERID) FROM TEAM_MEMBERS WHERE DECKID = {DECKID}")
			DECKMATCH=DECKMATCH[0]
		ALL_VALUES.append(f"({THEMESID},'{theme}',{percent},{DECKID},{DECKMATCH})")
	if len(ALL_VALUES)> 0:
		ALL_VALUES = ",".join(x for x in ALL_VALUES)
		executeQuery(f"INSERT INTO META_THEMES (\
			THEMESID,THEMES,PERCENT,DECKID,DECKMATCH\
			) VALUES {ALL_VALUES}", True)
	CARDSID=getNewIndex("META_CARDS","CARDSID")
	ALL_VALUES=[]
	for card_id in CARDS.keys():
		percent=CARDS[card_id]
		ALL_VALUES.append(f"({CARDSID},{card_id},{percent})")
	if len(ALL_VALUES)> 0:
		ALL_VALUES = ",".join(x for x in ALL_VALUES)
		executeQuery(f"INSERT INTO META_CARDS (\
			CARDSID,CARDID,PERCENT\
			) VALUES {ALL_VALUES}", True)
	COSTID="NULL"
	if COSTS != None:
		COSTID=getNewIndex("META_COST","COSTID")
		ALL_VALUES=[]
		for cost in COSTS.keys(): #{ 3.3 : 100 }
			total=COSTS[cost]
			ALL_VALUES.append(f"({COSTID},{cost},{total})")
		if len(ALL_VALUES)> 0:
			ALL_VALUES = ",".join(x for x in ALL_VALUES)
			executeQuery(f"INSERT INTO META_COST (\
				COSTID,COST,TOTAL\
				) VALUES {ALL_VALUES}", True)
	#if SEARCH and NAME are already in there. Just update the TIME,THEMESID,CARDSID
	index=None
	if SEARCH != "Last 1 day":
		index = executeQuery(f"SELECT * from META_REPORT WHERE SEARCH='{SEARCH}' AND NAME='{NAME}'")
	if index == None:
		executeQuery(f"INSERT INTO META_REPORT (\
			TIME,SEARCH,NAME,THEMESID,CARDSID,TOTALDECKS,COSTID\
			) VALUES (\
			{TIME},'{SEARCH}','{NAME}',{THEMESID},{CARDSID},{TOTALDECKS},{COSTID}\
			)", True)
	else:
		executeQuery(f"UPDATE META_REPORT \
			SET TIME = {TIME}, THEMESID = {THEMESID}, CARDSID = {CARDSID}, TOTALDECKS = {TOTALDECKS}\
			WHERE SEARCH='{SEARCH}' AND NAME='{NAME}'\
			", True)
	return getNewIndex("META_REPORT")

def insertMetaChalReport(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	TIME=int(time.time())
	THEMES=result["THEMES"] #{ "adv,fan" : 12.3 }
	CARDS=result["CARDS"] #{ 123 : 12.3 }
	TOTALDECKS=result["TOTALDECKS"]
	METADECKS=None
	if "METADECKS" in result: METADECKS=result["METADECKS"]
	
	ALL_VALUES=[]
	THEMESID=getNewIndex("META_THEMES","THEMESID")
	for theme in THEMES.keys():
		percent=THEMES[theme]
		DECKID="NULL"
		if METADECKS != None and theme in METADECKS:
			DECKID=insertDeckWithLevelsTwo(METADECKS[theme],True)
		ALL_VALUES.append(f"({THEMESID},'{theme}',{percent},{DECKID})")
	if len(ALL_VALUES)> 0:
		ALL_VALUES = ",".join(x for x in ALL_VALUES)
		executeQuery(f"INSERT INTO META_THEMES (\
			THEMESID,THEMES,PERCENT,DECKID\
			) VALUES {ALL_VALUES}", True)
	CARDSID=getNewIndex("META_CARDS","CARDSID")
	ALL_VALUES=[]
	for card_id in CARDS.keys():
		percent=CARDS[card_id]
		ALL_VALUES.append(f"({CARDSID},{card_id},{percent})")
	if len(ALL_VALUES)> 0:
		ALL_VALUES = ",".join(x for x in ALL_VALUES)
		executeQuery(f"INSERT INTO META_CARDS (\
			CARDSID,CARDID,PERCENT\
			) VALUES {ALL_VALUES}", True)
	#if SEARCH and NAME are already in there. Just update the TIME,THEMESID,CARDSID
	index = None
	EVENTID = executeQuery(f"SELECT ID FROM EVENTS WHERE TYPE = 4 AND STARTTIME = (SELECT MAX(STARTTIME) FROM EVENTS WHERE TYPE = 4)")
	if type(EVENTID) == tuple: EVENTID = EVENTID[0]
	index = executeQuery(f"SELECT * from META_CHAL_REPORT WHERE EVENTID = {EVENTID}")
	if index == None:
		executeQuery(f"INSERT INTO META_CHAL_REPORT (\
			TIME,EVENTID,THEMESID,CARDSID,TOTALDECKS\
			) VALUES (\
			{TIME},{EVENTID},{THEMESID},{CARDSID},{TOTALDECKS}\
			)", True)
	else:
		executeQuery(f"UPDATE META_CHAL_REPORT \
			SET TIME = {TIME}, THEMESID = {THEMESID}, CARDSID = {CARDSID}, TOTALDECKS = {TOTALDECKS}\
			WHERE EVENTID = {EVENTID}\
			", True)
	return getNewIndex("META_CHAL_REPORT")
	
def insertTeamReport(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	TEAMID=result["TEAMID"]
	RANK=result["RANK"]
	TROPHIES=result["TROPHIES"]
	MEMBERS=result["MEMBERS"]
	NKLEVEL=result["NKLEVEL"]
	COUNTRY=result["COUNTRY"]
	STATUS=result["STATUS"]
	DESCRIPTION=result["DESCRIPTION"].replace("'","''")
	UPDATED=int(time.time())
	
	index = executeQuery(f"SELECT RANK, LASTRANK from TEAMS_REPORT WHERE TEAMID={TEAMID}")
	if index == None:
		if RANK == None: RANK = 9999
		LASTRANK=RANK
		executeQuery(f"INSERT INTO TEAMS_REPORT (\
			TEAMID,RANK,LASTRANK,TROPHIES,MEMBERS,\
			NKLEVEL,COUNTRY,STATUS,DESCRIPTION,UPDATED\
			) VALUES (\
			{TEAMID},{RANK},{LASTRANK},{TROPHIES},{MEMBERS},\
			{NKLEVEL},'{COUNTRY}','{STATUS}','{DESCRIPTION}',{UPDATED}\
			)", True)
	else:
		#today = datetime.datetime.now()
		#start = today - datetime.timedelta((today.weekday() + 1) % 7)
		#monday = start + relativedelta.relativedelta(weekday=relativedelta.MO(0))
		#last_monday=int(monday.timestamp())
		CUR_RANK=index[0]
		LASTRANK=index[1]
		if RANK == None:
			RANK = CUR_RANK
			LASTRANK=RANK
		else:
			LASTRANK=RANK
			if CUR_RANK == 0 or RANK == 0: LASTRANK=0
			elif RANK != CUR_RANK: LASTRANK=CUR_RANK
		#else: pass
		#Keep the same LASTRANK the same
		executeQuery(f"UPDATE TEAMS_REPORT \
			SET RANK = {RANK}, LASTRANK = {LASTRANK}, TROPHIES = {TROPHIES},\
			MEMBERS = {MEMBERS}, NKLEVEL = {NKLEVEL}, COUNTRY = '{COUNTRY}',\
			STATUS = '{STATUS}', DESCRIPTION = '{DESCRIPTION}',\
			UPDATED = {UPDATED}\
			WHERE TEAMID={TEAMID}\
			", True)
	return getNewIndex("TEAMS_REPORT")
	
###TEAMWARS###
	
def insertTeamWarCardChoices(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	CARDS=result["CARDS"] #[ [ { "id": 1272 }, { "id": 186 } ], ... ]
	TIME=int(time.time())
	
	today = datetime.datetime.now()
	start = today - datetime.timedelta((today.weekday() + 1) % 7)
	monday = start + relativedelta.relativedelta(weekday=relativedelta.MO(0))
	last_monday=int(monday.timestamp())
	LAST_UPDATE = executeQuery(f"SELECT MAX(TIME) from TEAMWAR_CARDS")
	if type(LAST_UPDATE) == tuple: LAST_UPDATE=LAST_UPDATE[0]
	if LAST_UPDATE == None: LAST_UPDATE=0
	if LAST_UPDATE < last_monday:
		for card_pair in CARDS: #[ { "id": 1272 }, { "id": 186 } ]
			pair_of_cards=[]
			for card in card_pair:
				if 'id' in card: pair_of_cards.append(card['id'])
			if len(pair_of_cards) != 2: continue #hopefull should never happen
			CARDID1=pair_of_cards[0]
			CARDID2=pair_of_cards[1]
			#get the latest PAIRID, insert it into TEAMWAR_PAIRS
			PAIRID=getNewIndex("TEAMWAR_PAIRS", "PAIRID")
			executeQuery(f"INSERT INTO TEAMWAR_PAIRS (\
				PAIRID,CARDID1,CARDID2\
				) VALUES (\
				{PAIRID},{CARDID1},{CARDID2}\
				)", True)
			#then add to TEAMWAR_CARDS
			executeQuery(f"INSERT INTO TEAMWAR_CARDS (\
				TIME,PAIRID\
				) VALUES (\
				{TIME},{PAIRID}\
				)", True)
	return getNewIndex("TEAMWAR_CARDS")
	
def getAllSubscribed(bracketid):
	subscribe_results={}
	OneWeekAgo=int(time.time()) - 3600 * 24 * 4
	subscriptions = executeQuery(f"SELECT EMAIL, TEAMNAME, SUBSCRIBED FROM BRACKET_SUBSCRIBE WHERE BRACKETID = {bracketid}")
	if subscriptions == None: return subscribe_results
	elif type(subscriptions) == tuple: subscriptions=[subscriptions]
	for sub_data in subscriptions:
		email=sub_data[0]
		team_name=sub_data[1]
		if type(team_name) == str: team_name=team_name.upper()
		is_subscribed=int(sub_data[2])
		if is_subscribed == 1:
			if team_name not in subscribe_results:
				subscribe_results[team_name]=[]
			subscribe_results[team_name].append(email)
	return subscribe_results

def insertBracketDetails(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	BRACKET=result["BRACKET"] #{ TEAMNAME: [SCORE,RUNS,MEMBERS], ...}
	UPDATED=int(time.time())
	team_names=[]
	for key in BRACKET.keys():
		team_names.append(key)
	if len(team_names) == 0: return "You did not provide any teams"
	global BracketLock
	BracketLock.acquire()
	BRACKETID=getBracketID(team_names)
	if BRACKETID == None:
		#BRACKETID=getNewIndex("TEAMWAR_BRACKET", "BRACKETID")
		VALUES=[]
		for team in team_names:
			clean_team_name=removeCharactersOutOfRange(team).replace("'","''").lower()
			SCORE,RUNS,MEMBERS=BRACKET[team]
			#(SELECT MAX(y.BRACKETID)+1 FROM TEAMWAR_BRACKET y)
			VALUES.append(f"((SELECT MAX(y.BRACKETID)+1 FROM TEAMWAR_BRACKET y),'{clean_team_name}',{RUNS},{MEMBERS},{SCORE},{UPDATED})")
		#then add to TEAMWAR_BRACKET
		if len(VALUES) > 0:
			VALUES=",".join(x for x in VALUES)
			executeQuery(f"INSERT INTO TEAMWAR_BRACKET (\
					BRACKETID,TEAMNAME,RUNS,MEMBERS,SCORE,UPDATED\
					) VALUES {VALUES}", True)
	else:
		old_bracket_data=processBracketForEmail(BRACKETID)
			
		ALL_BRACKET_DATA=[]
		for team in team_names:
			clean_team_name=removeCharactersOutOfRange(team).replace("'","''").lower()
			SCORE,RUNS,MEMBERS=BRACKET[team]
			ALL_BRACKET_DATA.append(f"UPDATE TEAMWAR_BRACKET \
					SET RUNS = {RUNS}, MEMBERS = {MEMBERS},\
					SCORE = {SCORE}, UPDATED = {UPDATED}\
					WHERE BRACKETID={BRACKETID} AND TEAMNAME='{clean_team_name}' AND RUNS < {RUNS}")
		executeMany(ALL_BRACKET_DATA, True)
	
		new_bracket_data=processBracketForEmail(BRACKETID)
		#Find out which teams have different information (i.e. runs)
		delta_teams={}
		VALUES=[]
		for old_row in old_bracket_data:
			team_name = old_row[0]
			#[TEAMNAME,SCORE,RUNS,float(avg),MEMBERS,projected,maximum]
			for new_row in new_bracket_data:
				if team_name == new_row[0]:
					clean_team_name=removeCharactersOutOfRange(team_name).replace("'","''").lower()
					if old_row[2] != new_row[2]:
						delta_score = new_row[1] - old_row[1]
						delta_runs = new_row[2] - old_row[2]
						delta_avg = "%.2f" % (float(new_row[3]) - float(old_row[3]))
						if float(delta_avg) > 0: delta_avg = f"+ {delta_avg}"
						delta_teams[team_name]=[f"{old_row[1]} + {delta_score}",f"{old_row[2]} + {delta_runs}",f"{old_row[3]} {delta_avg}"]
						#Add to the BRACKET history.
						#new_row = [TEAMNAME,SCORE,RUNS,float(avg),MEMBERS,projected,maximum,BRACKETID]
						VALUES.append(f"({new_row[7]},'{clean_team_name}',{new_row[2]},{new_row[4]},{new_row[1]},UNIX_TIMESTAMP())")
					break
		if len(VALUES) > 0:
			VALUES=",".join(x for x in VALUES)
			executeQuery(f"INSERT INTO TEAMWAR_BRACKET_HISTORY (\
					BRACKETID,TEAMNAME,RUNS,MEMBERS,SCORE,UPDATED\
					) VALUES {VALUES}", True)
		subscriber_list=getAllSubscribed(BRACKETID)
		if len(subscriber_list) > 0:
			for team in subscriber_list.keys():
				if team in delta_teams:
					receiver_emails=subscriber_list[team]
					EMAILER.sendBracketUpdate(receiver_emails,team,delta_teams[team],new_bracket_data)
			
	BracketLock.notify_all()
	BracketLock.release()
	return getNewIndex("TEAMWAR_BRACKET", "BRACKETID")

def findUserUpgrades(users_list,TEAMID):
	user_upgrades={}
	search_str=",".join(f"'{x}'" for x in users_list)
	fourdaysago = int(time.time()) - 3600 * 24 * 3 - 3600 * 12 #3.5 days
	#result = executeQuery(f"SELECT USERID, SPENT, MAX(TOTAL), MAX(UPDATED) FROM TEAMWAR_UPGRADE_USERS WHERE TEAMID={TEAMID} and UPDATED > {fourdaysago} AND USERID IN ({search_str}) GROUP BY USERID")
	result = executeQuery(f"SELECT t.USERID, t.SPENT, t.TOTAL, t.UPDATED FROM (SELECT USERID, MAX(UPDATED) AS UPDATED FROM TEAMWAR_UPGRADE_USERS WHERE TEAMID={TEAMID} and UPDATED > {fourdaysago} AND USERID IN ({search_str}) GROUP BY USERID) x JOIN TEAMWAR_UPGRADE_USERS t ON x.USERID = t.USERID AND x.UPDATED = t.UPDATED")
	if result == None: return user_upgrades
	if type(result) == tuple: result=[result]
	for row in result:
		user_upgrades[row[0]]=[row[1],row[2],row[3]]
	return user_upgrades

def findCardUpgades(cards_list,TEAMID):
	card_upgrades={}
	search_str=",".join(f"'{x}'" for x in cards_list)
	fourdaysago = int(time.time()) - 3600 * 24 * 3 - 3600 * 12 #3.5 days
	#result = executeQuery(f"SELECT t.CARDID, t.TOTAL, t.UPDATED FROM (SELECT CARDID, MAX(UPDATED) AS UPDATED FROM TEAMWAR_UPGRADE_CARDS GROUP BY CARDID) x JOIN TEAMWAR_UPGRADE_CARDS t ON x.CARDID = t.CARDID AND x.UPDATED = t.UPDATED WHERE t.TEAMID={TEAMID} and t.UPDATED > {fourdaysago} AND t.CARDID IN ({search_str})")
	result = executeQuery(f"SELECT t.CARDID, t.TOTAL, t.UPDATED FROM (SELECT CARDID, MAX(UPDATED) AS UPDATED FROM TEAMWAR_UPGRADE_CARDS WHERE TEAMID={TEAMID} AND UPDATED > {fourdaysago} AND CARDID IN ({search_str}) GROUP BY CARDID) x JOIN TEAMWAR_UPGRADE_CARDS t ON x.CARDID = t.CARDID AND x.UPDATED = t.UPDATED")
	if result == None: return card_upgrades
	if type(result) == tuple: result=[result]
	for row in result:
		card_upgrades[int(row[0])]=[row[1],row[2]]
	return card_upgrades

def insertUpgradeDetails(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	TEAMID=result["TEAMID"]
	CARDS=result["CARDS"] #{ UTC_TIME : {card_id : [spent,total], card_id: [spent,total]}, ...}
	USERS=result["USERS"] #{ UTC_TIME : {user_id : [spent,total], user_id: [spent,total]}, ...}
	for key in USERS.keys():
		USERS_VALUES=[]
		CARD_VALUES=[]
		BLOBID = getNewIndex("TEAMWAR_UPGRADE_USERS", "BLOBID")
		UTC_TIME=int(key)
		users_list=list(USERS[key].keys())
		old_user_upgrades = findUserUpgrades(users_list,TEAMID)
		for user in USERS[key].keys():
			old_spent=old_total=old_updated=0
			if user in old_user_upgrades:
				old_spent,old_total,old_updated=old_user_upgrades[user]
			new_spent,new_total=USERS[key][user]
			if (int(old_spent) < int(new_spent) or int(old_total) < int(new_total)) and\
				old_updated < UTC_TIME:
				#print(f"{user}, {old_spent}, {new_spent}, {old_total}, {new_total}")
				USERS_VALUES.append(f"({TEAMID},'{user}',{new_spent},{new_total},{UTC_TIME},{BLOBID})")
		if len(USERS_VALUES) > 0:
			USERS_VALUES=",".join(x for x in USERS_VALUES)
			executeQuery(f"INSERT INTO TEAMWAR_UPGRADE_USERS (\
							TEAMID,USERID,SPENT,TOTAL,UPDATED,BLOBID\
							) VALUES {USERS_VALUES}", True)
							
		if key not in CARDS: continue #Skip the rest
		cards_list=list(CARDS[key].keys())
		old_card_upgrades = findCardUpgades(cards_list,TEAMID)
		for card in CARDS[key].keys():
			old_total=old_updated=0
			card_id=int(card)
			if card_id in old_card_upgrades:
				old_total,old_updated=old_card_upgrades[card_id]
			else: old_total=old_updated=-1
			new_spent,new_total=CARDS[key][card]
			if int(old_total) < int(new_total) and old_updated < UTC_TIME:
				#print(f"{card}, {old_total}, {new_total}")
				if new_spent == new_total and new_total!=0: new_spent=new_total-old_total
				if new_spent > new_total: new_spent = new_total
				CARD_VALUES.append(f"({TEAMID},{card},{new_spent},{new_total},{UTC_TIME},{BLOBID})")
		if len(CARD_VALUES) > 0:
			CARD_VALUES=",".join(x for x in CARD_VALUES)
			executeQuery(f"INSERT INTO TEAMWAR_UPGRADE_CARDS (\
							TEAMID,CARDID,SPENT,TOTAL,UPDATED,BLOBID\
							) VALUES {CARD_VALUES}", True)
	
	return getNewIndex("TEAMWAR_UPGRADE_CARDS", "BLOBID")

def findCardRequests(TEAMID):
	#get last 8 hours
	lasteighthours=int(time.time()) - 3600 * 9
	card_requests={}
	result = executeQuery(f"SELECT USERID, UPDATED FROM TEAM_REQUESTS WHERE TEAMID={TEAMID} and UPDATED > {lasteighthours}")
	if result == None: return card_requests
	if type(result) == tuple: result=[result]
	for row in result:
		USERID=row[0]
		if USERID not in card_requests:
			card_requests[USERID]=[]
		card_requests[USERID].append(int(row[1]))
	return card_requests

def insertCardRequests(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	TEAMID=result["TEAMID"]
	REQUESTS=result["REQUESTS"] #[ [CREATED,USERID,CARDID], ...]
	old_card_requests=findCardRequests(TEAMID)
	VALUES=[]
	for elem in REQUESTS:
		CREATED,USERID,CARDID=elem
		if USERID in old_card_requests:
			created_list=old_card_requests[USERID]
			if CREATED not in created_list:
				VALUES.append(f"({TEAMID},'{USERID}',{CARDID},{CREATED})")
		else:
			VALUES.append(f"({TEAMID},'{USERID}',{CARDID},{CREATED})")
			
	if len(VALUES) > 0:
		VALUES=",".join(x for x in VALUES)
		executeQuery(f"INSERT INTO TEAM_REQUESTS (\
						TEAMID,USERID,CARDID,UPDATED\
						) VALUES {VALUES}", True)
	return getNewIndex("TEAM_REQUESTS")
	
#{RECEIVER : [ [SENDER,CREATED], ...]}	
def findCardDonations(TEAMID,max_time=int(time.time()) - 3600 * 48):
	#get last 8 hours
	card_donations={}
	result = executeQuery(f"SELECT RECEIVER, SENDER, UPDATED FROM TEAM_DONATIONS WHERE TEAMID={TEAMID} and UPDATED >= {max_time}")
	if result == None: return card_donations
	if type(result) == tuple: result=[result]
	for row in result:
		RECEIVER=row[0]
		if RECEIVER not in card_donations:
			card_donations[RECEIVER]=[]
		card_donations[RECEIVER].append([row[1],int(row[2])])
	return card_donations
	
def insertCardDonations(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	TEAMID=result["TEAMID"]
	DONATIONS=result["DONATIONS"] #[ [CREATED,RECEIVER,SENDER,CARDID], ...]
	max_time=int(time.time())
	for elem in DONATIONS:
		CREATED,RECEIVER,SENDER,CARDID=elem
		if CREATED < max_time:
			max_time=CREATED
	old_card_donations=findCardDonations(TEAMID,max_time) #{RECEIVER : [ [SENDER,CREATED], ...]}
	VALUES=[]
	for elem in DONATIONS:
		CREATED,RECEIVER,SENDER,CARDID=elem
		if RECEIVER in old_card_donations:
			created_list=old_card_donations[RECEIVER]
			if [SENDER,int(CREATED)] not in created_list:
				VALUES.append(f"({TEAMID},'{RECEIVER}','{SENDER}',{CARDID},{CREATED})")
		else:
			VALUES.append(f"({TEAMID},'{RECEIVER}','{SENDER}',{CARDID},{CREATED})")
			
	if len(VALUES) > 0:
		VALUES=",".join(x for x in VALUES)
		executeQuery(f"INSERT INTO TEAM_DONATIONS (\
						TEAMID,RECEIVER,SENDER,CARDID,UPDATED\
						) VALUES {VALUES}", True)
	return getNewIndex("TEAM_DONATIONS")


def insertTeamApplications(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	TEAMID=result["TEAMID"]
	APPLICATIONS=result["USERS"] #{ USERID : [STATUS, ROLE], ...}
	result = executeQuery(f"SELECT USERID FROM TEAM_ACCEPT WHERE TEAMID={TEAMID}")
	if type(result) == tuple: result=[result]
	FOUND_USERS=[]
	if result != None:
		for row in result:
			FOUND_USERS.append(row[0])
	#Insert or Update?
	ALL_QUERIES=[]
	INSERT_VALUES=[]
	CUR_TIME=int(time.time())
	for user in APPLICATIONS.keys():
		status,role=APPLICATIONS[user]
		if user in FOUND_USERS:
			ALL_QUERIES.append(f"UPDATE TEAM_ACCEPT \
					SET STATUS = '{status}', ROLE = '{role}', UPDATED = {CUR_TIME}\
					WHERE TEAMID={TEAMID} AND USERID='{user}'")
		else:
			INSERT_VALUES.append(f"({TEAMID},'{user}','{status}','{role}',{CUR_TIME})")
	if len(INSERT_VALUES) > 0:
		INSERT_VALUES=",".join(x for x in INSERT_VALUES)
		ALL_QUERIES.append(f"INSERT INTO TEAM_ACCEPT (\
						TEAMID,USERID,STATUS,ROLE,UPDATED\
						) VALUES {INSERT_VALUES}")
	if len(ALL_QUERIES) > 0:
		executeMany(ALL_QUERIES, True)
	return getNewIndex("TEAM_ACCEPT")
	
def downloadTeamApplications(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	TEAMID=result["TEAMID"]
	UPDATED=result["UPDATED"]
	result = executeQuery(f"SELECT MAX(UPDATED) FROM TEAM_ACCEPT WHERE TEAMID={TEAMID}")
	GRAB_APPLICATIONS=False
	if type(result) == tuple: result=result[0]
	if result == None: GRAB_APPLICATIONS=True
	elif int(result) > int(UPDATED): GRAB_APPLICATIONS=True
	if not GRAB_APPLICATIONS: return "{}"
	
	result = executeQuery(f"SELECT USERID, STATUS, ROLE, UPDATED FROM TEAM_ACCEPT WHERE TEAMID={TEAMID}")
	if result == None: return "{}"
	if type(result) == tuple: result=[result]
	member_map={}
	member_map["applications"]={}
	max_updated=0
	for row in result:
		USERID=row[0]
		STATUS=row[1]
		ROLE=row[2]
		member_update=row[3]
		if member_update > max_updated:
			max_updated=member_update
		if STATUS != 'ignore':
			member_map["applications"][USERID]=[STATUS,ROLE]
	member_map["updated"]=max_updated
	return json.dumps(member_map)

def insertTeamwarHistory(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
		
	USERS=result["USERS"]#{USERID : [ [SCORE,CAPS,WEEK,YEAR], ... ], ...}
	INSERT_VALUES=[]
	past_dict={}
	USERID_LIST=','.join(f"'{x}'" for x in USERS.keys())
	past_result = executeQuery(f"SELECT USERID,MANUAL,WEEK,YEAR FROM TEAMWAR_HISTORY WHERE USERID in ({USERID_LIST})")
	if past_result == None: past_result = []
	elif type(past_result) == tuple: past_result=[past_result]
	for row in past_result:
		USERID=row[0]
		if USERID not in past_dict:
			past_dict[USERID]=[]
		manual = row[1]
		if manual != 1:
			week = row[2]
			year = row[3]
			past_dict[USERID].append(f"{week}-{year}")
	
	for USERID in USERS.keys():
		for elem in USERS[USERID]:
			SCORE,CAPS,WEEK,YEAR = elem
			if USERID in past_dict and f"{WEEK}-{YEAR}" in past_dict[USERID]:
				continue
			if SCORE == None: SCORE = "NULL"
			if CAPS == None or (CAPS == 0 and SCORE == "NULL"):
				continue
				#CAPS = "NULL"
			INSERT_VALUES.append(f"('{USERID}',{SCORE},{CAPS},{WEEK},{YEAR},0)")
	if len(INSERT_VALUES) > 0:
		INSERT_VALUES=",".join(x for x in INSERT_VALUES)
		executeQuery(f"INSERT INTO TEAMWAR_HISTORY (\
						USERID,SCORE,CAPS,WEEK,YEAR,MANUAL\
						) VALUES {INSERT_VALUES}", True)
	return getNewIndex("TEAMWAR_HISTORY")

def insertTeamwarHistoryTwo(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
		
	USERS=result["USERS"]#{USERID : [ [SCORE,CAPS,EVENTID], ... ], ...}
	INSERT_VALUES=[]
	past_dict={}
	USERID_LIST=','.join(f"'{x}'" for x in USERS.keys())
	past_result = executeQuery(f"SELECT USERID,EVENTID FROM TEAMWAR_HISTORY_TWO WHERE USERID in ({USERID_LIST})")
	if past_result == None: past_result = []
	elif type(past_result) == tuple: past_result=[past_result]
	for row in past_result:
		USERID=row[0]
		EVENTID=row[1]
		if USERID not in past_dict:
			past_dict[USERID]=[]
		past_dict[USERID].append(int(EVENTID))
	
	for USERID in USERS.keys():
		for elem in USERS[USERID]:
			SCORE,CAPS,EVENTID = elem
			if USERID in past_dict and int(EVENTID) in past_dict[USERID]:
				continue
			if SCORE == None: SCORE = "NULL"
			if CAPS == None or (CAPS == 0 and SCORE == "NULL"):
				continue
				#CAPS = "NULL"
			INSERT_VALUES.append(f"('{USERID}',{SCORE},{CAPS},{EVENTID})")
	if len(INSERT_VALUES) > 0:
		INSERT_VALUES=",".join(x for x in INSERT_VALUES)
		executeQuery(f"INSERT INTO TEAMWAR_HISTORY_TWO (\
						USERID,SCORE,CAPS,EVENTID\
						) VALUES {INSERT_VALUES}", True)
	return getNewIndex("TEAMWAR_HISTORY_TWO")

'''
Notes:
6 - Battle Pass
5 - TVT
4 - ?
3 - ?
2 - Card Usage
1 - ?
0 - ?
'''
def insertEvents(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
		
	EVENTS=result["EVENTS"]#{ID : [NAME,TYPE,TEAM,START,END,[PACK1,PACK2,...]], ...}
	INSERT_TEAM_EVENTS=[]
	INSERT_EVENTS=[]
	past_dict={}
	EVENTID_LIST=','.join(f"'{x}'" for x in EVENTS.keys())
	past_result = executeQuery(f"SELECT EVENTID,STARTTIME,ENDTIME FROM EVENTS WHERE EVENTID in ({EVENTID_LIST})")
	if past_result == None: past_result = []
	elif type(past_result) == tuple: past_result=[past_result]
	for row in past_result:
		EVENTID=int(row[0])
		if EVENTID not in past_dict:
			past_dict[EVENTID]=[]
		start_time = row[1]
		end_time = row[2]
		past_dict[EVENTID].append(f"{start_time}-{end_time}")
	
	for eventid in EVENTS.keys():
		EVENTID = int(eventid)
		NAME,TYPE,TEAM,START,END,PACK_DATA = EVENTS[eventid]
		NAME=NAME.replace("'","''")
		if EVENTID in past_dict and f"{START}-{END}" in past_dict[EVENTID]:
			continue
		if PACK_DATA == None:
			INSERT_EVENTS.append(f"({EVENTID},'{NAME}',{TYPE},{TEAM},{START},{END})")
		else:
			expected_pack_data=["NULL","NULL","NULL","NULL","NULL","NULL","NULL","NULL"]
			final_pack=len(PACK_DATA)
			for i in range(final_pack):
				if i == len(expected_pack_data):
					print("ERROR: insertEvents - PACK_DATA exceeds 8 packs!")
					break
				expected_pack_data[i]=PACK_DATA[i]
			expected_pack_data=",".join(str(x) for x in expected_pack_data)
			INSERT_TEAM_EVENTS.append(f"({EVENTID},'{NAME}',{TYPE},{TEAM},{START},{END},{expected_pack_data},{final_pack})")
	if len(INSERT_EVENTS) > 0:
		INSERT_EVENTS=",".join(x for x in INSERT_EVENTS)
		executeQuery(f"INSERT INTO EVENTS (\
						EVENTID,NAME,TYPE,TEAM,STARTTIME,ENDTIME\
						) VALUES {INSERT_EVENTS}", True)
	if len(INSERT_TEAM_EVENTS) > 0:
		INSERT_TEAM_EVENTS=",".join(x for x in INSERT_TEAM_EVENTS)
		executeQuery(f"INSERT INTO EVENTS (\
						EVENTID,NAME,TYPE,TEAM,STARTTIME,ENDTIME,\
						PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8,FINALPACK\
						) VALUES {INSERT_TEAM_EVENTS}", True)
	return getNewIndex("EVENTS")
	
def getAmount(text):
	digits=''
	if sys.hexversion >= 0x3070000:
		digits=''.join(filter(lambda x: x.isdigit(), text))
	else:
		digits=filter(str.isdigit, text)
	if len(digits)>0: return int(digits)
	return -1
	
def addRewardPack(pack_data):
	'''
	reward_pack = [
		{item_id : quantity},
		...
	]
	'''
	PACKSID = getNewIndex("REWARD_PACKS","PACKSID")
	INSERT_CARDID = []
	INSERT_CODE = []
	for elem in pack_data:
		for key,value in elem.items():
			tmp_key = key
			if type(key) == str:
				card_id = getAmount(key)
				if card_id != -1: tmp_key = card_id
			if type(tmp_key) == int:
				if tmp_key == 255 or value > 65535: value = 0
				INSERT_CARDID.append(f"({PACKSID},{key},{value})")
			else:
				INSERT_CODE.append(f"({PACKSID},'{key}',{value})")
	if len(INSERT_CARDID) > 0:
		INSERT_CARDID=",".join(x for x in INSERT_CARDID)
		executeQuery(f"INSERT INTO REWARD_PACKS (PACKSID,CARDID,QUANTITY) VALUES {INSERT_CARDID}", True)
	if len(INSERT_CODE) > 0:
		INSERT_CODE=",".join(x for x in INSERT_CODE)
		executeQuery(f"INSERT INTO REWARD_PACKS (PACKSID,CODE,VALUE) VALUES {INSERT_CODE}", True)
	if len(INSERT_CARDID) == 0 and len(INSERT_CODE) == 0:
		executeQuery(f"INSERT INTO REWARD_PACKS (PACKSID,CARDID,QUANTITY) VALUES ({PACKSID},255,0)", True)
		
	return PACKSID
	
def addEventPacks(pack_data):
	'''
	PACK_DATA = [
		[
			team_pack,pack_num,score,
			CARDS0,CARDSP0, #common
			CARDS1,CARDSP1, #rare
			CARDS2,CARDSP2, #epic
			CARDS3,CARDSP3, #legendary
			CUR1,CUR2,CUR3, #Coins, Cash, (PVP?)
			UPS0,UPSP0, #bronze
			UPS1,UPSP1, #silver
			UPS2,UPSP2, #gold
			reward_pack
		],
		...
	]
	'''
	PACKSID = getNewIndex("EVENT_PACKS","PACKSID")
	INSERT_EVENT_PACKS = []
	for elem in pack_data:
		TEAM,PACKNUM,SCORE,\
			CARDS0,CARDSP0,\
			CARDS1,CARDSP1,\
			CARDS2,CARDSP2,\
			CARDS3,CARDSP3,\
			CUR1,CUR2,CUR3,CUR4,\
			UPS0,UPSP0,\
			UPS1,UPSP1,\
			UPS2,UPSP2,\
			reward_pack = elem
		SUBPACK = "NULL"
		if len(reward_pack) > 0:
			SUBPACK = addRewardPack(reward_pack)
		INSERT_EVENT_PACKS.append(f"({PACKSID},{TEAM},{PACKNUM},{SCORE},\
			{CARDS0},{CARDSP0},\
			{CARDS1},{CARDSP1},\
			{CARDS2},{CARDSP2},\
			{CARDS3},{CARDSP3},\
			{CUR1},{CUR2},{CUR3},{CUR4},\
			{UPS0},{UPSP0},\
			{UPS1},{UPSP1},\
			{UPS2},{UPSP2},\
			{SUBPACK})")
	if len(INSERT_EVENT_PACKS) > 0:
		INSERT_EVENT_PACKS=",".join(x for x in INSERT_EVENT_PACKS)
		executeQuery(f"INSERT INTO EVENT_PACKS (\
							PACKSID,TEAM,PACKNUM,SCORE,\
							CARDS0,CARDSP0,\
							CARDS1,CARDSP1,\
							CARDS2,CARDSP2,\
							CARDS3,CARDSP3,\
							CUR1,CUR2,CUR3,CUR4,\
							UPS0,UPSP0,\
							UPS1,UPSP1,\
							UPS2,UPSP2,\
							SUBPACK) VALUES {INSERT_EVENT_PACKS}", True)
	return PACKSID
	
def insertEvents_two(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	EVENTS=result["EVENTS"]
	'''
	{
		ID : [
			[event_name,event_type_id,TEAM,start_time,end_time,PACK_DATA]
		],
		...
	}
	'''
	### 1. Has the event already been added?
	past_dict={}
	EVENTID_LIST=','.join(f"'{x}'" for x in EVENTS.keys())
	past_result = executeQuery(f"SELECT EVENTID,STARTTIME,ENDTIME FROM EVENTS_TWO WHERE EVENTID in ({EVENTID_LIST})")
	if past_result == None: past_result = []
	elif type(past_result) == tuple: past_result=[past_result]
	for row in past_result:
		EVENTID=int(row[0])
		if EVENTID not in past_dict:
			past_dict[EVENTID]=[]
		start_time = row[1]
		end_time = row[2]
		past_dict[EVENTID].append(f"{start_time}-{end_time}")
	
	### 2. Preprocess before insert
	INSERT_EVENTS=[]
	INSERT_EVENTS_NOPACK=[]
	for eventid in EVENTS.keys():
		EVENTID = int(eventid)
		NAME,TYPE,TEAM,START,END,PACK_DATA = EVENTS[eventid]
		NAME=NAME.replace("'","''")
		if EVENTID in past_dict and f"{START}-{END}" in past_dict[EVENTID]:
			continue
		if PACK_DATA == None or len(PACK_DATA) == 0:
			INSERT_EVENTS_NOPACK.append(f"({EVENTID},'{NAME}',{TYPE},{TEAM},{START},{END})")
		else:
			PACKSID = addEventPacks(PACK_DATA)
			INSERT_EVENTS.append(f"({EVENTID},'{NAME}',{TYPE},{TEAM},{START},{END},{PACKSID})")
			
	### 3. Insert into database
	if len(INSERT_EVENTS_NOPACK) > 0:
		INSERT_EVENTS_NOPACK=",".join(x for x in INSERT_EVENTS_NOPACK)
		executeQuery(f"INSERT INTO EVENTS_TWO (\
						EVENTID,NAME,TYPE,TEAM,STARTTIME,ENDTIME\
						) VALUES {INSERT_EVENTS_NOPACK}", True)
	if len(INSERT_EVENTS) > 0:
		INSERT_EVENTS=",".join(x for x in INSERT_EVENTS)
		executeQuery(f"INSERT INTO EVENTS_TWO (\
						EVENTID,NAME,TYPE,TEAM,STARTTIME,ENDTIME,PACKSID\
						) VALUES {INSERT_EVENTS}", True)
	return getNewIndex("EVENTS_TWO")

def insertTeamEvents(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	
	USERS_DATA=result["USERS"]#[ [USERID, SCORE, EVENTID], ...]
	USERS_LIST=[]
	EVENT_LIST=[]
	for elem in USERS_DATA:
		USERID, SCORE, EVENTID=elem
		if USERID not in USERS_LIST:
			USERS_LIST.append(USERID)
		if EVENTID not in EVENT_LIST:
			EVENT_LIST.append(EVENTID)
	USERS_LIST=','.join(f"'{x}'" for x in USERS_LIST)
	EVENT_LIST=','.join(str(x) for x in EVENT_LIST)
	CUR_TIME = int(time.time())
	FOUR_DAYS_AGO = CUR_TIME - 3600 * 24 * 4
	past_result = executeQuery(f"SELECT USERID,EVENTID,SCORE FROM TEAM_EVENT_PARTICIPATION\
		WHERE USERID in ({USERS_LIST}) AND EVENTID IN ({EVENT_LIST}) AND UPDATED > {FOUR_DAYS_AGO}")
	if past_result == None: past_result = []
	elif type(past_result) == tuple: past_result=[past_result]
	past_dict={}
	for row in past_result:
		USERID=row[0]
		if USERID not in past_dict:
			past_dict[USERID]={}
		EVENTID = row[1]
		SCORE = row[2]
		past_dict[USERID][int(EVENTID)]=int(SCORE)
	ALL_QUERIES=[]
	INSERT_VALUES=[]
	for elem in USERS_DATA:
		USERID, SCORE, EVENTID=elem
		if USERID in past_dict and int(EVENTID) in past_dict[USERID]:
			if past_dict[USERID][int(EVENTID)] == int(SCORE): continue
			ALL_QUERIES.append(f"UPDATE TEAM_EVENT_PARTICIPATION \
				SET SCORE = {SCORE}, UPDATED = {CUR_TIME}\
				WHERE USERID = '{USERID}' AND EVENTID = {EVENTID} AND SCORE < {SCORE} AND UPDATED > {FOUR_DAYS_AGO}\
				")
		else:
			INSERT_VALUES.append(f"('{USERID}',{EVENTID},{SCORE},{CUR_TIME})")
	if len(INSERT_VALUES) > 0:
		INSERT_VALUES=",".join(x for x in INSERT_VALUES)
		ALL_QUERIES.append(f"INSERT INTO TEAM_EVENT_PARTICIPATION (\
						USERID,EVENTID,SCORE,UPDATED\
						) VALUES {INSERT_VALUES}")
	if len(ALL_QUERIES) > 0:
		executeMany(ALL_QUERIES, True)
	return getNewIndex("TEAM_EVENT_PARTICIPATION")
	
def convertDeckEff(user_id,deck):
	WAL_MAP={}
	WAL_MAP[1]=[0,5]
	WAL_MAP[2]=[5,15]
	WAL_MAP[3]=[15,25]
	WAL_MAP[4]=[25,40]
	WAL_MAP[5]=[40,55]
	WAL_MAP[6]=[55,70]
	WAL_MAP[7]=[70,70]
	json_data = { "USERID":user_id, "CARDS": {}}
	#"CARDS" : {card_id : {'l': level, 'u': upgrades}, ...}
	for card_id in deck.keys():
		level_float = deck[card_id]
		level = math.floor(level_float)
		if level > 7: level = 7
		lower,upper = WAL_MAP[level]
		upgrades = math.ceil((level_float-level) * (upper - lower))
		json_data["CARDS"][card_id]={'l': level, 'u': upgrades}
	return json.dumps(json_data)
	
def insertMatch(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	if len(result) < 17: return getNewIndex("USER_MATCHES")
	if result["USERID1"] == None or result["USERID2"] == None: return getNewIndex("USER_MATCHES")
	if "DECK1" not in result or "DECK2" not in result: return getNewIndex("USER_MATCHES")
	#result is a blob of data to be inserted into the database.
	#PREPROCESS THE DECKS
	DECK1=result["DECK1"]
	DECK2=result["DECK2"]
	DECK1_ID=insertDeckWithLevelsTwo(DECK1)
	DECK2_ID=insertDeckWithLevelsTwo(DECK2)
	if DECK1_ID == None or DECK2_ID == None: return getNewIndex("USER_MATCHES")
	del result["DECK1"]
	del result["DECK2"]
	
	#Upload the card levels for these bad boys
	if "DECK1EFF" in result:
		user_id = result["USERID1"]
		deck = result["DECK1EFF"]
		collection_str=convertDeckEff(user_id,deck)
		insertCollections(collection_str,True)
		del result["DECK1EFF"]
	if "DECK2EFF" in result:
		user_id = result["USERID2"]
		deck = result["DECK2EFF"]
		collection_str=convertDeckEff(user_id,deck)
		insertCollections(collection_str,True)
		del result["DECK2EFF"]
		
	COLUMNS=[]
	VALUES=[]
	COLUMNS.append("DECK1")
	VALUES.append(DECK1_ID)
	COLUMNS.append("DECK2")
	VALUES.append(DECK2_ID)
	
	for key in result.keys():
		if key in ["TIME","TIMELEFT","MODE","NK1","TEAM1","MMR1","SCORE1","RESULT1","NK2","TEAM2","MMR2","SCORE2","RESULT2","DISCONNECT"]:
			COLUMNS.append(key)
			if key == "RESULT2" and "RESULT1" in result and result["RESULT1"] == 3:
				result["RESULT2"] = 3 #Opponent disconnected. Both players lose.
			VALUES.append(result[key])
		elif key in ["USERID1","USERID2","REGION"]:
			result_str=result[key]
			COLUMNS.append(key)
			VALUES.append(f"'{result_str}'")
	COLUMNS=",".join(x for x in COLUMNS)
	VALUES=",".join(str(x) for x in VALUES)
	executeQuery(f"INSERT INTO USER_MATCHES \
		({COLUMNS}) VALUES ({VALUES})", True)
	return getNewIndex("USER_MATCHES")
	
def bindWord(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	DSERVER=result["DSERVER"]
	DWORD=result["DWORD"]
	DTYPE=result["DTYPE"]
	DCONTENT=result["DCONTENT"]
	CREATOR=result["CREATOR"]
	DISCORDID = "NULL"
	if "DISCORDID" in result:
		DISCORDID = '"%s"' % result["DISCORDID"]
	#print(f"{DSERVER},{DWORD},{DTYPE},{DCONTENT}")
	executeSanitize(f"INSERT INTO DOUGLAS_BINDER (DSERVER,DWORD,DTYPE,DCONTENT,CREATOR,DISCORDID) VALUES ({DSERVER},%(name)s,'{DTYPE}',%(name2)s,'{CREATOR}',{DISCORDID})", DWORD, DCONTENT, True)
	return getNewIndex("DOUGLAS_BINDER")
	
def unbindWord(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	DSERVER=result["DSERVER"]
	DWORD=result["DWORD"]
	executeQuery(f"DELETE FROM DOUGLAS_BINDER WHERE DSERVER = {DSERVER} AND DWORD='{DWORD}'", True)
	return getNewIndex("DOUGLAS_BINDER")
	
def chatSupport(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	ACTION=result["ACTION"]
	
	#Init
	#	Check if the teamid and email pair already exists in the table.
	if ACTION == "INIT":
		EMAIL = result["EMAIL"]
		TOKEN = result["TOKEN"]
		TEAM = result["TEAM"]
		if TEAM == None: TEAM = 'NULL'
		result = executeQuery(f"SELECT EMAIL FROM CHAT_SUPPORT WHERE TOKEN = '{TOKEN}'")
		new_token = result == None
		found_email = None if result == None else result[0]
		result = executeQuery(f"SELECT TOKEN FROM CHAT_SUPPORT WHERE EMAIL = '{EMAIL}'")
		found_token = None if result == None else result[0]
		if result == None and new_token:
			#	If it does not, add it.
			executeQuery(f"INSERT INTO CHAT_SUPPORT (EMAIL,TOKEN,TEAM,UPDATED) VALUES ('{EMAIL}','{TOKEN}',{TEAM},UNIX_TIMESTAMP())", True)
		elif not new_token:
			#	If it does, update the time.
			executeQuery(f"UPDATE CHAT_SUPPORT SET TEAM = {TEAM}, EMAIL = '{EMAIL}', UPDATED = UNIX_TIMESTAMP() WHERE TOKEN = '{TOKEN}'", True)
		elif new_token and found_token != TOKEN:
			#The found token does not match the current token
			executeQuery(f"UPDATE CHAT_SUPPORT SET TEAM = {TEAM}, TOKEN = '{TOKEN}', UPDATED = UNIX_TIMESTAMP() WHERE EMAIL = '{EMAIL}'", True)
		return getNewIndex("CHAT_SUPPORT")
	return getNewIndex("CHAT_SUPPORT")
	
def chatSupportTwo(raw_data):
	json_string=raw_data.decode("utf-8")
	result={}
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
	ACTION=result["ACTION"]
	
	#Init
	#	Check if the teamid and email pair already exists in the table.
	if ACTION == "INIT":
		EMAIL = result["EMAIL"].lower()
		TOKEN = result["TOKEN"]
		TEAM = result["TEAM"]
		if TEAM == None: TEAM = 'NULL'
		result = executeQuery(f"SELECT EMAIL FROM CHAT_SUPPORT WHERE TOKEN = '{TOKEN}'")
		new_token = result == None
		found_email = None if result == None else result[0].lower()
		result = executeQuery(f"SELECT TOKEN FROM CHAT_SUPPORT WHERE EMAIL = '{EMAIL}'")
		found_token = None if result == None else result[0]
		'''
		if new_token:
			if result == None:
				executeQuery(f"INSERT INTO CHAT_SUPPORT (EMAIL,TOKEN,TEAM,UPDATED) VALUES ('{EMAIL}','{TOKEN}',{TEAM},UNIX_TIMESTAMP())", True)
			elif found_token != TOKEN:
				executeQuery(f"UPDATE CHAT_SUPPORT SET TEAM = {TEAM}, TOKEN = '{TOKEN}', UPDATED = UNIX_TIMESTAMP() WHERE EMAIL = '{EMAIL}'", True)
		else:
			if found_email == EMAIL:
				executeQuery(f"UPDATE CHAT_SUPPORT SET TEAM = {TEAM}, TOKEN = '{TOKEN}', UPDATED = UNIX_TIMESTAMP() WHERE EMAIL = '{EMAIL}'", True)
		'''
		if result == None and new_token:
			#	If it does not, add it.
			executeQuery(f"INSERT INTO CHAT_SUPPORT (EMAIL,TOKEN,TEAM,UPDATED) VALUES ('{EMAIL}','{TOKEN}',{TEAM},UNIX_TIMESTAMP())", True)
		elif not new_token and found_email == EMAIL:
			#	If it does, update the time.
			executeQuery(f"UPDATE CHAT_SUPPORT SET TEAM = {TEAM}, TOKEN = '{TOKEN}', UPDATED = UNIX_TIMESTAMP() WHERE EMAIL = '{EMAIL}'", True)
		elif new_token and found_token != TOKEN:
			#The found token does not match the current token
			executeQuery(f"UPDATE CHAT_SUPPORT SET TEAM = {TEAM}, TOKEN = '{TOKEN}', UPDATED = UNIX_TIMESTAMP() WHERE EMAIL = '{EMAIL}'", True)
		return getNewIndex("CHAT_SUPPORT")
	#Add
	if ACTION == "ADD":
		TEAM = result["TEAM"]
		CHANNEL = result["CHANNEL"]
		WSID = result["WSID"]
		WSTOKEN = result["WSTOKEN"]
		EMAIL = None
		if "EMAIL" in result:
			EMAIL = result["EMAIL"]
		result = executeQuery(f"SELECT STATE FROM CHAT_SUPPORT WHERE TEAM = {TEAM} AND UPDATED > UNIX_TIMESTAMP() - 24*3600")
		if result == None:
			return "FAIL"
		if type(result) == list:
			result = result[0]
			if EMAIL == None:
				return "EXCEPTION"
		result = result[0]
		if result != 'SUPPORTED': return result
		result = executeQuery(f"SELECT TEAM FROM CHAT_SUPPORT WHERE CHANNEL = {CHANNEL}")
		if result != None:
			return "DUPLICATE"
		QUERY = f"UPDATE CHAT_SUPPORT SET CHANNEL = {CHANNEL}, WSID = {WSID}, WSTOKEN = '{WSTOKEN}', TEMPORARY = 'Y', STATE = 'PENDING' WHERE TEAM = {TEAM} AND UPDATED > UNIX_TIMESTAMP() - 24*3600"
		if EMAIL != None:
			QUERY += f" AND EMAIL = '{EMAIL}'"
		executeQuery(QUERY, True)
		return "OK"
	#Add TVT Score Chat Bot
	if ACTION == "TVTADD":
		CHANNEL = result["CHANNEL"]
		TVTCHANNEL = result["TVTCHANNEL"]
		WSID = result["WSID"]
		WSTOKEN = result["WSTOKEN"]
		result = executeQuery(f"SELECT TEMPORARY FROM CHAT_SUPPORT WHERE CHANNEL = {CHANNEL} AND UPDATED > UNIX_TIMESTAMP() - 24*3600")
		if result == None or result[0] != 'N':
			return "FAIL"
		QUERY = f"UPDATE CHAT_SUPPORT SET TVTCHANNEL = {TVTCHANNEL}, TVTWSID = {WSID}, TVTWSTOKEN = '{WSTOKEN}' WHERE CHANNEL = {CHANNEL} AND UPDATED > UNIX_TIMESTAMP() - 24*3600"
		executeQuery(QUERY, True)
		return "OK"
	#Remove
	if ACTION == "REM":
		CHANNEL = result["CHANNEL"]
		result = executeQuery(f"SELECT TEAM FROM CHAT_SUPPORT WHERE CHANNEL = {CHANNEL} LIMIT 1")
		if type(result) == tuple: result = result[0]
		executeQuery(f"UPDATE CHAT_SUPPORT SET CHANNEL = NULL, STATE = 'SUPPORTED', TEMPORARY = 'Y', CONFIRM = 'Y', WSID = NULL, WSTOKEN = NULL WHERE CHANNEL = {CHANNEL}", True)
		return result
	#Remove TVT Score Chat Bot
	if ACTION == "TVTREM":
		CHANNEL = result["CHANNEL"]
		result = executeQuery(f"SELECT TVTCHANNEL FROM CHAT_SUPPORT WHERE CHANNEL = {CHANNEL} AND UPDATED > UNIX_TIMESTAMP() - 24*3600 LIMIT 1")
		if result == None or result[0] == None:
			return "FAIL"
		QUERY = f"UPDATE CHAT_SUPPORT SET TVTCHANNEL = NULL, TVTWSID = NULL, TVTWSTOKEN = NULL WHERE CHANNEL = {CHANNEL}"
		executeQuery(QUERY, True)
		return "OK"
	#Confirmation messages
	if ACTION == "CONF":
		ENABLE = result["ENABLE"]
		if ENABLE:
			ENABLE = "Y"
		else:
			ENABLE = "N"
		CHANNEL = result["CHANNEL"]
		executeQuery(f"UPDATE CHAT_SUPPORT SET CONFIRM = '{ENABLE}' WHERE CHANNEL = {CHANNEL} AND STATE = 'VERIFIED'", True)
		return getNewIndex("CHAT_SUPPORT")
	#Verify
	if ACTION == "VER":
		EMAIL = result["EMAIL"]
		TEAM = result["TEAM"]
		executeQuery(f"UPDATE CHAT_SUPPORT SET STATE = 'VERIFIED', TEMPORARY = 'N' WHERE TEAM = {TEAM} AND EMAIL = '{EMAIL}'", True)
		return getNewIndex("CHAT_SUPPORT")
	#Fail
	if ACTION == "FAIL":
		EMAIL = result["EMAIL"]
		TEAM = result["TEAM"]
		executeQuery(f"UPDATE CHAT_SUPPORT SET STATE = 'FAILED' WHERE TEAM = {TEAM} AND EMAIL = '{EMAIL}'", True)
		return getNewIndex("CHAT_SUPPORT")
	#Pull
	if ACTION == "PULL":
		result = executeQuery(f"SELECT EMAIL,TOKEN,TEAM,CHANNEL,WSID,WSTOKEN,TEMPORARY,CONFIRM,TVTCHANNEL,TVTWSID,TVTWSTOKEN FROM CHAT_SUPPORT WHERE STATE IN ('VERIFIED','PENDING') AND UPDATED > UNIX_TIMESTAMP() - 24*3600 AND WSID IS NOT NULL")
		#put result in json, return it... similar to applications.
		if result == None: result = []
		if type(result) == tuple: result = [result]
		user_map = {"USERS" : []}
		for row in result:
			EMAIL,TOKEN,TEAM,CHANNEL,WSID,WSTOKEN,TEMPORARY,CONFIRM,TVTCHANNEL,TVTWSID,TVTWSTOKEN = [row[0],row[1],row[2],row[3],row[4],row[5],row[6]=='Y',row[7]=='Y',row[8],row[9],row[10]]
			user_map["USERS"].append([EMAIL,TOKEN,TEAM,CHANNEL,WSID,WSTOKEN,TEMPORARY,CONFIRM,TVTCHANNEL,TVTWSID,TVTWSTOKEN])
		return json.dumps(user_map)
	#Update
	if ACTION == "UPDATE":
		TEAM = result["TEAM"]
		WSID = result["WSID"]
		WSTOKEN = result["WSTOKEN"]
		QUERY = f"UPDATE CHAT_SUPPORT SET WSID = {WSID}, WSTOKEN = '{WSTOKEN}' WHERE TEAM = {TEAM} AND WSID IS NOT NULL AND UPDATED > UNIX_TIMESTAMP() - 24*3600"
		executeQuery(QUERY, True)
		return "OK"
	#Error, unknown action...
	return getNewIndex("CHAT_SUPPORT")
	
app = Flask(__name__)
		
@app.route('/meta_chal_report',methods = ['POST', 'GET'])
def meta_chal_report():
	if request.method == 'POST':
		data=request.data
		length=insertMetaChalReport(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("META_CHAL_REPORT")
		return make_response((f"{length}\n"),{})
		
@app.route('/meta_report',methods = ['POST', 'GET'])
def meta_report():
	if request.method == 'POST':
		data=request.data
		length=insertMetaReport(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("META_REPORT")
		return make_response((f"{length}\n"),{})
		
@app.route('/teams_report',methods = ['POST', 'GET'])
def teams_report():
	if request.method == 'POST':
		data=request.data
		length=insertTeamReport(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAMS_REPORT")
		return make_response((f"{length}\n"),{})
		
@app.route('/teams',methods = ['POST', 'GET'])
def teams():
	if request.method == 'POST':
		data=request.data
		length=insertTeams(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAMS")
		return make_response((f"{length}\n"),{})
		
@app.route('/users',methods = ['POST', 'GET'])
def users():
	if request.method == 'POST':
		data=request.data
		length=insertUsers(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USERS")
		return make_response((f"{length}\n"),{})
		
@app.route('/users_platform',methods = ['POST', 'GET'])
def users_platform():
	if request.method == 'POST':
		data=request.data
		length=insertUsersPlatform(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USERS")
		return make_response((f"{length}\n"),{})
		
@app.route('/login_users',methods = ['POST', 'GET'])
def login_users():
	if request.method == 'POST':
		data=request.data
		length=insertLoginUsers(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USER_LOGINS")
		return make_response((f"{length}\n"),{})
		

@app.route('/collections',methods = ['POST', 'GET'])
def collections():
	if request.method == 'POST':
		data=request.data
		length=insertCollections(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USER_COLLECTIONS")
		return make_response((f"{length}\n"),{})

@app.route('/card_comparison_data',methods = ['POST', 'GET'])
def card_comparison_data():
	if request.method == 'POST':
		data=request.data
		length=insertCardComparisonData(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USER_COLLECTIONS")
		return make_response((f"{length}\n"),{})
		
@app.route('/bracket_subscriptions',methods = ['POST', 'GET'])
def bracket_subscriptions():
	if request.method == 'POST':
		data=request.data
		length=insertBracketSubscriptions(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("BRACKET_SUBSCRIBE")
		return make_response((f"{length}\n"),{})
		
@app.route('/douglas_subscriptions',methods = ['POST', 'GET'])
def douglas_subscriptions():
	if request.method == 'POST':
		data=request.data
		length=insertBracketDouglasSubscriptions(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("BRACKET_SUBSCRIBE")
		return make_response((f"{length}\n"),{})
		
@app.route('/user_details',methods = ['POST', 'GET'])
def user_details():
	if request.method == 'POST':
		data=request.data
		length=insertUserDetails(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAM_MEMBERS")
		return make_response((f"{length}\n"),{})
		
@app.route('/team_members',methods = ['POST', 'GET'])
def team_members():
	if request.method == 'POST':
		data=request.data
		length=insertTeamMembers(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAM_MEMBERS")
		return make_response((f"{length}\n"),{})
		
@app.route('/primary_account',methods = ['POST', 'GET'])
def primary_account():
	if request.method == 'POST':
		data=request.data
		length=setPrimaryAccount(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USER_LOGINS")
		return make_response((f"{length}\n"),{})
		
@app.route('/delete_account',methods = ['POST', 'GET'])
def delete_account():
	if request.method == 'POST':
		data=request.data
		length=deleteAccount(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USER_LOGINS")
		return make_response((f"{length}\n"),{})
		
@app.route('/optout_account',methods = ['POST', 'GET'])
def optout_account():
	if request.method == 'POST':
		data=request.data
		length=optoutAccount(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USER_LOGINS")
		return make_response((f"{length}\n"),{})
		
@app.route('/card_choices',methods = ['POST', 'GET'])
def card_choices():
	if request.method == 'POST':
		data=request.data
		length=insertTeamWarCardChoices(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAMWAR_CARDS")
		return make_response((f"{length}\n"),{})
		
@app.route('/bracket_details',methods = ['POST', 'GET'])
def bracket_details():
	if request.method == 'POST':
		data=request.data
		length=insertBracketDetails(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAMWAR_BRACKET")
		return make_response((f"{length}\n"),{})

@app.route('/upgrade_details',methods = ['POST', 'GET'])
def upgrade_details():
	if request.method == 'POST':
		data=request.data
		length=insertUpgradeDetails(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAMWAR_UPGRADE_CARDS", "BLOBID")
		return make_response((f"{length}\n"),{})

@app.route('/card_requests',methods = ['POST', 'GET'])
def card_requests():
	if request.method == 'POST':
		data=request.data
		length=insertCardRequests(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAM_REQUESTS")
		return make_response((f"{length}\n"),{})
		
@app.route('/card_donations',methods = ['POST', 'GET'])
def card_donations():
	if request.method == 'POST':
		data=request.data
		length=insertCardDonations(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAM_DONATIONS")
		return make_response((f"{length}\n"),{})
		
@app.route('/team_applications',methods = ['POST', 'GET'])
def team_applications():
	if request.method == 'POST':
		data=request.data
		length=downloadTeamApplications(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAM_ACCEPT")
		return make_response((f"{length}\n"),{})
		
@app.route('/insert_team_applications',methods = ['POST', 'GET'])
def insert_team_applications():
	if request.method == 'POST':
		data=request.data
		length=insertTeamApplications(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAM_ACCEPT")
		return make_response((f"{length}\n"),{})
		
@app.route('/teamwar_history_two',methods = ['POST', 'GET'])
def teamwar_history_two():
	if request.method == 'POST':
		data=request.data
		length=insertTeamwarHistoryTwo(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAMWAR_HISTORY_TWO")
		return make_response((f"{length}\n"),{})
		
@app.route('/teamwar_history',methods = ['POST', 'GET'])
def teamwar_history():
	if request.method == 'POST':
		data=request.data
		length=insertTeamwarHistory(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAMWAR_HISTORY")
		return make_response((f"{length}\n"),{})
		
@app.route('/insert_events',methods = ['POST', 'GET'])
def insert_events():
	if request.method == 'POST':
		data=request.data
		length=insertEvents(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("EVENTS")
		return make_response((f"{length}\n"),{})
		
@app.route('/insert_events_two',methods = ['POST', 'GET'])
def insert_events_two():
	if request.method == 'POST':
		data=request.data
		length=insertEvents_two(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("EVENTS_TWO")
		return make_response((f"{length}\n"),{})
		
@app.route('/team_events',methods = ['POST', 'GET'])
def team_events():
	if request.method == 'POST':
		data=request.data
		length=insertTeamEvents(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("TEAM_EVENT_PARTICIPATION")
		return make_response((f"{length}\n"),{})
		
@app.route('/update_past_names',methods = ['POST', 'GET'])
def update_past_names():
	if request.method == 'POST':
		length=updatePastUserNames()
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USERS_NAMES_PAST")
		return make_response((f"{length}\n"),{})
		
@app.route('/update_past_teams',methods = ['POST', 'GET'])
def update_past_teams():
	if request.method == 'POST':
		length=updatePastTeams()
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USERS_TEAMS_PAST")
		return make_response((f"{length}\n"),{})
		
@app.route('/insert_match',methods = ['POST', 'GET'])
def insert_match():
	if request.method == 'POST':
		data=request.data
		length=insertMatch(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("USER_MATCHES")
		return make_response((f"{length}\n"),{})
		
@app.route('/bind_word',methods = ['POST', 'GET'])
def bind_word():
	if request.method == 'POST':
		data=request.data
		length=bindWord(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("DOUGLAS_BINDER")
		return make_response((f"{length}\n"),{})
		
@app.route('/unbind_word',methods = ['POST', 'GET'])
def unbind_word():
	if request.method == 'POST':
		data=request.data
		length=unbindWord(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("DOUGLAS_BINDER")
		return make_response((f"{length}\n"),{})
		
@app.route('/chat_support',methods = ['POST', 'GET'])
def chat_support():
	if request.method == 'POST':
		data=request.data
		length=chatSupport(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("CHAT_SUPPORT")
		return make_response((f"{length}\n"),{})
		
@app.route('/chat_support_two',methods = ['POST', 'GET'])
def chat_support_two():
	if request.method == 'POST':
		data=request.data
		length=chatSupportTwo(data)
		return make_response((f"{length}\n"),{})
	else:
		length=getNewIndex("CHAT_SUPPORT")
		return make_response((f"{length}\n"),{})
		
@app.route('/cleanup',methods = ['GET'])
def cleanup():
	#doCleanup()
	return make_response(("OK\n"),{})
	
@app.route('/oppdeck_killswitch',methods = ['GET'])
def oppdeck_killswitch():
	return make_response(("NO\n"),{})
	
@app.route('/oppdeck_killswitch_two',methods = ['GET'])
def oppdeck_killswitch_two():
	return make_response(("OK\n"),{})	
		
if __name__ == '__main__':
	#insertAllCards()
	serve(app, host='0.0.0.0', port='5002', threads=60)
	#deepUpdateDecks()