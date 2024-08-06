import dash
import dash_core_components as dcc
import dash_html_components as html
import sqlite3
import HELPER_DB
import DATABASE
from googletrans import Translator
from translate import TRANS
import threading

THEME_FILTER=[
	'All',
	'adv',
	'sci',
	'mys',
	'fan',
	'sup',
	'neu'
]
CTHEME_FILTER=[
	'All',
	"Adventure",
	"Sci-Fi",
	"Mystical",
	"Fantasy",
	"Superheroes",
	"Neutral"
]
TYPE_FILTER=[
	'All',
	'fight',
	'range',
	'tank',
	'ass',
	'spell'
]
COST_FILTER=[
	'All',
	2,
	3,
	4,
	5,
	6,
	7
]
RARITY_FILTER=[
	'All',
	'com',
	'rar',
	'epi',
	'leg'
]
CRARITY_FILTER=[
	'All',
	"Legendary",
	"Epic",
	"Rare",
	"Common"
]
KEYWORD_FILTER=[
	'All',
	'warcry',
	'deathwish',
	'charge',
	'flying'
]
TIME_FILTER=[
	'Last 14 days',
	'Last 7 days',
	'Last 3 days',
	'Last 1 day',
	'Last Patch'
]
MODE_FILTER=[
	'All',
	'Ranked',
	'Challenge',
	'Friendly Fight',
	'Team Wars'
]
TEAM_RANK=[
	'Top 50',
	'Top 250',
	'Top 1000',
	'1000 to 2000',
	'>2000'
]
TEAM_MEMBERS=range(50,0,-1)
TEAM_NKLEVEL=range(25,-1,-1)
TEAM_STATUS=[
	'All',
	'Open',
	'Moderated',
	'Closed'
]
PLAYER_RANK=[
	'Top 50',
	'Top 250',
	'Top 1000'
]
for i in range(8500, 0, -100):
	min_rank=i-100
	PLAYER_RANK.append(f'{min_rank}-{i}')
WIDE_PLAYER_RANK=['All','8500+']
for i in range(8500, 0, -1000):
	min_rank=i-1000
	WIDE_PLAYER_RANK.append(f'{min_rank}-{i}')
PLAYERS_SORT=[
	'RANK',
	'DONATED',
	'TW CAPS',
	'PVP WINS',
	'PVP WINS PERFECT',
	'CHLG WINS',
	'TW WINS',
	'FF WINS',
	'FF WINS PERFECT'
]
LEAGUES=[
	'SUMMARY',
	'GOLD',
	'SILVER',
	'BRONZE'
]
LANGUAGES=[
	"English",
	"Русский",		#Russian, ru
	"Deutsch",		#German, de
	"Français",		#French, fr
	"Italiano",		#Italian, it
	"Español",		#Spanish, es
	"한국어",			#Korean, ko
	"繁體中文(台灣)",	#Chinese Taiwan, zh-tw
	"中文（简体）",		#Chinese Simplified, zh-cn
	"Português",	#Brazilian, pt
	"Polski",		#Polish, pl
	"Türkçe",		#Turkish, tr
	"日本語",			#Japanese, ja
	#"Dutch",		#Netherlands, nl
]
language_map=['en','ru','de','fr','it','es','ko','zh-tw','zh-cn','pt','pl','tr','ja','nl']
translator = Translator()
translateLock = threading.Condition()

def tr(words, lang_index=0):
	#if lang_index == 0: print(f"looking in {lang_index} for {words}")
	if lang_index == 0 or type(words) != str or len(words) == 0: return words
	if words in TRANS.WORDS and lang_index in TRANS.WORDS[words]:
		return TRANS.WORDS[words][lang_index]
	try:
		quotes = '"'
		if "\n" in words: quotes = "'''"
		global translator
		result = translator.translate(words,src='en',dest=language_map[lang_index])
		translateLock.acquire()
		if words in TRANS.WORDS: TRANS.WORDS[words][lang_index]=result.text
		else: TRANS.WORDS[words]={lang_index : result.text}
		filename = 'translate/' + language_map[lang_index].replace('-','_') + '.py'
		fh = open(filename, 'ab')
		write_line = 'WORDS[%s%s%s]={%d:%s%s%s}\n' % (quotes,words,quotes,lang_index,quotes,result.text,quotes)
		fh.write(write_line.encode('utf8'))
		fh.close()
		translateLock.notify_all()
		translateLock.release()
		return result.text
	except:
		print(f"\tERROR: Unable to Translate to {language_map[lang_index]}: '{words[:20]}'")
	return words

def getSideBar(current_page,show=True,data=None,lindex=0):
	style_sidebar={
		'display': 'block' if show else 'none',
		'position': 'absolute',
		'width': '400px',
		'margin-top': '60px',
		'height': '800px',
		'background-color': '#888',
		'font-size': '32pt',
		'text-transform': 'lowercase',
		'font-variant': 'all-small-caps'
	}
	style_dropdown={
		'text-transform': 'lowercase',
		'font-variant': 'all-small-caps',
		'color': 'black'
	}
	if current_page == '/cards':
		META_FILTER=HELPER_DB.getDistinctNamesFromMetaReport()
		return	[
			html.H1(children=tr('CARDS',lindex)),
			html.P(children=tr('Rank Range',lindex)),
			dcc.Dropdown(
				id='cards-dropdown-rank',
				options=[{'label': tr(i,lindex), 'value': i} for i in META_FILTER],
				value=META_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Mode',lindex)),
			dcc.Dropdown(
				id='cards-dropdown-mode',
				options=[{'label': tr(i,lindex), 'value': i, 'disabled': (True if i != MODE_FILTER[0] else False)} for i in MODE_FILTER],
				value=MODE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Time Frame',lindex)),
			dcc.Dropdown(
				id='cards-dropdown-time',
				options=[{'label': tr(i,lindex), 'value': i} for i in TIME_FILTER],
				value=TIME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Deck Theme',lindex)),
			dcc.Dropdown(
				id='cards-dropdown-theme',
				options=[{'label': tr(i,lindex), 'value': i} for i in THEME_FILTER],
				value=THEME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Type',lindex)),
			dcc.Dropdown(
				id='cards-dropdown-type',
				options=[{'label': tr(i,lindex), 'value': i} for i in TYPE_FILTER],
				value=TYPE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Cost',lindex)),
			dcc.Dropdown(
				id='cards-dropdown-cost',
				options=[{'label': tr(i,lindex), 'value': i} for i in COST_FILTER],
				value=COST_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Rarity',lindex)),
			dcc.Dropdown(
				id='cards-dropdown-rarity',
				options=[{'label': tr(i,lindex), 'value': i} for i in RARITY_FILTER],
				value=RARITY_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Keyword',lindex)),
			dcc.Dropdown(
				id='cards-dropdown-keyword',
				options=[{'label': tr(i,lindex), 'value': i} for i in KEYWORD_FILTER],
				value=KEYWORD_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			)
		]
	elif current_page == '/allcards':
		return	[
			html.H1(children=tr('ALL CARDS',lindex)),
			html.P(children=tr('Deck Theme',lindex)),
			dcc.Dropdown(
				id='allcards-dropdown-theme',
				options=[{'label': tr(i,lindex), 'value': i} for i in THEME_FILTER],
				value=THEME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Type',lindex)),
			dcc.Dropdown(
				id='allcards-dropdown-type',
				options=[{'label': tr(i,lindex), 'value': i} for i in TYPE_FILTER],
				value=TYPE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Cost',lindex)),
			dcc.Dropdown(
				id='allcards-dropdown-cost',
				options=[{'label': tr(i,lindex), 'value': i} for i in COST_FILTER],
				value=COST_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Rarity',lindex)),
			dcc.Dropdown(
				id='allcards-dropdown-rarity',
				options=[{'label': tr(i,lindex), 'value': i} for i in RARITY_FILTER],
				value=RARITY_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Keyword',lindex)),
			dcc.Dropdown(
				id='allcards-dropdown-keyword',
				options=[{'label': tr(i,lindex), 'value': i} for i in KEYWORD_FILTER],
				value=KEYWORD_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			)
		]
	elif current_page == '/cardstats':
		return	[
			html.H1(children=tr('CARD STATS',lindex)),
			html.P(children=tr('Deck Theme',lindex)),
			dcc.Dropdown(
				id='cardstats-dropdown-theme',
				options=[{'label': tr(i,lindex), 'value': i} for i in CTHEME_FILTER],
				value=THEME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Type',lindex)),
			dcc.Dropdown(
				id='cardstats-dropdown-type',
				options=[{'label': tr(i,lindex), 'value': i} for i in TYPE_FILTER],
				value=TYPE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Cost',lindex)),
			dcc.Dropdown(
				id='cardstats-dropdown-cost',
				options=[{'label': tr(i,lindex), 'value': i} for i in COST_FILTER],
				value=COST_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Rarity',lindex)),
			dcc.Dropdown(
				id='cardstats-dropdown-rarity',
				options=[{'label': tr(i,lindex), 'value': i} for i in CRARITY_FILTER],
				value=RARITY_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
		]
	elif current_page == '/deckbuilder':
		return	[
			html.H1(children=tr('CARD STATS',lindex)),
			html.P(children=tr('Deck Theme',lindex)),
			dcc.Dropdown(
				id='deckbuilder-dropdown-theme',
				options=[{'label': tr(i,lindex), 'value': i} for i in CTHEME_FILTER],
				value=THEME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Type',lindex)),
			dcc.Dropdown(
				id='deckbuilder-dropdown-type',
				options=[{'label': tr(i,lindex), 'value': i} for i in TYPE_FILTER],
				value=TYPE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Cost',lindex)),
			dcc.Dropdown(
				id='deckbuilder-dropdown-cost',
				options=[{'label': tr(i,lindex), 'value': i} for i in COST_FILTER],
				value=COST_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Rarity',lindex)),
			dcc.Dropdown(
				id='deckbuilder-dropdown-rarity',
				options=[{'label': tr(i,lindex), 'value': i} for i in CRARITY_FILTER],
				value=RARITY_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
		]
	elif current_page == '/themes':
		META_FILTER=HELPER_DB.getDistinctNamesFromMetaReport()
		return	[
			html.H1(children=tr('THEMES',lindex)),
			html.P(children=tr('Rank Range',lindex)),
			dcc.Dropdown(
				id='themes-dropdown-rank',
				options=[{'label': tr(i,lindex), 'value': i} for i in META_FILTER],
				value=META_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children="Mode"),
			dcc.Dropdown(
				id='themes-dropdown-mode',
				options=[{'label': tr(i,lindex), 'value': i, 'disabled': (True if i != MODE_FILTER[0] else False)} for i in MODE_FILTER],
				value=MODE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children="Time Frame"),
			dcc.Dropdown(
				id='themes-dropdown-time',
				options=[{'label': tr(i,lindex), 'value': i} for i in TIME_FILTER],
				value=TIME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			)
		]
	elif current_page == '/decks':
		META_FILTER=HELPER_DB.getDistinctNamesFromMetaReport()
		return	[
			html.H1(children='DECKS'),
			html.P(children="Rank Range"),
			dcc.Dropdown(
				id='decks-dropdown-rank',
				options=[{'label': tr(i,lindex), 'value': i} for i in META_FILTER],
				value=META_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
		]
	elif current_page == '/mycards':
		return	[
			html.H1(children=tr('MY CARDS',lindex)),
			html.P(children=tr('Deck Theme',lindex)),
			dcc.Dropdown(
				id='collections-dropdown-theme',
				options=[{'label': tr(i,lindex), 'value': i, 'disabled': True} for i in THEME_FILTER],
				value=THEME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Type',lindex)),
			dcc.Dropdown(
				id='collections-dropdown-type',
				options=[{'label': tr(i,lindex), 'value': i, 'disabled': True} for i in TYPE_FILTER],
				value=TYPE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Cost',lindex)),
			dcc.Dropdown(
				id='collections-dropdown-cost',
				options=[{'label': i, 'value': i, 'disabled': True} for i in COST_FILTER],
				value=COST_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Rarity',lindex)),
			dcc.Dropdown(
				id='collections-dropdown-rarity',
				options=[{'label': tr(i,lindex), 'value': i, 'disabled': True} for i in RARITY_FILTER],
				value=RARITY_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Keyword',lindex)),
			dcc.Dropdown(
				id='collections-dropdown-keyword',
				options=[{'label': tr(i,lindex), 'value': i, 'disabled': True} for i in KEYWORD_FILTER],
				value=KEYWORD_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			)
		]
	elif current_page == '/mymatches':
		return	[
			html.H1(children=tr('MY MATCHES',lindex)),
			html.P(children="TBD"),
			dcc.Dropdown(
				id='collections-dropdown-theme',
				options=[{'label': i, 'value': i, 'disabled': True} for i in THEME_FILTER],
				value=THEME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children="TBD"),
			dcc.Dropdown(
				id='collections-dropdown-type',
				options=[{'label': i, 'value': i, 'disabled': True} for i in TYPE_FILTER],
				value=TYPE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children="TBD"),
			dcc.Dropdown(
				id='collections-dropdown-cost',
				options=[{'label': i, 'value': i, 'disabled': True} for i in COST_FILTER],
				value=COST_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children="TBD"),
			dcc.Dropdown(
				id='collections-dropdown-rarity',
				options=[{'label': i, 'value': i, 'disabled': True} for i in RARITY_FILTER],
				value=RARITY_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children="TBD"),
			dcc.Dropdown(
				id='collections-dropdown-keyword',
				options=[{'label': i, 'value': i, 'disabled': True} for i in KEYWORD_FILTER],
				value=KEYWORD_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			)
		]
	elif current_page == '/challenge':
		return	[
			html.H1(children=tr('CHALLENGE',lindex)),
			html.P(children="TBD"),
			html.P(children="Rank Range"),
			dcc.Dropdown(
				id='challenge-dropdown-rank',
				options=[{'label': i, 'value': i, 'disabled': True} for i in PLAYER_RANK],
				value=PLAYER_RANK[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
		]
	elif current_page == '/teamwars':
		return	[
			html.H1(children=tr('TEAMWARS',lindex)),
			html.P(children=tr('League',lindex)),
			dcc.Dropdown(
				id='teamwars-dropdown-league',
				options=[{'label': tr(i,lindex), 'value': i} for i in LEAGUES],
				value=LEAGUES[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
		]
	elif current_page == '/twmeta':
		return	[
			html.H1(children=tr('TEAMWARS',lindex)),
			html.P(children=tr('League',lindex)),
			dcc.Dropdown(
				id='twmeta-dropdown-league',
				options=[{'label': tr(i,lindex), 'value': i} for i in LEAGUES],
				value=LEAGUES[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
		]
	elif current_page == '/player' and data == None:
		return [
			html.H1(children=tr('PLAYERS',lindex)),
			html.P(children=tr('Search by Name Only',lindex)),
			dcc.Input(id='players-dropdown-name', type="text", placeholder=tr('<at least five letters>',lindex), value='', style=style_dropdown),
			html.Button(tr('Search',lindex),
				className="w3-button",
				id='players-dropdown-search-button'
			),
			html.P(children=tr('Rank Range',lindex)),
			dcc.Dropdown(
				id='players-dropdown-rank',
				options=[{'label': tr(i,lindex), 'value': i} for i in PLAYER_RANK],
				value=PLAYER_RANK[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr("Sort By",lindex)),
			dcc.Dropdown(
				id='players-dropdown-sort',
				options=[{'label': tr(i,lindex), 'value': i} for i in PLAYERS_SORT],
				value=PLAYERS_SORT[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
		]
	elif current_page == '/match':
		return [
			html.H1(children=tr('MATCHES',lindex)),
			html.P(children=tr('Rank Range',lindex)),
			dcc.Dropdown(
				id='match-dropdown-rank',
				options=[{'label': tr(i,lindex), 'value': i} for i in WIDE_PLAYER_RANK],
				value=WIDE_PLAYER_RANK[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Match Type',lindex)),
			dcc.Dropdown(
				id='match-dropdown-mode',
				options=[{'label': tr(i,lindex), 'value': i, 'disabled': False} for i in MODE_FILTER],
				value=MODE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
		]
	elif current_page == '/player' and data != None:
		return	[
			html.H1(children=tr('MY CARDS',lindex)),
			html.P(children=tr('Deck Theme',lindex)),
			dcc.Dropdown(
				id='player-dropdown-theme',
				options=[{'label': i, 'value': i, 'disabled': True} for i in THEME_FILTER],
				value=THEME_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Type',lindex)),
			dcc.Dropdown(
				id='player-dropdown-type',
				options=[{'label': i, 'value': i, 'disabled': True} for i in TYPE_FILTER],
				value=TYPE_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Cost',lindex)),
			dcc.Dropdown(
				id='player-dropdown-cost',
				options=[{'label': i, 'value': i, 'disabled': True} for i in COST_FILTER],
				value=COST_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Rarity',lindex)),
			dcc.Dropdown(
				id='player-dropdown-rarity',
				options=[{'label': i, 'value': i, 'disabled': True} for i in RARITY_FILTER],
				value=RARITY_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Keyword',lindex)),
			dcc.Dropdown(
				id='player-dropdown-keyword',
				options=[{'label': i, 'value': i, 'disabled': True} for i in KEYWORD_FILTER],
				value=KEYWORD_FILTER[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			)
		]
	elif current_page == '/teams' and data == None:
		return [
			html.H1(children=tr('TEAMS',lindex)),
			html.P(children=tr('Rank Range',lindex)),
			dcc.Dropdown(
				id='teams-dropdown-rank',
				options=[{'label': tr(i,lindex), 'value': i} for i in TEAM_RANK],
				value=TEAM_RANK[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Max Members',lindex)),
			dcc.Dropdown(
				id='teams-dropdown-members',
				options=[{'label': i, 'value': i} for i in TEAM_MEMBERS],
				value=TEAM_MEMBERS[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Min NK Level',lindex)),
			dcc.Dropdown(
				id='teams-dropdown-nklevel',
				options=[{'label': i, 'value': i} for i in TEAM_NKLEVEL],
				value=TEAM_NKLEVEL[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.P(children=tr('Status',lindex)),
			dcc.Dropdown(
				id='teams-dropdown-status',
				options=[{'label': i, 'value': i} for i in TEAM_STATUS],
				value=TEAM_STATUS[0],
				searchable=False,
				clearable=False,
				style=style_dropdown
			)
		]
	elif current_page == '/teams' and data != None:
		return	html.Div(children=[
			html.H1(children=tr('Team Dashboard',lindex)),
			dcc.Link(tr('Back to Teams',lindex),href='/teams'),
			html.P(children=tr('Under Construction',lindex))
			],
			style=style_sidebar
		)
	return html.Div(children=[
			html.P(children=tr('Under Construction',lindex))
			],
			style=style_sidebar
	)
	
def getAccountsPrimaryOnTop(g_user):
	primary_accounts=[]
	non_primary_accounts=[]
	accounts=HELPER_DB.getAccounts(g_user)
	for account in accounts:
		name=account[0]
		primary=account[1]
		if primary:
			primary_accounts.append(name)
		else:
			non_primary_accounts.append(name)
	primary_accounts.extend(non_primary_accounts)
	if len(primary_accounts) == 0:
		primary_accounts.append(tr('Link SPPD Account'))
	return primary_accounts
	
def getHeader(g_user=None,is_settings_page=False,lang_index=0):
	PAGES=[
		'Players',
		'Teams',
		'Matches',
		'Brackets',
		'Events',
		'Downloads',
		'Donate',
		'About',
		'News'
	]
	LINKS=[
		'player',
		'teams',
		'match',
		'brackets',
		'events',
		'downloads',
		'donate',
		'about',
		'articles'
	]
	style_link_disabled={
		'pointer-events': 'none',
		'cursor': 'default'
	}
	myProfile="/player"
	myTeam="/teams"
	if g_user != None:
		okta_id=g_user.id
		user_id=HELPER_DB.getUserIDFromOktaID(okta_id)
		if user_id != None:
			team=HELPER_DB.getTeamFromUserID(user_id)
			unique_user_id=HELPER_DB.getUniqueUserIDfromInGameUserID(user_id)
			if team != None:
				myTeam=f"/teams/{team}"
			if unique_user_id != None:
				myProfile=f"/player/{unique_user_id}"
	login_button = ""
	if g_user == None:
		login_button = html.Div(children=
			html.A([
				html.Span(className="glyphicon glyphicon-log-in",
					style={'display': 'inline-block'}
				),
				html.Div(tr('Login',lang_index),
						className="collapse",
						style={'display': 'inline-block', 'font-weight': 'bold'}
				)],
				href='/login',
				className="w3-button"
			),
			className="w3-dropdown-hover w3-right",
		)
	else:
		accounts_list = getAccountsPrimaryOnTop(g_user)
		name = accounts_list[0]
		need_link = name == "Link SPPD Account"
		#style_link_disabled
		if need_link:
			login_button = html.Div(children=[
				dcc.Link(name, href='/settings', className="w3-button"),
				html.Div(children=[
					dcc.Link(html.Span(' ' + tr('Settings',lang_index),
						className="glyphicon glyphicon-cog"
						), href='/settings', className="w3-bar-item w3-button"
					),
					html.A(html.Span(' ' + tr('Logout',lang_index),
						className="glyphicon glyphicon-log-out"
						), href='/logout', className="w3-bar-item w3-button"
					)],
					className="w3-dropdown-content w3-bar-block w3-card-4"
				)
				],
				className="w3-dropdown-hover w3-right",
			)
		else:
			non_primary_accounts=[html.Button(accounts_list[index],
						className="w3-button w3-bar-item",
						id=f'header-primary-button-{index}'
					) for index in range(1,len(accounts_list[1:])+1)]
			invisible_accounts=[html.Button("",
						className="w3-button",
						id=f'header-primary-button-{index}',
						style={'display': 'none'}
					) for index in range(len(accounts_list),10)]
			login_button = html.Div(id='users-list',children=[
				html.Button(html.Span(' ' + name,
					className="glyphicon glyphicon-user"
					), className="w3-button"
				),
				html.Div(children=[
					*non_primary_accounts,
					*invisible_accounts,
					dcc.Link(html.Span(' ' + tr('Settings',lang_index),
						className="glyphicon glyphicon-cog"
						), href='/settings', className="w3-bar-item w3-button"
					),
					html.A(html.Span(' ' + tr('Logout',lang_index),
						className="glyphicon glyphicon-log-out"
						), href='/logout', className="w3-bar-item w3-button"
					)],
					className="w3-dropdown-content w3-bar-block w3-card-4"
				)
				],
				className="w3-dropdown-hover w3-right",
			)
	non_primary_languages=[html.Button(LANGUAGES[index],
				className="w3-button w3-bar-item",
				id=f'language-button-{index}'
			) for index in range(len(LANGUAGES))]
	language_button = html.Div(id='language-list',children=[
				html.Button([
					html.Span(className="glyphicon glyphicon-globe",
						style={'display': 'inline-block'}
					),
					html.Div(LANGUAGES[lang_index],
							className="collapse",
							style={'display': 'inline-block', 'font-weight': 'bold'}
					)
					],
					className="w3-button"
				),
				html.Div(children=non_primary_languages,
					className="w3-dropdown-content w3-bar-block w3-card-4",
				)
				],
				className="w3-dropdown-hover w3-right",
			)
	my_data_id = 'my-settings-data' if is_settings_page else 'my-data'
	

	return html.Div(children=[
		html.Button("☰",
				#html.Span(
				#	className="glyphicon glyphicon-menu-hamburger"
				#),
			id='main-sidebar-open',
			className="w3-button"
		),
		login_button,
		html.Div(children=[
			html.Button([
				html.Span(className="glyphicon glyphicon-home",
					style={'display': 'inline-block'}
				),
				html.Div(tr('My Data',lang_index),
						className="collapse",
						style={'display': 'inline-block', 'font-weight': 'bold'}
				)
				],
				className="w3-button"
			),
			html.Div(id=my_data_id,children=[
				dcc.Link(tr('My Profile',lang_index), href=myProfile, className="w3-bar-item w3-button"),
				dcc.Link(tr('My Team',lang_index), href=myTeam, className="w3-bar-item w3-button"),
				html.A(tr('My Cards',lang_index), href='/mycards', className="w3-bar-item w3-button"),
				#dcc.Link('My Decks', href='#', className="w3-bar-item w3-button", style=style_link_disabled),
				html.A(tr('My Matches',lang_index), href='/mymatches', className="w3-bar-item w3-button"),
					#html.Span('My Matches',
					#	className="glyphicon glyphicon-play-circle"
					#),
				#dcc.Link('My Packs', href='#', className="w3-bar-item w3-button", style=style_link_disabled),
				#dcc.Link('My Lockers', href='#', className="w3-bar-item w3-button", style=style_link_disabled),
				#dcc.Link('My Replays', href='#', className="w3-bar-item w3-button", style=style_link_disabled),
				],
				className="w3-dropdown-content w3-bar-block w3-card-4"
			)
			],
			className="w3-dropdown-hover w3-right",
		),
		language_button
		],
		className="w3-black",
		style={'position': 'sticky'}
	)
	
def getMainSideBar(lang_index=0):
	return html.Nav(children=[
			html.Div(children=[
				html.Button(html.Span(
					className="glyphicon glyphicon-remove"),
					id='main-sidebar-close',
					className="w3-button w3-display-topright w3-xlarge"
				)],
				className="w3-red",
				style={'top': 0, 'position': 'sticky'}
			),
			dcc.Link(html.Span(' ' + tr('Themes',lang_index),
					className="glyphicon glyphicon-flash"
				), href='/themes', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Decks',lang_index),
					className="glyphicon glyphicon-tags"
				), href='/decks', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Deck Builder',lang_index),
					className="glyphicon glyphicon-tags"
				), href='/deckbuilder', className="w3-bar-item w3-button",
				style={'margin-left': '25%'}),
			dcc.Link(html.Span(' ' + tr('Cards',lang_index),
					className="glyphicon glyphicon-tag"
				), href='/cards', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('All Cards',lang_index),
					className="glyphicon glyphicon-tag"
				), href='/allcards', className="w3-bar-item w3-button",
				style={'margin-left': '25%'}),
			dcc.Link(html.Span(' ' + tr('Compare',lang_index),
					className="glyphicon glyphicon-tag"
				), href='/compare', className="w3-bar-item w3-button",
				style={'margin-left': '25%'}),
			dcc.Link(html.Span(' ' + tr('Cards DPS',lang_index),
					className="glyphicon glyphicon-tag"
				), href='/cardstats', className="w3-bar-item w3-button",
				style={'margin-left': '25%'}),
			dcc.Link(html.Span(' ' + tr('Build-A-Card',lang_index),
					className="glyphicon glyphicon-star-empty"
				), href='/build', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Upgrade Calculator',lang_index),
					className="glyphicon glyphicon-star-empty"
				), href='/calc', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Players',lang_index),
					className="glyphicon glyphicon-user"
				), href='/player', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Teams',lang_index),
					className="glyphicon glyphicon-plane"
				), href='/teams', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Brackets',lang_index),
					className="glyphicon glyphicon-dashboard"
				), href='/brackets', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Matches',lang_index),
					className="glyphicon glyphicon-fire"
				), href='/match', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Events',lang_index),
					className="glyphicon glyphicon-calendar"
				), href='/events', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Challenge',lang_index),
					className="glyphicon glyphicon-tag"
				), href='/challenge', className="w3-bar-item w3-button",
				style={'margin-left': '25%'}),
			dcc.Link(html.Span(' ' + tr('Team-Wars',lang_index),
					className="glyphicon glyphicon-tag"
				), href='/teamwars', className="w3-bar-item w3-button",
				style={'margin-left': '25%'}),
			dcc.Link(html.Span(' ' + tr('TW Meta',lang_index),
					className="glyphicon glyphicon-tag"
				), href='/twmeta', className="w3-bar-item w3-button",
				style={'margin-left': '25%'}),
			dcc.Link(html.Span(' ' + tr('Downloads',lang_index),
					className="glyphicon glyphicon-download-alt"
				), href='/downloads', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Donate',lang_index),
					className="glyphicon glyphicon-usd"
				), href='/donate', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('About',lang_index),
					className="glyphicon glyphicon-info-sign"
				), href='/about', className="w3-bar-item w3-button"),
			dcc.Link(html.Span(' ' + tr('Articles',lang_index),
					className="glyphicon glyphicon-comment"
				), href='/articles', className="w3-bar-item w3-button"),
			],
			className="w3-sidebar w3-bar-block w3-dark-grey w3-animate-left",
			style = {'top': 0, 'display': 'none'},
			id='main-sidebar'
		)
		
def buildSidebarCustom(unique_id,description="",lang_index=0):
	return [html.Div(children=[
		html.Div(children=[
			html.Button(html.Span(
				className="glyphicon glyphicon-remove"),
				id=f'{unique_id}-sidebar-button-close',
				n_clicks=0,
				className="w3-button w3-display-topright w3-xlarge"
			)],
			className="w3-red",
			style={'top': 0, 'position': 'sticky'}
		),
		html.Div(children=getSideBar(f"/{unique_id}",lindex=lang_index))
		],
		className="w3-sidebar w3-dark-grey w3-animate-left",
		style={'top':0,'display':'none'},
		id=f'{unique_id}-sidebar',
	),
	html.Div(children=[
		html.Button(
			html.Span(tr('Filter',lang_index),
				className="glyphicon glyphicon-filter"
			),
			id=f'{unique_id}-sidebar-button-open',
			n_clicks=0,
			className="btn btn-default btn-sm"
		),
		description,
		html.Div(
			className="w3-container",
			id=f'{unique_id}-content'
		)
	])]
	
def donate_button():
	return html.Form([
		dcc.Input(name="cmd", value="_donations", type='hidden'),
		dcc.Input(name="item_name", value="SPPD Deck Tracker", type='hidden'),
		dcc.Input(name="business", value="RT6V8ULGM6JQ4", type='hidden'),
		dcc.Input(name="currency_code", value="USD", type='hidden'),
		html.Button(
			html.Img(
				src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif",
				style={
					'border': '0',
					'alt': "Donate with PayPal button",
					'title': "PayPal - The safer, easier way to pay online!"
				}
			),'Donate', type='submit'
		),
		#dcc.Input(name="submit",
		#	type='image',
		#	style={
		#		'border': '0',
		#		'alt': "Donate with PayPal button",
		#		'title': "PayPal - The safer, easier way to pay online!",
		#		'src': "https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif"
		#	}
		#),
		#html.Img(src="https://www.paypal.com/en_US/i/scr/pixel.gif",
		#	style={
		#		'border': '0',
		#		'alt': "",
		#		'width': "1",
		#		'height': "1"
		#	}
		#)
		],
		action="https://www.paypal.com/cgi-bin/webscr",
		method="post",
		target="_top"
	)
	
def listAccounts(ACCOUNTS, response=None, is_paid_user=False): #ACCOUNTS = [ [name_str, primary_bool], ... ]
	html_result=[]
	index=0
	if response != None and "userid_claimed" in response:
		html_result.append(html.H3("Account has already been claimed"))
	if response != None and "logged_out" in response:
		html_result.append(html.H3("You are not logged in. Refresh the page."))
	for elem in ACCOUNTS:
		html_result.append(
			html.Div(children=[
				html.Button(elem[0],
					className="w3-button",
					style = {'width': '280px'}
				),
				html.Button('Make Primary' if not elem[1] else "(Primary)",
					className="w3-button",
					disabled=elem[1],
					id=f'settings-primary-button-{index}',
					style = {'width': '140px'}
				),
				html.Button('Delete',
					className="w3-button",
					id=f'settings-delete-button-{index}',
					style = {'width': '90px'}
				),
				html.Button('Opt-In' if elem[2] else 'Opt-out',
					className="w3-button",
					id=f'settings-optout-button-{index}',
					style = {'width': '90px'}
				)
				],
				style={'display': 'inline-block'}
			)
		)
		html_result.append(html.Br())
		index+=1
	max_accounts = 3
	if is_paid_user: max_accounts = 10
	for i in range(len(ACCOUNTS),max_accounts):
		html_result.append(
			html.Div(children=[
				html.Button("<Add an account>",
					disabled=True,
					className="w3-button",
					style = {'width': '280px'}
				),
				html.Button('Make Primary',
					className="w3-button",
					disabled=True,
					id=f'settings-primary-button-{index}',
					style = {'width': '140px'}
				),
				html.Button('Delete',
					disabled=True,
					className="w3-button",
					id=f'settings-delete-button-{index}',
					style = {'width': '90px'}
				),
				html.Button('Opt-out',
					className="w3-button",
					disabled=True,
					id=f'settings-optout-button-{index}',
					style = {'width': '90px'}
				)
				],
				style={'display': 'inline-block'}
			)
		)
		html_result.append(html.Br())
		index+=1
	if max_accounts == 10: return html_result
	for i in range(max_accounts,10):
		html_result.append(
			html.Div(children=[
				html.Button("<Add an account>",
					disabled=True,
					className="w3-button",
					style = {'width': '280px'}
				),
				html.Button('Make Primary',
					className="w3-button",
					disabled=True,
					id=f'settings-primary-button-{index}',
					style = {'width': '140px'}
				),
				html.Button('Delete',
					disabled=True,
					className="w3-button",
					id=f'settings-delete-button-{index}',
					style = {'width': '90px'}
				),
				html.Button('Opt-out',
					className="w3-button",
					disabled=True,
					id=f'settings-optout-button-{index}',
					style = {'width': '90px'}
				)
				],
				style={'display': 'none'}
			)
		)
		html_result.append(html.Br())
		index+=1
	return html_result
	
def getSettingsContent(g_user,lang_index=0):
	style_box={
		'width': '320px',
		'padding': '10px',
		'border': '5px solid gray',
		'margin': '0',
	}
	if g_user == None:
		return html.Div(children=[
			html.H1(tr('You need to log in to view this page',lang_index))
			],
			className="w3-container",
			style=style_box,
			id='settings-content'
		)
	ACCOUNTS=HELPER_DB.getAccounts(g_user)
	return html.Div(children=[
		html.H1(tr('Connected Accounts',lang_index)),
		html.Div(id='settings-accounts', children=listAccounts(ACCOUNTS)),
		html.H1(tr('Add Account',lang_index)),
		html.H3(tr('Your Tracking ID',lang_index)),
		html.H5(tr('Note: Tracking ID is A-F and 0-9.',lang_index)),
		dcc.Input(id="input-tracking-id", type="text", placeholder="12345678-abcd-abcd-abcd-123456789012", value='',style={
			'text-transform': 'lowercase',
			'font-variant': 'all-small-caps',
			'color': 'black'
		}),
		html.Button(tr('Add',lang_index),
				className="w3-button",
				id='settings-add-button'
		),
		dcc.Markdown(tr('''
		
			**How do I find my TRACKING ID?**
			
			1. Go to SPPD's In-Game Settings
			
			![Settings](https://i.imgur.com/IL2VXGQ.png)
			
			2. Scroll to the bottom
			
			![Tracking ID](https://i.imgur.com/zxeD4NS.png)
			
			If you have any questions: [Join the discord](https://discord.gg/m95hg3S)!
				
		''',lang_index))
		],
		className="w3-container",
		id='settings-content'
	)
	
def getTMCContent(lang_index=0):
	style_box={
		'width': '320px',
		'padding': '10px',
		'border': '5px solid gray',
		'margin': '0',
	}
	return html.Div(children=[
		html.H1(tr('Add your Android account to Team Manager Cloud',lang_index)),
		html.H3(tr('By clicking Add, you understand this service is free with an optional recommended 2$ per month donation, you can donate for more than 1 month if desired.',lang_index)),
		dcc.Input(id="tmc-em", type="text", placeholder="you@gmail.com", value='',style={
			'color': 'black'
		}),
		dcc.Input(id="tmc-pw", type="text", placeholder="********", value='',style={
			'color': 'black'
		}),
		html.Button(tr('Add',lang_index),
				className="w3-button",
				id='tmc-add-button',
				disabled=False,
		),
		dcc.Store(id="tmc-response-data",data=0),
		html.Div(id='tmc-in-progress'),
		html.Div(id='tmc-response'),
		dcc.Markdown(tr('''
		
		**What does Team Manager Cloud offer?**

		* Track Team War Upgrade Spending
			* who spends where
		* Track Team War Bracket Details
			* How many runs each team has and their current average score
		* Track Team Wars History (Scores/Caps)
		* Track Card Requests
			* Who is requesting which cards and when.
		* Track Card Donations
			* Who Donated What (and to who it was donated)
			* Track who donated the most today, this week, this month.
		* Auto-Accept/Reject team members based on your team's Application tab, where you can set a Whitelist/Blacklist.
		* Auto-Role Assignment after Auto-Accept (Auto assigning Leader role is disabled)
		* Track Weekend Event Participation
		
		Notes:
		
		* If a link pops up, you must verify your account, then try again.
		* If you have two factor authentication, you must generate a one-time-use password here: https://support.google.com/accounts/answer/185833?hl=en. You can delete it at any time.
		* Changing your password will disable the Team Manager cloud from running, and you will need to Add it again.
		* iOS accounts are NOT supported. Only Android Google Play Accounts that have been used to connect to South Park Phone Destroyer.
		
		**Frequently Asked Questions**
		
		* What should I do if I am concerned about using my primary email account.?
			* You can create a new throw-away alternate account to join your team and use that.
		* Can you remove my account from the Team Manager Cloud, because I don't want to change my password?
			* Yes. Ask and you shall receive. And by ask, I mean direct message me the associated email address on **DISCORD**.
		* What should I do if $2 (USD) per account per month is too much?
			* Message me on **DISCORD** and we can work something out. I am not in it for the money, just trying to cover cloud server expenses.
		''',lang_index))
		],
		className="w3-container",
		id='tmc-content'
	)
	
def getCalcContent(lang_index=0):
	style_dropdown={
		'text-transform': 'lowercase',
		'font-variant': 'all-small-caps',
		'color': 'black'
	}
	options = []
	for level in DATABASE.WAL_MAP:
		if level == 0: continue
		start, end = DATABASE.WAL_MAP[level]
		for upgrade in range(start,end+1):
			if upgrade == 0: continue
			options.append([f"L{level} {upgrade}/{end}",f"{level}-{upgrade}"])
					
	RARITY = ["Common", "Rare", "Epic", "Legendary"]
	return html.Div(children=[
		html.H1(tr('Card Upgrade Calculator',lang_index)),
		html.H3(children=tr('Rarity',lang_index)),
		dcc.Dropdown(
			id='calc-dropdown-rarity',
			options=[{'label': i, 'value': i} for i in RARITY],
			value=RARITY[0],
			searchable=False,
			clearable=False,
			style=style_dropdown
		),
		html.H3(tr('Current Level',lang_index)),
		dcc.Dropdown(
			id='calc-dropdown-from',
			options=[{'label': label, 'value': value} for label, value in options],
			value=options[0][1],
			searchable=False,
			clearable=False,
			style=style_dropdown
		),
		html.H3(tr('Target Level',lang_index)),
		dcc.Dropdown(
			id='calc-dropdown-to',
			options=[{'label': label, 'value': value} for label, value in options],
			value=options[0][1],
			searchable=False,
			clearable=False,
			style=style_dropdown
		),
		html.Div(id='calc-response')
		],
		className="w3-container",
		id='calc-content'
	)
	
def getDataFromBulkString(long_string):
	data=[]
	if "," not in long_string: return data
	split_string=long_string.split(",")
	for elem in split_string:
		if ":" not in elem: continue
		card_split=elem.split(":")
		card_name=card_split[0].lower().strip(' ')
		if card_name not in DATABASE.LOWER_NAME_TO_ID:
			print(f"\t[Warning] Unable to find card_name in '{elem}'")
			continue
		card_id=DATABASE.LOWER_NAME_TO_ID[card_name]
		card_name_proper=DATABASE.DECK_MAP[card_id][0]
		try:
			card_level=0
			card_upgrades=0
			card_level_upgrade=card_split[1]
			if "." in card_level_upgrade:
				card_level_upgrade_split=card_level_upgrade.split(".")
				card_level=int(card_level_upgrade_split[0])
				card_upgrades=int(card_level_upgrade_split[1])
				min_upgrades,max_upgrades=DATABASE.WAL_MAP[card_level]
				if not (card_upgrades >= min_upgrades or card_upgrades <= max_upgrades):
					card_upgrades = card_upgrades * 10
					if not (card_upgrades >= min_upgrades or card_upgrades <= max_upgrades):
						card_upgrades=0
			else:
				card_level=int(card_level_upgrade)
			min_upgrades,max_upgrades=DATABASE.WAL_MAP[card_level]
			one_elem={'id': card_name_proper, 'Level': card_level, 'Upgrades': f'{card_upgrades}/{max_upgrades}'}
			data.append(one_elem)
		except:
			print(f"\t[Warning] Failed to parse '{elem}'")
			pass
	return data
	
def generate_nklevel_graph(nk_level_array):
	nk_dict=dict()
	total_nks=0
	for level in nk_level_array:
		if level not in nk_dict:
			nk_dict[level]=0
		nk_dict[level]+=1
		total_nks+=1
	x=[] # Unique NK Levels (ordered)
	y=[] # % of total NKs
	for level in sorted(nk_dict.keys()):
		x.append(level)
		y.append(100*float(nk_dict[level])/total_nks)
	return x,y
		
def getPageCount(pathname):
	if "/" not in pathname: return 0
	global PAGE_TRACKER
	last_index = pathname.rindex('/')
	substr = pathname
	if last_index > 0:
		substr = pathname[:last_index+1]
	if substr not in PAGE_TRACKER:
		PAGE_TRACKER[substr]=0
	PAGE_TRACKER[substr]+=1
	return PAGE_TRACKER[substr]
	
def printPageView(g_user, pathname):
	accounts=HELPER_DB.getAccounts(g_user)
	pc=getPageCount(pathname)
	USERNAME=""
	if len(accounts) > 0:
		USERNAME=", User: "
		USERNAME+=", ".join(x[0] for x in accounts[:3])
	print(f"Page: {pathname}, {pc}{USERNAME}")
	
PAGE_TRACKER={}
