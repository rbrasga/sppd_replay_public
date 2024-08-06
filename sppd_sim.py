# -*- coding: utf-8 -*-
"""
 SPPD_SIM
 Created 10/22/19
 Updated 09/02/20
 Current Version: 2.00
----------------------
WSGI Server (cherrypy):
	Webserver (Flask):
		Web Application (Dash)
        
Setup:
* Install Python 3.7+ 64-bit

As Administrator - install these packages using pip.

* sppd_sim requires these packages
   * cherrypy
   * flask, flask_oidc
   * dash
   * okta
   * pandas
   * mysql-connector-python
   * dash_bootstrap_components
   * pillow

   
* sppd_restful requires these packages
   * waitress
   
* SCHEDULER requires these packages
   * schedule
   
* SPPD_API requires these packages
   * gpsoauth


"""
import asyncio
import threading
import traceback
import cherrypy
#from waitress import serve
from flask import send_from_directory
from flask import Flask, render_template, g, redirect, request
from flask_oidc import OpenIDConnect
#from okta import UsersClient
from okta.client import Client as OktaClient
from okta.resource_clients.user_client import UserClient

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt

import decimal
import pandas
from collections import OrderedDict
import os, re, sys, time, datetime

import HELPER
from api import SPPD_API
import RESTFUL
import HELPER_DB
import DATABASE
import ARTICLES
import NK_ART

#Card Builder Libraries
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64
import textwrap
import random

#SSH for team manager cloud
import HELPER_SSH
#g.user.id
#g.user.profile.firstName

SPPD_API.setUsernamePassword("<email address>","")

"""
TO DO:
* Add Footer - giving credit to Okta and state that this website is not in any way affiliated with the game

Add this right after <body> or <head> in dash.py:
		<!-- Global site tag (gtag.js) - Google Analytics -->
		<script async src="https://www.googletagmanager.com/gtag/js?id=UA-177063001-1"></script>
		<script>
		  window.dataLayer = window.dataLayer || [];
		  function gtag(){dataLayer.push(arguments);}
		  gtag('js', new Date());

		  gtag('config', 'UA-177063001-1');
		</script>
		<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
		<!-- Horiz -->
		<ins class="adsbygoogle"
			style="display:inline-block;width:100%;height:100px"
			 data-ad-client="ca-pub-6246309647896152"
			 data-ad-slot="9682316342"></ins>
		<script>
			 (adsbygoogle = window.adsbygoogle || []).push({});
		</script>
"""

"""
#print(dir(dash))
['Dash', '_CallbackContext', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', '_callback_context', '_configs', '_utils', '_watch', 'callback_context', 'dash', 'dependencies', 'development', 'exceptions', 'fingerprint', 'no_update', 'resources', 'version']

#print(dir(dcc))
['Checklist', 'ConfirmDialog', 'ConfirmDialogProvider', 'DatePickerRange', 'DatePickerSingle', 'Dropdown', 'Graph', 'Input', 'Interval', 'Link', 'Loading', 'Location', 'LogoutButton', 'Markdown', 'RadioItems', 'RangeSlider', 'Slider', 'Store', 'Tab', 'Tabs', 'Textarea', 'Upload', '_', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', '_basepath', '_component', '_current_path', '_dash', '_filepath', '_imports_', '_js_dist', '_os', '_sys', '_this_module', 'f', 'json', 'package', 'package_name']

#print(dir(html))
['A', 'Abbr', 'Acronym', 'Address', 'Area', 'Article', 'Aside', 'Audio', 'B', 'Base', 'Basefont', 'Bdi', 'Bdo', 'Big', 'Blink', 'Blockquote', 'Br', 'Button', 'Canvas', 'Caption', 'Center', 'Cite', 'Code', 'Col', 'Colgroup', 'Command', 'Content', 'Data', 'Datalist', 'Dd', 'Del', 'Details', 'Dfn', 'Dialog', 'Div', 'Dl', 'Dt', 'Element', 'Em', 'Embed', 'Fieldset', 'Figcaption', 'Figure', 'Font', 'Footer', 'Form', 'Frame', 'Frameset', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Header', 'Hgroup', 'Hr', 'I', 'Iframe', 'Img', 'Ins', 'Isindex', 'Kbd', 'Keygen', 'Label', 'Legend', 'Li', 'Link', 'Listing', 'Main', 'MapEl', 'Mark', 'Marquee', 'Meta', 'Meter', 'Multicol', 'Nav', 'Nextid', 'Nobr', 'Noscript', 'ObjectEl', 'Ol', 'Optgroup', 'Option', 'Output', 'P', 'Param', 'Picture', 'Plaintext', 'Pre', 'Progress', 'Q', 'Rb', 'Rp', 'Rt', 'Rtc', 'Ruby', 'S', 'Samp', 'Script', 'Section', 'Select', 'Shadow', 'Slot', 'Small', 'Source', 'Spacer', 'Span', 'Strike', 'Strong', 'Sub', 'Summary', 'Sup', 'Table', 'Tbody', 'Td', 'Template', 'Textarea', 'Tfoot', 'Th', 'Thead', 'Time', 'Title', 'Tr', 'Track', 'U', 'Ul', 'Var', 'Video', 'Wbr', 'Xmp', '_', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', '_basepath', '_component', '_css_dist', '_current_path', '_dash', '_filepath', '_imports_', '_js_dist', '_os', '_sys', '_this_module', 'f', 'json', 'package', 'package_name']
"""
"""
dcc.Input(...)
Allowed arguments: autoComplete, autoFocus, className, debounce, disabled, id, inputMode, list, loading_state, max, maxLength, min, minLength, multiple, n_blur, n_blur_timestamp, n_submit, n_submit_timestamp, name, pattern, persisted_props, persistence, persistence_type, placeholder, readOnly, required, selectionDirection, selectionEnd, selectionStart, size, spellCheck, step, style, type, value
"""

#SECRET_KEY=''.join(random.choice('0123456789abcdef') for n in range(64))
#print(SECRET_KEY)

SPPDREPLAY="https://sppdreplay.net"
###SETUP DASH
#<script data-ad-client="ca-pub-6246309647896152" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
external_scripts=[
]
external_stylesheets = [
	'https://www.w3schools.com/lib/w3.css',
	#'https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css',
	"https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap-glyphicons.css",
	f"{SPPDREPLAY}/static/stylesheet.css",
	]

app = dash.Dash(__name__, external_scripts=external_scripts, external_stylesheets=external_stylesheets, meta_tags=[
    # A description of the app, used by e.g.
    # search engines when displaying search results.
    {
        'name': 'description',
        'content': 'South Park Phone Destroyer Replay - bringing advanced gaming analytics and tools to the players'
    },
    # A tag that tells Internet Explorer (IE)
    # to use the latest renderer version available
    # to that browser (e.g. Edge)
    {
        'http-equiv': 'X-UA-Compatible',
        'content': 'IE=edge'
    },
    # A tag that tells the browser not to scale
    # desktop widths to fit mobile screens.
    # Sets the width of the viewport (browser)
    # to the width of the device, and the zoom level
    # (initial scale) to 1.
    #
    # Necessary for "true" mobile support.
    {
      'name': 'viewport',
      'content': 'width=device-width, initial-scale=1.0'
    }
	])

app.title = "SPPDReplay.net - Unleash your potential"
# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
app.config.suppress_callback_exceptions = True

###SETUP SERVER
server = app.server
server.config["OIDC_CLIENT_SECRETS"] = "client_secrets.json"
server.config["OIDC_COOKIE_SECURE"] = False
server.config["OIDC_CALLBACK_ROUTE"] = "/oidc/callback"
server.config["OIDC_SCOPES"] = ["openid", "email", "profile"]
server.secret_key = '<secret key>'
server.config["OIDC_ID_TOKEN_COOKIE_NAME"] = "oidc_token"
oidc = OpenIDConnect(server)

class GPROFILE():
	def __init__(self, first_name, last_name, email):
		self.firstName = first_name
		self.lastName = last_name
		self.email = email

class GUSER():
	def __init__(self, user_data):
		self.id = user_data.id
		self.profile = GPROFILE(user_data.profile.first_name, user_data.profile.last_name, user_data.profile.email)

config = {
	'orgUrl': 'https://<org>.okta.com',
	#'authorizationMode': 'PrivateKey',
	'clientId': '<client id>',
	#'scopes': ['okta.users.manage'],
	'token': '<token>' #sppdreplay
}
okta_client = OktaClient(config)

tab_styles = {
	'height': '44px',
	'backgroundColor': 'rgb(50, 50, 50)',
	'padding': '1px',
	'color': 'white'
}
tab_style = {
	'backgroundColor': 'rgb(50, 50, 50)',
	'padding': '1px',
	'color': 'white',
	'fontWeight': 'bold'
}
tab_selected_style = {
	'backgroundColor': '#119DFF',
	'padding': '1px',
	'color': 'white'
}

from functools import wraps

from asyncio.proactor_events import _ProactorBasePipeTransport

def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise
    return wrapper

_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)

OKTALock = threading.Condition()

def get_okta_user(oktaid):
	user_info,resp,err = None,None,True
	global okta_client,OKTALock
	try:
		OKTALock.acquire()
		user_info,resp,err = asyncio.run(okta_client.get_user(oktaid))
		OKTALock.notify()
		OKTALock.release()
	except:
		print("ERROR get_okta_user")
		OKTALock.notify()
		OKTALock.release()
		pass
	return user_info,resp,err
	

'''
@cherrypy.expose
def index(self, clsname):
    if "ddns" in cherrypy.request.headers['Host']:
        raise cherrypy.HTTPRedirect(SPPDREPLAY)
    return str(globals()[clsname].created)
'''
@server.before_request
def before_request():
	if 'Host' in request.headers and "ddns" in request.headers['Host']:
		return redirect(SPPDREPLAY)
	LOGGEDIN=False
	try:
		LOGGEDIN=oidc.user_loggedin
	except:
		print("[ERROR] Failed to check if the user was logged in!")
	if LOGGEDIN and (not hasattr(g, 'user') or g.user == None):
		try:
			#global okta_client
			#user_info,resp,err = asyncio.run(okta_client.get_user(oidc.user_getfield("sub")))
			oktaid = oidc.user_getfield("sub")
			if type(oktaid) == str and len(oktaid) >= 15:
				global okta_client
				#user_info,resp,err = asyncio.run(okta_client.get_user(oktaid))
				user_info,resp,err = get_okta_user(oktaid)
				if err == None:
					g.user = GUSER(user_info)
				elif err == False and user_info == None:
					return
				else:
					g.user = None
			else:
				g.user = None
			#name=g.user.profile.firstName
			#email=g.user.profile.email
		except:
			g.user = None
			print(f'[Warning] Failed - okta_client.get_user({oidc.user_getfield("sub")})')
	else:
		g.user = None

@server.route("/")
def index():
	return redirect('/')

@server.route("/login")
@oidc.require_login
def login():
	return redirect('/')

@server.route("/logout")
def logout():
	try:
		oidc.logout()
	except:
		print("[ERROR] Failed logout the user!")
	return redirect('/')
	
@server.route('/static/<path>')
def static_file(path):
	if ".." in path:
		flask.abort(401)
	static_folder = os.path.join(os.getcwd(), 'static')
	return send_from_directory(static_folder, path)
	
@server.route('/ads.txt')
def ads_file():
    static_folder = os.getcwd()
    return send_from_directory(static_folder, 'ads.txt')
	
@server.route('/.shutdown')
def shutdown_cherrypy():  
	cherrypy.engine.exit()
	return redirect('/')
	
###END SERVER

###CHERRYPY
	
# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
			[dash.dependencies.Input('url', 'pathname'),
			dash.dependencies.Input('url', 'search'),
			dash.dependencies.Input('hidden-time-output','data'),
			dash.dependencies.Input('hidden-language-output','data')])
def display_page(pathname, search, gmtOffset=480, lang_index=0):
	full_search = {}
	if search != None and "?" in search:
		tmp_search = search.strip("?")
		if "&" in tmp_search:
			n_search = tmp_search.split("&")
			for elem in n_search:
				eq_search = elem.split("=")
				if len(eq_search) == 2:
					full_search[eq_search[0]]=eq_search[1]
		else:
			eq_search = tmp_search.split("=")
			if len(eq_search) == 2:
				full_search[eq_search[0]]=eq_search[1]
	if pathname != None:
		full_path = pathname
		if search != None:full_path+= search
		HELPER.printPageView(g.user, full_path)
		pathname = pathname.lower()
	if pathname == '/downloads':
		return SPPDSIM.downloads_layout(lindex=lang_index)
	elif pathname == '/donate':
		return SPPDSIM.donate_layout(lindex=lang_index)
	elif pathname == '/decks':
		return SPPDSIM.decks_layout(lindex=lang_index)
	elif pathname == '/cards':
		return SPPDSIM.cards_layout(lindex=lang_index)
	elif pathname == '/allcards':
		return SPPDSIM.allcards_layout(lindex=lang_index)
	elif isinstance(pathname, str) and '/cards/' in pathname:
		card_id=pathname.strip('/cards/')
		match = re.match('^[0-9]+$', card_id, re.I)
		if match == None:
			return SPPDSIM.cards_layout(lindex=lang_index)
		return SPPDSIM.cards_layout(card_id,lindex=lang_index)
	elif pathname == '/cardstats':
		return SPPDSIM.cardstats_layout(lindex=lang_index)
	elif pathname == '/deckbuilder':
		return SPPDSIM.deckbuilder_layout(lindex=lang_index)
	elif pathname == '/compare':
		return SPPDSIM.compare_layout(lindex=lang_index)
	elif pathname == '/themes':
		return SPPDSIM.themes_layout(lindex=lang_index)
	elif pathname == '/settings':
		return SPPDSIM.settings_layout(lindex=lang_index)
	elif pathname == '/articles':
		return SPPDSIM.articles_layout(lindex=lang_index)
	elif isinstance(pathname, str) and '/articles/' in pathname:
		article_id=pathname.strip('/articles/')
		match = re.match('^[0-9]+$', article_id, re.I)
		if match == None:
			return SPPDSIM.articles_layout(lindex=lang_index)
		return SPPDSIM.articles_layout(article_id,lindex=lang_index)
	elif pathname == '/teamwars':
		return SPPDSIM.teamwars_layout(lindex=lang_index)
	elif isinstance(pathname, str) and '/teamwars/' in pathname:
		eventid=pathname.strip('/teamwars/')
		match = re.match('^[0-9]+$', eventid, re.I)
		if match == None:
			return SPPDSIM.teamwars_layout(lindex=lang_index)
		return SPPDSIM.teamwars_layout(eventid,lindex=lang_index)
	elif pathname == '/twmeta':
		return SPPDSIM.twmeta_layout(lindex=lang_index)
	elif isinstance(pathname, str) and '/twmeta/' in pathname:
		eventid=pathname.strip('/twmeta/')
		match = re.match('^[0-9]+$', eventid, re.I)
		if match == None:
			return SPPDSIM.twmeta_layout(lindex=lang_index)
		return SPPDSIM.twmeta_layout(eventid,lindex=lang_index)
	elif pathname == '/teams':
		return SPPDSIM.teams_layout(lindex=lang_index)
	elif isinstance(pathname, str) and '/teams/' in pathname:
		team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', team_id, re.I)
		if match == None:
			return SPPDSIM.teams_layout(lindex=lang_index)
		return SPPDSIM.teams_layout(team_id,full_search,lindex=lang_index)
	elif pathname == '/player':
		return SPPDSIM.player_layout(lindex=lang_index)
	elif isinstance(pathname, str) and '/player/' in pathname:
		player_id=pathname.strip('/player/')
		match = re.match('^[0-9]+$', player_id, re.I)
		if match == None:
			return SPPDSIM.player_layout(lindex=lang_index)
		return SPPDSIM.player_layout(player_id,lindex=lang_index)
	elif pathname == '/mycards':
		return SPPDSIM.collections_layout(lindex=lang_index)
	elif pathname == '/brackets':
		return SPPDSIM.brackets_layout(lindex=lang_index)
	elif isinstance(pathname, str) and '/brackets/' in pathname:
		bracket_id=pathname.strip('/brackets/')
		match = re.match('^[0-9]+$', bracket_id, re.I)
		if match == None:
			return SPPDSIM.brackets_layout(lindex=lang_index)
		email = None
		if g.user != None:
			email = g.user.profile.email
		return SPPDSIM.brackets_layout(gmtOffset,bracket_id,email,lindex=lang_index)
	elif pathname == '/events':
		return SPPDSIM.events_layout(gmtOffset,lindex=lang_index)
	elif isinstance(pathname, str) and '/events/' in pathname:
		event_id=pathname.strip('/events/')
		match = re.match('^[0-9]+$', event_id, re.I)
		if match == None:
			return SPPDSIM.events_layout(gmtOffset,lindex=lang_index)
		return SPPDSIM.events_layout(gmtOffset,event_id,lindex=lang_index)
	elif pathname == '/mymatches':
		return SPPDSIM.mymatches_layout(gmtOffset,lindex=lang_index)
	elif pathname == '/match':
		return SPPDSIM.match_layout(gmtOffset,lindex=lang_index)
	elif isinstance(pathname, str) and '/match/' in pathname:
		match_id=pathname.strip('/match/')
		match = re.match('^[0-9]+$', match_id, re.I)
		if match == None:
			return SPPDSIM.match_layout(gmtOffset,lindex=lang_index)
		return SPPDSIM.match_layout(gmtOffset,match_id,lindex=lang_index)
	elif pathname == '/challenge':
		return SPPDSIM.challenge_layout(gmtOffset,lindex=lang_index)
	elif isinstance(pathname, str) and '/challenge/' in pathname:
		chal_id=pathname.strip('/challenge/')
		chal = re.match('^[0-9]+$', chal_id, re.I)
		if chal == None:
			return SPPDSIM.challenge_layout(gmtOffset,lindex=lang_index)
		return SPPDSIM.challenge_layout(gmtOffset,chal_id,lindex=lang_index)
	elif pathname == '/build':
		return SPPDSIM.card_builder_layout(lindex=lang_index)
	elif pathname == '/about':
		return SPPDSIM.about_page(lang_index)
	elif pathname == '/teammanagercloud':
		return SPPDSIM.teammanagercloud_page(lang_index)
	elif pathname == '/calc':
		return SPPDSIM.calc_page(lang_index)
	elif pathname == '/.shutdown':
		return SPPDSIM.shutdown()
	return SPPDSIM.home_page(lang_index)
	# You could also return a 404 "URL not found" page here

app.clientside_callback(
    """
    function(fooBar) {
		return new Date().getTimezoneOffset();
    }
    """,
    dash.dependencies.Output('hidden-time-output', 'data'),
    [dash.dependencies.Input('hidden-time-input', 'data')]
)

'''
app.clientside_callback(
    """
    function(fooBar) {
		return navigator.language || navigator.userLanguage;
    }
    """,
    dash.dependencies.Output('hidden-language-output', 'data'),
    [dash.dependencies.Input('hidden-language-input', 'data')]
)
'''

@app.callback(dash.dependencies.Output('my-settings-data', 'children'),
			  [dash.dependencies.Input('settings-add-button', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-0', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-1', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-2', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-3', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-4', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-5', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-6', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-7', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-8', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-9', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-0', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-1', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-2', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-3', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-4', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-5', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-6', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-7', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-8', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-9', 'n_clicks_timestamp')
			  ])
def update_my_data(n_clicks,
	p_clicks0,p_clicks1,p_clicks2,p_clicks3,p_clicks4,p_clicks5,p_clicks6,p_clicks7,p_clicks8,p_clicks9,
	d_clicks0,d_clicks1,d_clicks2,d_clicks3,d_clicks4,d_clicks5,d_clicks6,d_clicks7,d_clicks8,d_clicks9):
	myProfile="/player"
	myTeam="/teams"
	if g.user != None:
		time.sleep(2)
		user_id=HELPER_DB.getUserIDFromOktaID(g.user.id)
		if user_id != None:
			team=HELPER_DB.getTeamFromUserID(user_id)
			unique_user_id=HELPER_DB.getUniqueUserIDfromInGameUserID(user_id)
			if team != None:
				myTeam=f"/teams/{team}"
			if unique_user_id != None:
				myProfile=f"/player/{unique_user_id}"
	return [
		dcc.Link('My Profile', href=myProfile, className="w3-bar-item w3-button"),
		dcc.Link('My Team', href=myTeam, className="w3-bar-item w3-button"),
		html.A('My Cards', href='/mycards', className="w3-bar-item w3-button"),
		html.A('My Matches', href='/mymatches', className="w3-bar-item w3-button"),
	]

@app.callback(dash.dependencies.Output('tmc-response-data', 'data'),
			  [dash.dependencies.Input('tmc-response', 'children')])
def update_tmc_response_data(tmc_response_children):
	return int(time.time())

@app.callback([dash.dependencies.Output('tmc-in-progress', 'children'),
			  dash.dependencies.Output('tmc-add-button', 'disabled')],
			  [dash.dependencies.Input('tmc-add-button', 'n_clicks_timestamp'),
			  dash.dependencies.Input('tmc-response-data', 'data'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def tmc_inprogress_status(add_clicks,tmc_response_data,lang_index=0):
	long_string = HELPER.tr("Waiting...",lang_index)
	disabled = False
	if add_clicks != None and tmc_response_data != int(time.time()):
		long_string = HELPER.tr("In Progress...",lang_index)
		disabled = True
	return [html.H3(long_string)], disabled
	
@app.callback(dash.dependencies.Output('tmc-response', 'children'),
			  [dash.dependencies.Input('tmc-add-button', 'n_clicks_timestamp'),
			  dash.dependencies.Input('hidden-language-output', 'data')],
			  state=[dash.dependencies.State('tmc-em', 'value'),
			  dash.dependencies.State('tmc-pw', 'value')])
def setup_team_manager_cloud(add_clicks,lang_index,tmc_email,tmc_pw):
	long_string = ""
	if add_clicks != None:
		success, long_string = HELPER_SSH.setupTeamManager(tmc_email,tmc_pw)
		status_string = ""
		if success:
			status_string += HELPER.tr("SUCCESS!",lang_index) + "\n"
		else:
			status_string += HELPER.tr("FAILED!",lang_index) + "\n"
		long_string = status_string + long_string
	return [dcc.Markdown(long_string)]


@app.callback(dash.dependencies.Output('calc-response', 'children'),
			  [dash.dependencies.Input('calc-dropdown-rarity', 'value'),
			  dash.dependencies.Input('calc-dropdown-from', 'value'),
			  dash.dependencies.Input('calc-dropdown-to', 'value')])
def calc_response(rarity, from_level, to_level):
	total_coins = 0
	total_bronze = 0
	total_silver = 0
	total_gold = 0
	total_copies = 0
	total_exp = 0
	if rarity not in DATABASE.UPGRADE_COSTS: return "Unknown Rarity..."
	if from_level == to_level: return "Select a valid range"
	
	level_found=False
	for cur_level in DATABASE.UPGRADE_COSTS[rarity]:
		if not level_found:
			#If the range is in the wrong direction, it costs nothing.
			if cur_level == to_level:
				break
			if cur_level == from_level:
				level_found = True
			continue
		coins, bronze, silver, gold, copies, experience = DATABASE.UPGRADE_COSTS[rarity][cur_level]
		total_coins+=coins
		total_bronze+=bronze
		total_silver+=silver
		total_gold+=gold
		total_copies+=copies
		total_exp+=experience
		if cur_level == to_level:
			break
	
	return [dcc.Markdown(f'''\n\n
		Coins:\t{total_coins}\n
		Bronze:\t{total_bronze}\n
		Silver:\t{total_silver}\n
		Gold:\t{total_gold}\n
		Copies:\t{total_copies}\n
		Exp:\t{total_exp}\n
	''')]

@app.callback(dash.dependencies.Output('settings-accounts', 'children'),
			  [dash.dependencies.Input('settings-add-button', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-0', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-1', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-2', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-3', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-4', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-5', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-6', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-7', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-8', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-primary-button-9', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-0', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-1', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-2', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-3', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-4', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-5', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-6', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-7', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-8', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-delete-button-9', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-0', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-1', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-2', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-3', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-4', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-5', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-6', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-7', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-8', 'n_clicks_timestamp'),
			  dash.dependencies.Input('settings-optout-button-9', 'n_clicks_timestamp')
			  ],
			  state=[dash.dependencies.State('input-tracking-id', 'value')]
			  )
def settings_buttons(n_clicks,
	p_clicks0,p_clicks1,p_clicks2,p_clicks3,p_clicks4,p_clicks5,p_clicks6,p_clicks7,p_clicks8,p_clicks9,
	d_clicks0,d_clicks1,d_clicks2,d_clicks3,d_clicks4,d_clicks5,d_clicks6,d_clicks7,d_clicks8,d_clicks9,
	o_clicks0,o_clicks1,o_clicks2,o_clicks3,o_clicks4,o_clicks5,o_clicks6,o_clicks7,o_clicks8,o_clicks9,
	user_id):
	primary_clicks = [p_clicks0,p_clicks1,p_clicks2,p_clicks3,p_clicks4,p_clicks5,p_clicks6,p_clicks7,p_clicks8,p_clicks9]
	delete_clicks = [d_clicks0,d_clicks1,d_clicks2,d_clicks3,d_clicks4,d_clicks5,d_clicks6,d_clicks7,d_clicks8,d_clicks9]
	opt_clicks = [o_clicks0,o_clicks1,o_clicks2,o_clicks3,o_clicks4,o_clicks5,o_clicks6,o_clicks7,o_clicks8,o_clicks9]
	#Corner case where the user's session times out while on the settings page.
	if g.user == None: return HELPER.listAccounts([], "logged_out")
	#Must match this format exactly!
	click_list=[n_clicks]
	click_list.extend(primary_clicks)
	click_list.extend(delete_clicks)
	click_list.extend(opt_clicks)
	most_recent_clicked_button=1
	response=None
	for click in click_list:
		if click != None and click > 0:
			if click > most_recent_clicked_button:
				most_recent_clicked_button=click
	is_paid_user=HELPER_DB.isPaidUser(g.user)
	users_accounts=HELPER_DB.getAccounts(g.user)
	if user_id != None and n_clicks != None and n_clicks == most_recent_clicked_button:
		if not ((is_paid_user and len(users_accounts) < 10) or \
		 (not is_paid_user and len(users_accounts) < 3)):
			return HELPER.listAccounts(users_accounts, response, is_paid_user)
		lower_user_id=user_id.lower()
		match = re.match('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$', lower_user_id, re.I)
		if match != None and g.user != None:
			#Check if it's already in our database (That's great!)
			name = HELPER_DB.getUserName(lower_user_id)
			if name == None:
				#Check if it's a valid account (That's ok)
				result=SPPD_API.getUserName(lower_user_id)
				user_map=RESTFUL.getUserNames(result)
				if lower_user_id in user_map:
					#then add it to our database
					RESTFUL.uploadUserPlatform(user_map)
					name=user_map[lower_user_id]
				else: name=None
			if name != None:
				response=RESTFUL.uploadAccount(lower_user_id, g.user.id)
		return HELPER.listAccounts(users_accounts, response, is_paid_user)
	index = 0
	for p_click in primary_clicks:
		if p_click != None and p_click == most_recent_clicked_button:
			RESTFUL.setPrimaryAccount(index,g.user.id)
			return HELPER.listAccounts(users_accounts, response, is_paid_user)
		index +=1
	index = 0
	for d_click in delete_clicks:
		if d_click != None and d_click == most_recent_clicked_button:
			RESTFUL.deleteAccount(index,g.user.id)
			return HELPER.listAccounts(users_accounts, response, is_paid_user)
		index +=1
	index = 0
	for o_click in opt_clicks:
		if o_click != None and o_click == most_recent_clicked_button:
			RESTFUL.optoutAccount(index,g.user.id)
			return HELPER.listAccounts(users_accounts, response, is_paid_user)
		index +=1
	return HELPER.listAccounts(users_accounts, response, is_paid_user)
	
def header_button_primary_helper(index,g_user):
	myProfile="/player"
	myTeam="/teams"
	non_primary_accounts=[]
	accounts=HELPER_DB.getAccounts(g_user)
	subindex = 0
	for account in accounts:
		primary=account[1]
		if not primary:
			non_primary_accounts.append(subindex)
		subindex+=1
	if index < len(non_primary_accounts):
		RESTFUL.setPrimaryAccount(non_primary_accounts[index],g.user.id)
		time.sleep(2)
	user_id=HELPER_DB.getUserIDFromOktaID(g.user.id)
	if user_id != None:
		team=HELPER_DB.getTeamFromUserID(user_id)
		unique_user_id=HELPER_DB.getUniqueUserIDfromInGameUserID(user_id)
		if team != None:
			myTeam=f"/teams/{team}"
		if unique_user_id != None:
			myProfile=f"/player/{unique_user_id}"
	return [myTeam,myProfile]
	
@app.callback(dash.dependencies.Output('my-data', 'children'),
			  [dash.dependencies.Input('header-primary-button-1', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-2', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-3', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-4', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-5', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-6', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-7', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-8', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-9', 'n_clicks_timestamp')
			  ])
def header_buttons(p_clicks1,p_clicks2,p_clicks3,p_clicks4,p_clicks5,p_clicks6,p_clicks7,p_clicks8,p_clicks9):
	myProfile="/player"
	myTeam="/teams"
	if g.user == None:
		return [
			dcc.Link('My Profile', href=myProfile, className="w3-bar-item w3-button"),
			dcc.Link('My Team', href=myTeam, className="w3-bar-item w3-button"),
			html.A('My Cards', href='/mycards', className="w3-bar-item w3-button"),
			html.A('My Matches', href='/mymatches', className="w3-bar-item w3-button"),
		]
	primary_clicks = [p_clicks1,p_clicks2,p_clicks3,p_clicks4,p_clicks5,p_clicks6,p_clicks7,p_clicks8,p_clicks9]
	most_recent_clicked_button=1
	for click in primary_clicks:
		if click != None and click > 0 and click > most_recent_clicked_button:
			most_recent_clicked_button=click
	all_null=True
	index = 0
	for p_click in primary_clicks:
		if p_click != None and p_click == most_recent_clicked_button:
			myProfile, myTeam = header_button_primary_helper(index,g.user)
			all_null=False
		index+=1
	if all_null:
		user_id=HELPER_DB.getUserIDFromOktaID(g.user.id)
		if user_id != None:
			team=HELPER_DB.getTeamFromUserID(user_id)
			unique_user_id=HELPER_DB.getUniqueUserIDfromInGameUserID(user_id)
			if team != None:
				myTeam=f"/teams/{team}"
			if unique_user_id != None:
				myProfile=f"/player/{unique_user_id}"
	return [
		dcc.Link('My Profile', href=myProfile, className="w3-bar-item w3-button"),
		dcc.Link('My Team', href=myTeam, className="w3-bar-item w3-button"),
		html.A('My Cards', href='/mycards', className="w3-bar-item w3-button"),
		html.A('My Matches', href='/mymatches', className="w3-bar-item w3-button"),
	]
	
@app.callback([dash.dependencies.Output('deckbuilder1-content', 'children'),
			  dash.dependencies.Output('deckbuilder2-content', 'children')],
			  [dash.dependencies.Input('deckbuilder1-theme-dropdown', 'value'),
			  dash.dependencies.Input('deckbuilder2-theme-dropdown', 'value'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def deckbuilder_sub_content(my_themes,opp_themes,lang_index):
	your_cards_str = HELPER.tr('Your Cards',lang_index)
	blacklist_cards_str = HELPER.tr('Blacklist Cards',lang_index)
	opp_cards_str = HELPER.tr("Opponent's Cards",lang_index)
	my_card_options = []
	opp_card_options = []
	for name,energy,theme,key in sortCollectionWithKey():
		if theme == 0: #neutral
			my_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
			opp_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
			continue
			
		if my_themes == None or len(my_themes) == 0:
			my_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'adv' in my_themes and theme == 1:
			my_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'sci' in my_themes and theme == 2:
			my_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'mys' in my_themes and theme == 3:
			my_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'fan' in my_themes and theme == 4:
			my_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'sup' in my_themes and theme == 5:
			my_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
			
		if opp_themes == None or len(opp_themes) == 0:
			opp_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'adv' in opp_themes and theme == 1:
			opp_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'sci' in opp_themes and theme == 2:
			opp_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'mys' in opp_themes and theme == 3:
			opp_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'fan' in opp_themes and theme == 4:
			opp_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
		elif 'sup' in opp_themes and theme == 5:
			opp_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
			
	my_html_list = []
	my_html_list.append(html.H3(your_cards_str))
	my_html_list.append(
		dcc.Dropdown(
			id = 'deckbuilder1-cards-dropdown',
			options = my_card_options,
			value = [],
			placeholder = HELPER.tr('Select one or more cards',lang_index),
			multi=True,
			className='w3-white'
		)
	)
	my_html_list.append(html.H3(blacklist_cards_str))
	my_html_list.append(
		dcc.Dropdown(
			id = 'deckbuilder1-blacklist-dropdown',
			options = my_card_options,
			value = [],
			placeholder = HELPER.tr('Select one or more cards',lang_index),
			multi=True,
			className='w3-white'
		)
	)
	my_html_list.append(html.Div(id='deckbuilder1-deck-content'))
	opp_html_list = []
	opp_html_list.append(html.H3(opp_cards_str))
	opp_html_list.append(
		dcc.Dropdown(
			id = 'deckbuilder2-cards-dropdown',
			options = opp_card_options,
			value = [],
			placeholder = HELPER.tr('Select one or more cards',lang_index),
			multi=True,
			className='w3-white'
		)
	)
	opp_html_list.append(html.Div(id='deckbuilder2-deck-content'))
	return my_html_list,opp_html_list
	
@app.callback(dash.dependencies.Output('compare-content', 'children'),
			  [dash.dependencies.Input('compare-cards-dropdown', 'value'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def compare_content(my_cards,lang_index):
	#If autocomplete - autocomplete their deck with the best options
	#	If they haven't chosen any cards, go based off of the themes they have selected.
	#	If they haven't chosen any themes, select the best two themes, auto-include neutral.
	#else - only list the cards they have selected.
	my_html_list = []
	width = 100
	if len(my_cards) > 0: width = 100/len(my_cards)
	mycards = sorted(my_cards)
	for card_id in my_cards:
		card_name = HELPER_DB.getCardName(card_id)
		card_image = HELPER.tr(card_name,lang_index)
		if card_name in DATABASE.IMAGE_MAP:
			card_image = html.Img(src=DATABASE.IMAGE_MAP[card_name])
		my_html_list.append(
			html.Div(children=[
				card_image
				],
				style={'display': 'inline-block', 'width': f"{width}%", 'max-height': '300px'})
		)
	global tab_styles,tab_selected_style
	my_html_list.append(dcc.Tabs(
		id="compare-tabs",
		value='simple',
		children=[
			dcc.Tab(label='Simple', value='simple', style=tab_style, selected_style=tab_selected_style),
			dcc.Tab(label='Detailed', value='detailed', style=tab_style, selected_style=tab_selected_style),
		],persistence=True,
		style=tab_styles)
	)
	my_html_list.append(html.Div(id='compare-tabs-content'))
	return my_html_list
	
@app.callback(dash.dependencies.Output('compare-tabs-content', 'children'),
              [dash.dependencies.Input('compare-tabs', 'value'),
			  dash.dependencies.Input('compare-cards-dropdown', 'value'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def compare_tabs_content(tab, my_cards, lang_index):
	if tab == 'simple':
		return generate_carddetails_multiple_table(my_cards,lang_index)
	elif tab == 'detailed':
		return generate_cardfulldetails_multiple_table(my_cards,lang_index)
	else:
		return "This Page Does Not Exist."
	
@app.callback([dash.dependencies.Output('deckbuilder1-deck-content', 'children'),
			  dash.dependencies.Output('deckbuilder2-deck-content', 'children')],
			  [dash.dependencies.Input('deckbuilder-autocomplete', 'value'),
			  dash.dependencies.Input('deckbuilder1-theme-dropdown', 'value'),
			  dash.dependencies.Input('deckbuilder2-theme-dropdown', 'value'),
			  dash.dependencies.Input('deckbuilder1-cards-dropdown', 'value'),
			  dash.dependencies.Input('deckbuilder2-cards-dropdown', 'value'),
			  dash.dependencies.Input('deckbuilder1-blacklist-dropdown', 'value'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def deckbuilder_subsub_content(autocomplete,my_themes,opp_themes,my_cards,opp_cards,my_blacklist,lindex):
	#If autocomplete - autocomplete their deck with the best options
	#	If they haven't chosen any cards, go based off of the themes they have selected.
	#	If they haven't chosen any themes, select the best two themes, auto-include neutral.
	#else - only list the cards they have selected.
	my_html_list = []
	opp_html_list = []
	if autocomplete != None and True in autocomplete:
		#check your theme(s)
		#check opp theme(s)
		#check your card(s)
		#check opp card(s)
		#if they haven't selected anything... Pick the best deck based on the best themes
		tmp_mythemes = []
		tmp_mycards = []
		tmp_oppthemes = []
		tmp_oppcards = []
		tmp_blacklist = []
		if my_themes != None: tmp_mythemes = my_themes
		if my_cards != None: tmp_mycards = my_cards
		if opp_themes != None: tmp_oppthemes = opp_themes
		if opp_cards != None: tmp_oppcards = opp_cards
		if my_blacklist != None: tmp_blacklist = my_blacklist
		best_deck = HELPER_DB.getBestDeck(tmp_mythemes,tmp_mycards,tmp_oppthemes,tmp_oppcards,tmp_blacklist)
		
		#Display My Deck
		CARD_NAMES1=[]
		CARD_NAMES2=[]
		index = 0
		for card_id in best_deck:
			card_name = HELPER_DB.getCardName(card_id)
			if index % 2 == 0:
				CARD_NAMES1.append(card_name)
			else:
				CARD_NAMES2.append(card_name)
			index+=1
		my_html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(f"{HELPER.tr(x,lindex)}", style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES1)],
				#style={'display': 'inline-block'}
			)
		]))
		my_html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES1)],
				style={'display': 'inline-block'}
			)
		]))
		my_html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(f"{HELPER.tr(x,lindex)}", style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES2)],
				#style={'display': 'inline-block'}
			)
		]))
		my_html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES2)],
				style={'display': 'inline-block'}
			)
		]))
		
		#Display opponent's deck
		if opp_cards == None: opp_cards = []
		while len(opp_cards) < 12: opp_cards.append(0)
		CARD_NAMES1=[]
		CARD_NAMES2=[]
		index = 0
		for card_id in opp_cards:
			card_name = HELPER_DB.getCardName(card_id)
			if index % 2 == 0:
				CARD_NAMES1.append(card_name)
			else:
				CARD_NAMES2.append(card_name)
			index+=1
		opp_html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(f"{HELPER.tr(x,lindex)}", style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES1)],
				#style={'display': 'inline-block'}
			)
		]))
		opp_html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES1)],
				style={'display': 'inline-block'}
			)
		]))
		opp_html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(f"{HELPER.tr(x,lindex)}", style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES2)],
				#style={'display': 'inline-block'}
			)
		]))
		opp_html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES2)],
				style={'display': 'inline-block'}
			)
		]))
		return my_html_list,opp_html_list
	if my_cards == None: my_cards = []
	if opp_cards == None: opp_cards = []
	while len(my_cards) < 12: my_cards.append(0)
	while len(opp_cards) < 12: opp_cards.append(0)
	for player in [0,1]: #Me, Opp
		CARD_NAMES1=[]
		CARD_NAMES2=[]
		index = 0
		deck = my_cards if player == 0 else opp_cards
		for card_id in deck:
			card_name = HELPER_DB.getCardName(card_id)
			if index % 2 == 0:
				CARD_NAMES1.append(card_name)
			else:
				CARD_NAMES2.append(card_name)
			index+=1
		html_list = []
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(f"{HELPER.tr(x,lindex)}", style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES1)],
				#style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES1)],
				style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(f"{HELPER.tr(x,lindex)}", style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES2)],
				#style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES2)],
				style={'display': 'inline-block'}
			)
		]))
		if player == 0: my_html_list = html_list
		else: opp_html_list = html_list
	return my_html_list,opp_html_list
	
@app.callback(dash.dependencies.Output('users-list', 'children'),
			  [dash.dependencies.Input('header-primary-button-1', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-2', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-3', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-4', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-5', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-6', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-7', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-8', 'n_clicks_timestamp'),
			  dash.dependencies.Input('header-primary-button-9', 'n_clicks_timestamp')
			  ])
def header_buttons_user_list(p_clicks1,p_clicks2,p_clicks3,p_clicks4,p_clicks5,p_clicks6,p_clicks7,p_clicks8,p_clicks9):
	login_children=[]
	if g.user == None:
		login_children = [
			#dcc.Link('Login', href='/login'),
			#DCC doesn't actually refresh the page!
			html.A(html.Span(' Login',
					className="glyphicon glyphicon-log-in"
				),
				href='/login'
			)
		]
	else:
		time.sleep(3)
		accounts_list = HELPER.getAccountsPrimaryOnTop(g.user)
		name = accounts_list[0]
		need_link = name == "Link SPPD Account"
		if need_link:
			login_children = [
				dcc.Link(name, href='/settings', className="w3-button"),
				html.Div(children=[
					dcc.Link(html.Span('Settings',
						className="glyphicon glyphicon-cog"
						), href='/settings', className="w3-bar-item w3-button"
					),
					html.A(html.Span('Logout',
						className="glyphicon glyphicon-log-out"
						), href='/logout', className="w3-bar-item w3-button"
					)],
					className="w3-dropdown-content w3-bar-block w3-card-4"
				)
			]
		else:
			non_primary_accounts=[html.Button(accounts_list[index],
						className="w3-button",
						id=f'header-primary-button-{index}'
					) for index in range(1,len(accounts_list[1:])+1)]
			invisible_accounts=[html.Button("",
						className="w3-button",
						id=f'header-primary-button-{index}',
						style={'display': 'none'}
					) for index in range(len(accounts_list),10)]
			login_children = [
				html.Button(html.Span(' ' + name,
					className="glyphicon glyphicon-user"
					), className="w3-button"
				),
				html.Div(children=[
					*non_primary_accounts,
					*invisible_accounts,
					dcc.Link(html.Span('Settings',
						className="glyphicon glyphicon-cog"
						), href='/settings', className="w3-bar-item w3-button"
					),
					html.A(html.Span('Logout',
						className="glyphicon glyphicon-log-out"
						), href='/logout', className="w3-bar-item w3-button"
					)],
					className="w3-dropdown-content w3-bar-block w3-card-4"
				)
			]
	return login_children
	
@app.callback(dash.dependencies.Output('hidden-language-output', 'data'),
			  [dash.dependencies.Input('language-button-0', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-1', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-2', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-3', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-4', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-5', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-6', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-7', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-8', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-9', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-10', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-11', 'n_clicks_timestamp'),
			  dash.dependencies.Input('language-button-12', 'n_clicks_timestamp')],
			  [dash.dependencies.State('hidden-language-output', 'data')])
def buttons_language_list(p_clicks1,p_clicks2,p_clicks3,p_clicks4,p_clicks5,p_clicks6,
	p_clicks7,p_clicks8,p_clicks9,p_clicks10,p_clicks11,p_clicks12,p_clicks13,current):
	primary_clicks = [p_clicks1,p_clicks2,p_clicks3,p_clicks4,p_clicks5,p_clicks6,
		p_clicks7,p_clicks8,p_clicks9,p_clicks10,p_clicks11,p_clicks12,p_clicks13]
	most_recent_clicked_button=1
	for click in primary_clicks:
		if click != None and click > 0 and click > most_recent_clicked_button:
			most_recent_clicked_button=click
	index = 0
	for p_click in primary_clicks:
		if p_click != None and p_click == most_recent_clicked_button:
			return index
		index+=1
	return current

@app.callback(dash.dependencies.Output('mycards-content', 'children'),
			  [dash.dependencies.Input('collections-dropdown-theme', 'value'),
			  dash.dependencies.Input('collections-dropdown-type', 'value'),
			  dash.dependencies.Input('collections-dropdown-cost', 'value'),
			  dash.dependencies.Input('collections-dropdown-rarity', 'value'),
			  dash.dependencies.Input('collections-dropdown-keyword', 'value')])
def collections_dropdown(theme,type,cost,rarity,keyword):
	if g.user == None or HELPER_DB.getUserIDFromOktaID(g.user.id) == None:
		return html.H1("You must be registered with a linked SPPD Account to view this page.")
	html_list=[]
	index=0
	for elem in generate_collections_table():
		html_list.append(
			html.Div(
				id=f'las-table-{index}',
				children=elem,
			)
		)
		#Needed so the tables don't overlap
		html_list.append(html.Br())
		html_list.append(html.Br())
		index+=1
	html_list.append(html.H1('Bulk Insert'))
	html_list.append(html.H3('Will overwrite the levels for cards listed, Refresh the page after ~10 seconds.'))
	html_list.append(dcc.Input(id="bulk-card-input", type="text", placeholder="Dogpoo:4.40,Gizmo Ike:2,...", value='',style={
		'text-transform': 'lowercase',
		'font-variant': 'all-small-caps',
		'color': 'black'
	}))
	html_list.append(html.Button('Add',
				className="w3-button",
				id='collections-add-button'
		)
	)
	return html_list
	
@app.callback(dash.dependencies.Output('mymatches-content', 'children'),
			  [dash.dependencies.Input('collections-dropdown-theme', 'value'),
			  dash.dependencies.Input('collections-dropdown-type', 'value'),
			  dash.dependencies.Input('collections-dropdown-cost', 'value'),
			  dash.dependencies.Input('collections-dropdown-rarity', 'value'),
			  dash.dependencies.Input('collections-dropdown-keyword', 'value'),
			  dash.dependencies.Input('hidden-time-output','data')])
def mymatches_dropdown(theme,type,cost,rarity,keyword,gmtOffset=480):
	if g.user == None or HELPER_DB.getUserIDFromOktaID(g.user.id) == None:
		return html.H1("You must be registered with a linked SPPD Account to view this page.")
	return generate_mymatches_table(g.user,gmtOffset)
	
@app.callback(dash.dependencies.Output('specific-player-tabs-content', 'children'),
              [dash.dependencies.Input('specific-player-tabs', 'value'),
			  dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('hidden-time-output','data')])
def specific_player_tabs_content(tab, pathname, gmtOffset):
	unique_user_id="1000000"
	if isinstance(pathname, str) and '/player/' in pathname:
		tmp_user_id=pathname.strip('/player/')
		match = re.match('^[0-9]+$', tmp_user_id, re.I)
		if match != None:
			unique_user_id=tmp_user_id
	if not HELPER_DB.isValidUserID(unique_user_id):
		return html.H1("Oops, this page doesn't exist.")
	if tab == 'collection':
		return generate_players_collection_and_deck(g.user,unique_user_id)
	elif tab == 'matches':
		return [dcc.Link("Quick Link", href=f"{pathname}?t1=matches"),
			generate_specific_players_matches(unique_user_id, gmtOffset)]
	else:
		return "This Page Does Not Exist."

@app.callback(dash.dependencies.Output('specific-player-content', 'children'),
			  [dash.dependencies.Input('url', 'search')])
def sub_player_dropdown(search):
	global tab_styles,tab_style,tab_selected_style
	full_search = {}
	if search != None and "?" in search:
		tmp_search = search.strip("?")
		if "&" in tmp_search:
			n_search = tmp_search.split("&")
			for elem in n_search:
				eq_search = elem.split("=")
				if len(eq_search) == 2:
					full_search[eq_search[0]]=eq_search[1]
		else:
			eq_search = tmp_search.split("=")
			if len(eq_search) == 2:
				full_search[eq_search[0]]=eq_search[1]
	target='collection'
	if 't1' in full_search: target=full_search['t1']
	return [dcc.Tabs(
		id="specific-player-tabs",
		value=target,
		children=[
			dcc.Tab(label='Collection', value='collection', style=tab_style, selected_style=tab_selected_style),
			dcc.Tab(label='Matches', value='matches', style=tab_style, selected_style=tab_selected_style),
		],persistence=True,
		style=tab_styles),
		html.Div(id='specific-player-tabs-content')
	]

@app.callback(dash.dependencies.Output('player-content', 'children'),
			  [dash.dependencies.Input('players-dropdown-rank', 'value'),
			  dash.dependencies.Input('players-dropdown-sort', 'value'),
			  dash.dependencies.Input('players-dropdown-search-button', 'n_clicks_timestamp'),
			  dash.dependencies.Input('hidden-time-output','data'),
			  dash.dependencies.Input('hidden-language-output', 'data')],
			  state=[dash.dependencies.State('players-dropdown-name', 'value')])
def player_dropdown(rank, sort, n_clicks, gmtOffset, lang_index, name):
	tmp_name=None
	if name != None and n_clicks != None and n_clicks > 0 and len(name)>4:
		if type(name) == str: tmp_name = name.lower()
		else: tmp_name = name
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_players_table(rank, sort, tmp_name, gmtOffset, lang_index),
		)]
	)

@app.callback(dash.dependencies.Output('builder-session', 'data'),
			  [dash.dependencies.Input('builder-upload', 'contents')])
def builder_upload(contents):
	return contents
	
def getFontSizeOffset(txt_string, xoffset, yoffset, maxfontsize=24, lang_index=0):
	font_path = '/Users/Remin/Documents/GitHub/sppd-data/card_bases/south_park.ttf'
	font = ImageFont.truetype(font_path, maxfontsize)
	font_length = font.getsize(txt_string)
	while (font_length[0] > xoffset or font_length[1] > yoffset) and maxfontsize > 2:
		# iterate until the text size is just larger than the criteria
		maxfontsize -= 1
		font = ImageFont.truetype(font_path, maxfontsize)	
		font_length = font.getsize(txt_string)
	
	x = (font_length[0] + (xoffset - font_length[0]))/2 - font_length[0]/2
	y = (font_length[1] + (yoffset - font_length[1]))/2 - font_length[1]/2
	offset = x,y #X,Y coordinates
	return font, offset
		
@app.callback(dash.dependencies.Output('builder-apply-button', 'disabled'),
			  [dash.dependencies.Input('builder-apply-button', 'n_clicks_timestamp'),
			  dash.dependencies.Input('builder-interval', 'n_intervals')])
def builder_disable(n_clicks, n_intervals):
	if n_clicks == None: return False
	return (n_clicks/1000) > (int(time.time()) - 30)
	
@app.callback(dash.dependencies.Output('builder-content', 'children'),
			  [dash.dependencies.Input('builder-theme', 'value'),
			  dash.dependencies.Input('builder-rarity', 'value'),
			  dash.dependencies.Input('builder-type', 'value'),
			  dash.dependencies.Input('builder-level', 'value'),
			  dash.dependencies.Input('builder-cost', 'value'),
			  dash.dependencies.Input('builder-health', 'value'),
			  dash.dependencies.Input('builder-attack', 'value'),
			  dash.dependencies.Input('builder-session', 'data'),
			  dash.dependencies.Input('builder-apply-button', 'n_clicks_timestamp')
			  ],
			  state=[dash.dependencies.State('builder-name', 'value'),
			  dash.dependencies.State('builder-desc', 'value')])

def builder_dropdown(theme, rarity, card_type, level, cost, health, attack, card_art, n_clicks, name, description, lang_index=0):
	if n_clicks == None: return ""
	#Stich the image together
	c_image = None
	#0. Pick the card base
	theme_lower = theme.lower().replace('-','')
	rarity_lower = rarity.lower()
	type_lower = card_type.lower()
	pixelMap = Image.open(f'/Users/Remin/Documents/GitHub/sppd-data/card_bases/{theme}/{theme_lower}_{rarity_lower}_{type_lower}.png')
	W,H = pixelMap.size
	#1. Start with the card art (lowest layer)
	if card_art != None:
		try:
			index = card_art.find("base64,")+7
			card_art = card_art[index:]
			image = BytesIO(base64.b64decode(card_art))
			c_image = Image.open(image)
			w2,h2,w2offset,h2offset=66,151,578,806
			if c_image.mode != "RGBA": c_image = c_image.convert('RGBA')
			x,y = c_image.size
			multiplier = 1
			if float(w2offset)/x > float(h2offset)/y: #X is the smaller ratio
				multiplier = float(w2offset)/x
			else: #Y is the smaller ratio
				multiplier = float(h2offset)/y
			c_image = c_image.resize((round(c_image.size[0]*multiplier+1), round(c_image.size[1]*multiplier+1)))
			#Center the cardart
			x,y = 0,0
			if c_image.size[0] > w2offset+10:
				x = c_image.size[0]/2 - w2offset/2
			elif c_image.size[1] > h2offset+10:
				y = c_image.size[1]/2 - h2offset/2
			c_image = c_image.crop(box=(x,y,w2offset+x,h2offset+y))
			full_res = Image.new(pixelMap.mode, pixelMap.size)
			full_res.paste(c_image,box=(w2,h2))
			c_image = full_res
		except:
			return "Invalid Image. Please try a different file."
			
	#2. Then pick the overlay based on Theme/Rarity/Type
	core_image = None
	lowerbound=160
	weight = 0.80 # percent
	if c_image == None:
		core_image = pixelMap
	else:
		#c_image = Image.new(pixelMap.mode, pixelMap.size)
		pixelsNew = c_image.load()
		for i in range(c_image.size[0]):
			for j in range(c_image.size[1]):
				r,g,b,a = pixelMap.getpixel((i,j))
				if a == 0 or a == 255:
					pixelsNew[i,j] = (0,0,0,0)
		#core_image = c_image
		core_image = Image.alpha_composite(c_image, pixelMap)
	#3. Then add the attributes Level/Cost/Health/Attack/Name
	draw_text_list = [] # [ [xoffset,yoffset,string,font,border], ... ]
	#NAME
	x,y,xoffset,yoffset = DATABASE.CARD_BUILDER["NAME"]
	font,offset = getFontSizeOffset(name,xoffset*2,yoffset*2,35,lang_index=lang_index)
	draw_text_list.append([x-xoffset+offset[0],y-yoffset+offset[1],name,font,2])
	#LEVEL
	x,y,xoffset,yoffset = DATABASE.CARD_BUILDER["LEVEL"]
	if type(level) == str and 'L' not in level: level = f"LVL {level}"
	elif type(level) == int: level = f"LVL {level}"
	font,offset = getFontSizeOffset(level,xoffset*2,yoffset*2,22)
	draw_text_list.append([x-xoffset+offset[0],y-yoffset+offset[1],level,font,1])
	if card_type not in ["Spell", "Trap"]:
		if health != "":
			#HEALTH
			x,y,xoffset,yoffset = DATABASE.CARD_BUILDER["HEALTH"]
			font,offset = getFontSizeOffset(health,xoffset*2,yoffset*2,39)
			draw_text_list.append([x-xoffset+offset[0],y-yoffset+offset[1],health,font,2])
		if attack != "":
			#ATTACK
			x,y,xoffset,yoffset = DATABASE.CARD_BUILDER["ATTACK"]
			font,offset = getFontSizeOffset(attack,xoffset*2,yoffset*2,39)
			draw_text_list.append([x-xoffset+offset[0],y-yoffset+offset[1],attack,font,2])
	#COST
	x,y,xoffset,yoffset = DATABASE.CARD_BUILDER["COST"]
	font,offset = getFontSizeOffset(str(cost),xoffset*2,yoffset*2,90)
	draw_text_list.append([x-xoffset+offset[0],y-yoffset+offset[1],str(cost),font,6])
	
	#DESCRIPTION
	x,y,xoffset,yoffset = DATABASE.CARD_BUILDER["DESC"]
	pad=28
	para = textwrap.wrap(description, width=30)
	para_len = len(para)
	text_yoffset=y-pad/2
	if para_len % 2 == 0:
		text_yoffset = text_yoffset - pad/2
		text_yoffset += 7 # To adjust for pad height on even lines.
		para_len -= 1
	text_yoffset = text_yoffset - pad * (para_len-1) / 2
	current_h = text_yoffset
	for line in para:
		font,offset = getFontSizeOffset(line,xoffset*2,yoffset*2,24,lang_index=lang_index)
		draw_text_list.append([x-xoffset+offset[0],current_h,line,font,1])
		current_h += pad
	outline="black"
	draw = ImageDraw.Draw(core_image)
	for x,y,string,font,border in draw_text_list:
		for i in range(1,border+1):
			if i == 1 or i < border/2:
				draw.text((x, y-i), string, font=font, fill=outline)
				draw.text((x-i, y), string, font=font, fill=outline)
				draw.text((x+i, y), string, font=font, fill=outline)
			draw.text((x, y+i), string, font=font, fill=outline)
		draw.text((x,y), string, font=font, fill = 'rgb(230,226,197)')
	
	tmp_file = BytesIO()
	core_image.save(tmp_file,"PNG")
	encoded_image = base64.b64encode(tmp_file.getvalue())
	return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode('utf-8')))

@app.callback(dash.dependencies.Output('cards-content', 'children'),
			  [dash.dependencies.Input('cards-dropdown-rank', 'value'),
			  dash.dependencies.Input('cards-dropdown-mode', 'value'),
			  dash.dependencies.Input('cards-dropdown-time', 'value'),
			  dash.dependencies.Input('cards-dropdown-theme', 'value'),
			  dash.dependencies.Input('cards-dropdown-type', 'value'),
			  dash.dependencies.Input('cards-dropdown-cost', 'value'),
			  dash.dependencies.Input('cards-dropdown-rarity', 'value'),
			  dash.dependencies.Input('cards-dropdown-keyword', 'value'),
			  dash.dependencies.Input('hidden-time-output','data'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def cards_dropdown(rank,mode,search,theme,type,cost,rarity,keyword,gmtOffset,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_cards_table(rank,mode,search,theme,type,cost,rarity,keyword,gmtOffset,lang_index),
		)]
	)

@app.callback(dash.dependencies.Output('allcards-content', 'children'),
			  [dash.dependencies.Input('allcards-dropdown-theme', 'value'),
			  dash.dependencies.Input('allcards-dropdown-type', 'value'),
			  dash.dependencies.Input('allcards-dropdown-cost', 'value'),
			  dash.dependencies.Input('allcards-dropdown-rarity', 'value'),
			  dash.dependencies.Input('allcards-dropdown-keyword', 'value'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def cards_dropdown(theme,type,cost,rarity,keyword,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_allcards_table(theme,type,cost,rarity,keyword,lang_index),
		)]
	)

@app.callback(dash.dependencies.Output('cardstats-content', 'children'),
			  [dash.dependencies.Input('cardstats-dropdown-theme', 'value'),
			  dash.dependencies.Input('cardstats-dropdown-type', 'value'),
			  dash.dependencies.Input('cardstats-dropdown-cost', 'value'),
			  dash.dependencies.Input('cardstats-dropdown-rarity', 'value'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def cardstats_dropdown(theme,type,cost,rarity,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_cardstats_table(theme,type,cost,rarity,lang_index)
		)]
	)

@app.callback(dash.dependencies.Output('deckbuilder-content', 'children'),
			  [dash.dependencies.Input('deckbuilder-dropdown-theme', 'value'),
			  dash.dependencies.Input('deckbuilder-dropdown-type', 'value'),
			  dash.dependencies.Input('deckbuilder-dropdown-cost', 'value'),
			  dash.dependencies.Input('deckbuilder-dropdown-rarity', 'value'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def deckbuilder_dropdown(theme,type,cost,rarity,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_deckbuilder_table(theme,type,cost,rarity,lang_index)
		)]
	)

@app.callback(dash.dependencies.Output('teams-content', 'children'),
			  [dash.dependencies.Input('teams-dropdown-rank', 'value'),
			  dash.dependencies.Input('teams-dropdown-members', 'value'),
			  dash.dependencies.Input('teams-dropdown-nklevel', 'value'),
			  dash.dependencies.Input('teams-dropdown-status', 'value'),
			  dash.dependencies.Input('hidden-language-output', 'data')
			  ])
def teams_dropdown(rank,members,nklevel,status,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_teams_table(rank,members,nklevel,status,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('match-content', 'children'),
			  [dash.dependencies.Input('match-dropdown-rank', 'value'),
			  dash.dependencies.Input('match-dropdown-mode', 'value'),
			  dash.dependencies.Input('hidden-time-output', 'data'),
			  dash.dependencies.Input('hidden-language-output', 'data')
			  ])
def matches_dropdown(rank,mode,gmtOffset,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_match_table(gmtOffset,rank,mode,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('challenge-content', 'children'),
			  [dash.dependencies.Input('challenge-dropdown-rank', 'value'),
			  dash.dependencies.Input('hidden-time-output', 'data'),
			  dash.dependencies.Input('hidden-language-output', 'data')
			  ])
def challenge_dropdown(rank,gmtOffset,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_challenge_table(gmtOffset,rank,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('teamwars-content', 'children'),
			  [dash.dependencies.Input('teamwars-dropdown-league', 'value'),
			  dash.dependencies.Input('hidden-time-output', 'data'),
			  dash.dependencies.Input('hidden-language-output', 'data')
			  ])
def teamwars_dropdown(league,gmtOffset,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_teamwars_table(gmtOffset,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('twmeta-content', 'children'),
			  [dash.dependencies.Input('twmeta-dropdown-league', 'value'),
			  dash.dependencies.Input('hidden-time-output', 'data'),
			  dash.dependencies.Input('hidden-language-output', 'data')
			  ])
def twmeta_dropdown(league,gmtOffset,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_twmeta_table(gmtOffset,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('specific-teamwars-content', 'children'),
			  [dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('specific-meta-tw-tabs', 'value'),
			  dash.dependencies.Input('hidden-time-output', 'data'),
			  dash.dependencies.Input('hidden-language-output', 'data')
			  ])
def specific_teamwars_dropdown(pathname,league,gmtOffset,lang_index):
	eventid="10000"
	if isinstance(pathname, str) and '/teamwars/' in pathname:
		eventid=pathname.strip('/teamwars/')		
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_specific_teamwars_table(eventid,league,gmtOffset,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('specific-twmeta-content', 'children'),
			  [dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('specific-meta-tw-tabs', 'value'),
			  dash.dependencies.Input('hidden-time-output', 'data'),
			  dash.dependencies.Input('hidden-language-output', 'data')
			  ])
def specific_twmeta_dropdown(pathname,league,gmtOffset,lang_index):
	eventid="10000"
	if isinstance(pathname, str) and '/twmeta/' in pathname:
		eventid=pathname.strip('/twmeta/')		
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_specific_twmeta_table(eventid,league,gmtOffset,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('hidden-div3', 'children'),
			  [dash.dependencies.Input('team-applications-table', 'data'),
			  dash.dependencies.Input('url', 'pathname')])
def applications_dropdowns(data,pathname):
	if g.user == None: return ""
	user_id=HELPER_DB.getUserIDFromOktaID(g.user.id)
	if user_id == None: return ""
	team_id="10000"
	if isinstance(pathname, str) and '/teams/' in pathname:
		team_id=pathname.strip('/teams/')		
	ingame_team_id=HELPER_DB.getInGameTeamID(team_id)
	if ingame_team_id == None: return
	cur_data=HELPER_DB.getTeamApplicationsData(ingame_team_id)
	if cur_data != None:
		RESTFUL.processTeamApplications(ingame_team_id, data, cur_data)
	return ""
	
@app.callback(dash.dependencies.Output('hidden-div', 'children'),
			  [dash.dependencies.Input('collections-table-neu', 'data'),
			  dash.dependencies.Input('collections-table-adv', 'data'),
			  dash.dependencies.Input('collections-table-sci', 'data'),
			  dash.dependencies.Input('collections-table-mys', 'data'),
			  dash.dependencies.Input('collections-table-fan', 'data'),
			  dash.dependencies.Input('collections-table-sup', 'data'),
			  dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('collections-add-button', 'n_clicks')],
			  state=[dash.dependencies.State('bulk-card-input', 'value')])
def my_cards_dropdowns(neu,adv,sci,mys,fan,sup,pathname,n_clicks,values):
	unique_user_id_override=None
	user_id=None
	if isinstance(pathname, str):
		if '/player/' in pathname:
			tmp_user_id=pathname.strip('/player/')
			match = re.match('^[0-9]+$', tmp_user_id, re.I)
			if match != None:
				unique_user_id_override=tmp_user_id
				if not HELPER_DB.isValidUserID(unique_user_id_override):
					return html.H1("Oops, this user doesn't exist.")
				user_id=HELPER_DB.getUserIDFromUniqueUserID(unique_user_id_override)
		elif '/mycards' in pathname:
			if g.user == None: return ""
			user_id=HELPER_DB.getUserIDFromOktaID(g.user.id)
	if user_id == None: return ""
	
	data=[]
	if values != None and values != "" and n_clicks != None and n_clicks > 0:
		data=HELPER.getDataFromBulkString(values)
	else:
		if neu != None: data.extend(neu)
		if adv != None: data.extend(adv)
		if sci != None: data.extend(sci)
		if mys != None: data.extend(mys)
		if fan != None: data.extend(fan)
		if sup != None: data.extend(sup)
	cur_collection=HELPER_DB.getUsersCollection(g.user,unique_user_id_override)
	if cur_collection != None:
		RESTFUL.processCollectionsData(user_id, data, cur_collection)
	return ""
	
@app.callback(dash.dependencies.Output('hidden-div2', 'children'),
			  [dash.dependencies.Input('card-comparison-table', 'data'),
			  dash.dependencies.Input('url', 'pathname')])
def card_comparison_dropdowns(data,pathname):
	if g.user == None: return ""
	user_id=HELPER_DB.getUserIDFromOktaID(g.user.id)
	if user_id == None: return ""
	team_id="10000"
	if isinstance(pathname, str) and '/teams/' in pathname:
		team_id=pathname.strip('/teams/')		
	cur_data=HELPER_DB.getTeamWarChoices(team_id)
	if cur_data != None:
		RESTFUL.processCardComparisonData(team_id, data, cur_data)
	return ""
	
@app.callback(dash.dependencies.Output('hidden-div4', 'children'),
			  [dash.dependencies.Input('tw-bracket-table', 'data')])
def bracket_subscribe_dropdown(data):
	if g.user == None: return ""
	email = g.user.profile.email
	cur_data=HELPER_DB.getBracketSubscribe(email)
	RESTFUL.processBracketSubscribe(cur_data, data, email)
	return ""

@app.callback(dash.dependencies.Output('mymatches-sidebar', 'style'),
			  [dash.dependencies.Input('mymatches-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('mymatches-sidebar-button-open', 'n_clicks')
			  ])
def mymatches_sidebar_close(close_clicks,open_clicks):
	return {'top': 0,'display': 'block' if close_clicks!=open_clicks else 'none'}

@app.callback(dash.dependencies.Output('mycards-sidebar', 'style'),
			  [dash.dependencies.Input('mycards-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('mycards-sidebar-button-open', 'n_clicks')
			  ])
def collections_sidebar_close(close_clicks,open_clicks):
	return {'top': 0,'display': 'block' if close_clicks!=open_clicks else 'none'}
	
@app.callback(dash.dependencies.Output('main-sidebar', 'style'),
			  [dash.dependencies.Input('main-sidebar-close', 'n_clicks_timestamp'),
			  dash.dependencies.Input('main-sidebar-open', 'n_clicks_timestamp')
			  ])
def main_sidebar_close(close_clicks,open_clicks):
	to_display = 'none'
	if open_clicks != None and\
		(close_clicks == None or close_clicks < open_clicks):
		to_display = 'block'
	return {'top': 0, 'display': to_display}
	
@app.callback(dash.dependencies.Output('challenge-sidebar', 'style'),
			  [dash.dependencies.Input('challenge-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('challenge-sidebar-button-open', 'n_clicks')
			  ])
def challenge_sidebar_close(close_clicks,open_clicks):
	return {'top': 0, 'display': 'block' if close_clicks!=open_clicks else 'none'}

@app.callback(dash.dependencies.Output('match-sidebar', 'style'),
			  [dash.dependencies.Input('match-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('match-sidebar-button-open', 'n_clicks')
			  ])
def live_matches_sidebar_close(close_clicks,open_clicks):
	return {'top': 0, 'display': 'block' if close_clicks!=open_clicks else 'none'}
	
@app.callback(dash.dependencies.Output('cards-sidebar', 'style'),
			  [dash.dependencies.Input('cards-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('cards-sidebar-button-open', 'n_clicks')
			  ])
def cards_sidebar_close(close_clicks,open_clicks):
	return {'top': 0, 'display': 'block' if close_clicks!=open_clicks else 'none'}
	
@app.callback(dash.dependencies.Output('cardstats-sidebar', 'style'),
			  [dash.dependencies.Input('cardstats-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('cardstats-sidebar-button-open', 'n_clicks')
			  ])
def cardstats_sidebar_close(close_clicks,open_clicks):
	return {'top': 0, 'display': 'block' if close_clicks!=open_clicks else 'none'}
	
@app.callback(dash.dependencies.Output('deckbuilder-sidebar', 'style'),
			  [dash.dependencies.Input('deckbuilder-sidebar-button-close', 'n_clicks_timestamp'),
			  dash.dependencies.Input('deckbuilder-sidebar-button-open', 'n_clicks_timestamp')
			  ])
def deckbuilder_sidebar_close(close_clicks,open_clicks):
	display = 'none'
	if open_clicks != None and (close_clicks == None or open_clicks > close_clicks):
		display = 'block'
	return {'top': 0, 'display': display}
	
@app.callback(dash.dependencies.Output('decks-sidebar', 'style'),
			  [dash.dependencies.Input('decks-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('decks-sidebar-button-open', 'n_clicks')
			  ])
def decks_sidebar_close(close_clicks,open_clicks):
	return {'top': 0, 'display': 'block' if close_clicks!=open_clicks else 'none'}

@app.callback(dash.dependencies.Output('themes-sidebar', 'style'),
			  [dash.dependencies.Input('themes-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('themes-sidebar-button-open', 'n_clicks')
			  ])
def themes_sidebar_close(close_clicks,open_clicks):
	return {'top': 0, 'display': 'block' if close_clicks!=open_clicks else 'none'}
	
@app.callback(dash.dependencies.Output('teams-sidebar', 'style'),
			  [dash.dependencies.Input('teams-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('teams-sidebar-button-open', 'n_clicks')
			  ])
def teams_sidebar_close(close_clicks,open_clicks):
	return {'top': 0, 'display': 'block' if close_clicks!=open_clicks else 'none'}
	
@app.callback(dash.dependencies.Output('player-sidebar', 'style'),
			  [dash.dependencies.Input('player-sidebar-button-close', 'n_clicks'),
			  dash.dependencies.Input('player-sidebar-button-open', 'n_clicks')
			  ])
def player_sidebar_close(close_clicks,open_clicks):
	return {'top': 0, 'display': 'block' if close_clicks!=open_clicks else 'none'}

@app.callback(dash.dependencies.Output('teams-specific-sidebar', 'children'),
			  [dash.dependencies.Input('teams-specific-sidebar-button', 'n_clicks'),
			  dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def teams_specific_sidebar_open(n_clicks,pathname,lang_index):
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		team_id=pathname.strip('/teams/')
	return HELPER.getSideBar("/teams", (n_clicks % 2 == 0), team_id, lindex=lang_index)
	
@app.callback(dash.dependencies.Output('specific-team-refresh-button', 'disabled'),
			  [dash.dependencies.Input('specific-team-refresh-button', 'n_clicks'),
			  dash.dependencies.Input('url', 'pathname')
			  ])
def teams_specific_refresh_button(n_clicks,pathname):
	team_id="10000"
	if isinstance(pathname, str) and '/teams/' in pathname:
		team_id=pathname.strip('/teams/')
	last_refresh=HELPER_DB.getLastRefreshFromUniqueTeamID(team_id)
	can_refresh = last_refresh < time.time() - 24*3600
	if n_clicks != None and n_clicks == 1 and\
		HELPER_DB.isValidTeamID(team_id) and can_refresh:
		RESTFUL.refreshTeam(team_id)
	return (n_clicks != None and n_clicks > 0) or not can_refresh
	
@app.callback(dash.dependencies.Output('new_kid_art', 'children'),
			  [dash.dependencies.Input('url', 'pathname')])
def new_kid_art_callback(pathname):
	user_id=None
	if isinstance(pathname, str) and '/player/' in pathname:
		user_id=pathname.strip('/player/')
	outfit_data,gear_data,skin = HELPER_DB.getOutfitData(user_id)
	if gear_data == None: return ''
	
	BoxSkin = [2211,0,0]
	Head = None
	Body = [204,0,0]
	Eyebrows = None
	Eyes = [1554,0]
	FacialHair = None
	Glasses = None
	Hair = None
	Mouth = [1555,0]
	Detail = None
	for g in gear_data:
		if g[0] not in DATABASE.GEAR_MAP: continue
		result = DATABASE.GEAR_MAP[g[0]]
		slot = result["Slot"]
		if slot == 'BoxSkin': BoxSkin = g
		elif slot == 'Head': Head = g
		elif slot == 'Body': Body = g
	
	for g in outfit_data:
		if g[0] not in DATABASE.OUTFIT_MAP: continue
		result = DATABASE.OUTFIT_MAP[g[0]]
		slot = result["Slot"]
		if slot == 'Eyebrows': Eyebrows = g
		elif slot == 'Eyes': Eyes = g
		elif slot == 'FacialHair': FacialHair = g
		elif slot == 'Glasses': Glasses = g
		elif slot == 'Hair': Hair = g
		elif slot == 'Mouth': Mouth = g
		elif slot == 'Detail': Detail = g
	
	encoded_image = NK_ART.build_new_kid(skin, BoxSkin, Head, Body, Eyebrows, Eyes, FacialHair, Glasses, Hair, Mouth, Detail)
	return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode('utf-8')))
	
def getProjectedCapsByMMRS(mmr_list):
	total_caps=0
	for mmr in mmr_list.values():
		for arena in DATABASE.ARENA_MAP.keys():
			mmr_min,mmr_max=DATABASE.ARENA_MAP[arena]
			if mmr_max == None and mmr >= mmr_min:
				total_caps+=DATABASE.PROJECTED_CAPS[arena]
				break
			elif mmr >= mmr_min and mmr < mmr_max:
				total_caps+=DATABASE.PROJECTED_CAPS[arena]
				break
	return total_caps*3
	
@app.callback(dash.dependencies.Output('specific-team-tabs-tw-content', 'children'),
              [dash.dependencies.Input('specific-team-tabs-tw', 'value'),
			  dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('url', 'search')])
def teams_specific_tabs_tw(tab, pathname, search):
	global tab_styles,tab_style,tab_selected_style
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	if not HELPER_DB.isValidTeamID(team_id):
		return html.H3('That is not a valid team.')
	full_search = {}
	if search != None and "?" in search:
		tmp_search = search.strip("?")
		if "&" in tmp_search:
			n_search = tmp_search.split("&")
			for elem in n_search:
				eq_search = elem.split("=")
				if len(eq_search) == 2:
					full_search[eq_search[0]]=eq_search[1]
		else:
			eq_search = tmp_search.split("=")
			if len(eq_search) == 2:
				full_search[eq_search[0]]=eq_search[1]
	access_level=HELPER_DB.getAccessLevelTeam(g.user,None,team_id)
	if tab == 'votes':
		project_caps=HELPER_DB.getTeamsMMR(team_id)
		project_caps=getProjectedCapsByMMRS(project_caps)
		if access_level == -1:
			return [
				dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=votes"),
				ARTICLES.TWVoteDescription(),
				html.H5(f"Projected Caps: {project_caps}"),
				html.H1("This works, but you need to be on the team to view it.")
			]
		return [
			html.Div(id='card-comparison-content', children=[
			dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=votes"),
			ARTICLES.TWVoteDescription(),
			html.H5(f"Project Caps: {project_caps}"),
			generate_card_comparison_table(team_id),
			]),
			html.Div(id='hidden-div2')
		]
	elif tab == 'upgrade':
		if access_level == -1:
			return html.H1("This works, but you need to be on the team to view it.")
		target='log'
		if 't3' in full_search: target=full_search['t3']
		return [dcc.Tabs(
			id="specific-team-tabs-tw-upgrades",
			value=target,
			children=[
				dcc.Tab(label='Log', value='log', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Cards', value='cards', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Players', value='players', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Assignments', value='assign', style=tab_style, selected_style=tab_selected_style),
			],persistence=True,
			mobile_breakpoint=0,
			style=tab_styles),
			html.Div(id='specific-team-tabs-tw-upgrades-content')
		]
	elif tab == 'battle':
		target='live'
		if 't3' in full_search: target=full_search['t3']
		return [dcc.Tabs(
			id="specific-team-tabs-tw-battle",
			value=target,
			children=[
				dcc.Tab(label='Live', value='live', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='History', value='history', style=tab_style, selected_style=tab_selected_style),
			],persistence=True,
			mobile_breakpoint=0,
			style=tab_styles),
			html.Div(id='specific-team-tabs-tw-battle-content')
		]
	elif tab == 'summary':
		if access_level == -1:
			return html.H1("This works, but you need to be on the team to view it.")
		target='cards'
		if 't3' in full_search: target=full_search['t3']
		return [dcc.Tabs(
			id="specific-team-tabs-tw-summary",
			value=target,
			children=[
				dcc.Tab(label='By Cards', value='cards', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='By Players (Themes)', value='players', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='By Players (All Cards)', value='players-all', style=tab_style, selected_style=tab_selected_style),
			],persistence=True,
			mobile_breakpoint=0,
			style=tab_styles),
			html.Div(id='specific-team-tabs-tw-summary-content')
		]
	elif tab == 'history':
		if access_level == -1:
			return html.H1("This works, but you need to be on the team to view it.")
		target='scores'
		if 't3' in full_search: target=full_search['t3']
		return [dcc.Tabs(
			id="specific-team-tabs-tw-history",
			value=target,
			children=[
				dcc.Tab(label='Scores', value='scores', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Caps', value='caps', style=tab_style, selected_style=tab_selected_style),
			],persistence=True,
			mobile_breakpoint=0,
			style=tab_styles),
			html.Div(id='specific-team-tabs-tw-history-content')
		]
	else:
		return html.H3("Under Construction: Only members on the team will be able to view this.")
		
@app.callback(dash.dependencies.Output('specific-team-tabs-tw-summary-content', 'children'),
              [dash.dependencies.Input('specific-team-tabs-tw-summary', 'value'),
			  dash.dependencies.Input('url', 'pathname')])
def teams_specific_tabs_tw_summary(tab, pathname):
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	
	if tab == 'cards':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=summary&t3=cards"),
			generate_teamwar_summary_cards(team_id)]
	elif tab == 'players':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=summary&t3=players"),
			generate_teamwar_summary_players(team_id)]
	elif tab == 'players-all':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=summary&t3=players"),
			generate_teamwar_summary_players_all(team_id)]
	else:
		return html.H3("Under Construction: Only members on the team will be able to view this.")

@app.callback(dash.dependencies.Output('specific-team-tabs-tw-upgrades-content', 'children'),
              [dash.dependencies.Input('specific-team-tabs-tw-upgrades', 'value'),
			  dash.dependencies.Input('url', 'pathname')])
def teams_specific_tabs_tw_upgrade(tab, pathname):
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	
	if tab == 'log':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=upgrade&t3=log"),
			*generate_teamwar_upgrades_spent(team_id)]
	elif tab == 'cards':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=upgrade&t3=cards"),
			*generate_teamwar_upgrades_cards(team_id)]
	elif tab == 'players':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=upgrade&t3=players"),
			*generate_teamwar_upgrades_players(team_id)]
	elif tab == 'assign':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=upgrade&t3=assign"),
			generate_teamwar_upgrades_data(team_id)]
	else:
		return html.H3("Under Construction: Only members on the team will be able to view this.")
		
@app.callback(dash.dependencies.Output('specific-team-tabs-tw-battle-content', 'children'),
              [dash.dependencies.Input('specific-team-tabs-tw-battle', 'value'),
			  dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('hidden-time-output', 'data')])
def teams_specific_tabs_tw_battle(tab, pathname,gmtOffset):
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	
	if tab == 'live':
		email = None
		if g.user != None:
			email = g.user.profile.email
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=battle&t3=live"),
			*generate_teamwar_bracket_table(team_id,gmtOffset,email)]
	elif tab == 'history':
		if team_id == None:
			return html.H3("Invalid Team. How did you get here?")
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=battle&t3=history"),
			*generate_teamwar_bracket_history_table(team_id,gmtOffset)]
	else:
		return html.H3("Under Construction: Only members on the team will be able to view this.")

@app.callback(dash.dependencies.Output('specific-team-tabs-tw-history-content', 'children'),
              [dash.dependencies.Input('specific-team-tabs-tw-history', 'value'),
			  dash.dependencies.Input('url', 'pathname')])
def teams_specific_tabs_tw_history(tab, pathname):
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	
	style_dropdown={
		'text-transform': 'lowercase',
		'font-variant': 'all-small-caps',
		'color': 'black',
		'display': 'inline-block',
		'width': "75%"
	}
	if tab == 'scores':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=history&t3=scores"),
			html.Br(),
			html.H5("History:"),
			dcc.Dropdown(
				id='tw-history-scores-dropdown',
				value=12,
				options=[
					{'label': '4 Weeks', 'value': 4},
					{'label': '8 Weeks', 'value': 8},
					{'label': '12 Weeks', 'value': 12},
					{'label': '24 Weeks', 'value': 24},
					{'label': '52 Weeks', 'value': 52}
				],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.H5("Filter:"),
			dcc.Dropdown(
				id='tw-history-scores-filter-dropdown',
				value=0,
				options=[
					{'label': 'Loading...', 'value': 0},
				],
				searchable=False,
				clearable=False,
				style=style_dropdown,
				multi=True
			),
			html.Div(id='specific-team-tabs-tw-history-content-scores')]
	elif tab == 'caps':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=team-wars&t2=history&t3=caps"),
			html.Br(),
			html.H5("History:"),
			dcc.Dropdown(
				id='tw-history-caps-dropdown',
				value=12,
				options=[
					{'label': '4 Weeks', 'value': 4},
					{'label': '8 Weeks', 'value': 8},
					{'label': '12 Weeks', 'value': 12},
					{'label': '24 Weeks', 'value': 24},
					{'label': '52 Weeks', 'value': 52}
				],
				searchable=False,
				clearable=False,
				style=style_dropdown
			),
			html.Div(id='specific-team-tabs-tw-history-content-caps')]
	else:
		return html.H3("Oops. How did you get here?")

@app.callback([dash.dependencies.Output('tw-history-scores-filter-dropdown', 'value'),
				dash.dependencies.Output('tw-history-scores-filter-dropdown', 'options')],
              [dash.dependencies.Input('tw-history-scores-dropdown', 'value'),
			  dash.dependencies.Input('url', 'pathname')])
def teams_specific_tabs_tw_history_scores(value, pathname):
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	children, all_dates = generate_teamwar_history_table(team_id,value)
	options=[]
	value_list=[]
	for i in range(len(all_dates)):
		options.append({'label': all_dates[i], 'value': i})
		value_list.append(i)
	return value_list, options
	
@app.callback(dash.dependencies.Output('specific-team-tabs-tw-history-content-scores', 'children'),
              [dash.dependencies.Input('tw-history-scores-filter-dropdown', 'value'),
			  dash.dependencies.Input('url', 'pathname')])
def teams_specific_tabs_tw_history_scores(value, pathname):
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	weeks_ago = 0
	if type(value) == int:
		weeks_ago = 12
		value = []
	if type(value) == list: weeks_ago = max(value) + 1
	children, all_dates = generate_teamwar_history_table(team_id,weeks_ago,value)
	return children

@app.callback(dash.dependencies.Output('specific-team-tabs-tw-history-content-caps', 'children'),
              [dash.dependencies.Input('tw-history-caps-dropdown', 'value'),
			  dash.dependencies.Input('url', 'pathname')])
def teams_specific_tabs_tw_history_caps(value, pathname):
	team_id=None
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	return generate_teamwar_history_caps_table(team_id,value)

@app.callback(dash.dependencies.Output('specific-team-tabs-requests-content', 'children'),
              [dash.dependencies.Input('specific-team-tabs-requests', 'value'),
			  dash.dependencies.Input('url', 'pathname')
			  ])
def teams_specific_tabs_requests(tab, pathname):
	team_id="10000"
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	if not HELPER_DB.isValidTeamID(team_id):
		return html.H3('That is not a valid team.')
	access_level=HELPER_DB.getAccessLevelTeam(g.user,None,team_id)
	if access_level == -1:
		return html.H1("This works, but you need to be on the team to view it.")
	if tab == 'requested':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=requests&t2=requested"),
			*generate_card_requests_table(team_id,access_level)]
	if tab == 'donated':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=requests&t2=donated"),
			*generate_card_donations_table(team_id,access_level)]
	if tab == 'summary':
		return [dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=requests&t2=summary"),
			*generate_card_summary_table(team_id)]
	return html.H3("Under Construction: Only members on the team will be able to view this.")
	
@app.callback(dash.dependencies.Output('specific-team-tabs-content', 'children'),
              [dash.dependencies.Input('specific-team-tabs', 'value'),
			  dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('url', 'search')])
def teams_specific_tabs(tab, pathname, search):
	global tab_styles,tab_style,tab_selected_style
	team_id="10000"
	if isinstance(pathname, str) and '/teams/' in pathname:
		tmp_team_id=pathname.strip('/teams/')
		match = re.match('^[0-9]+$', tmp_team_id, re.I)
		if match != None:
			team_id=tmp_team_id
	if not HELPER_DB.isValidTeamID(team_id):
		return html.H3('That is not a valid team.')
	full_search = {}
	if search != None and "?" in search:
		tmp_search = search.strip("?")
		if "&" in tmp_search:
			n_search = tmp_search.split("&")
			for elem in n_search:
				eq_search = elem.split("=")
				if len(eq_search) == 2:
					full_search[eq_search[0]]=eq_search[1]
		else:
			eq_search = tmp_search.split("=")
			if len(eq_search) == 2:
				full_search[eq_search[0]]=eq_search[1]
				
	if tab == 'members':
		access_level=HELPER_DB.getAccessLevelTeam(g.user,None,team_id)
		last_refresh=HELPER_DB.getLastRefreshFromUniqueTeamID(team_id)
		last_refresh_pretty=""
		if last_refresh != -1:
			last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(last_refresh))
		return [
			html.Button('Refresh',
				className="w3-button",
				id='specific-team-refresh-button',
				n_clicks=0,
				disabled=True
			),
			html.H3(f"Last Refresh {last_refresh_pretty} PST"),
			ARTICLES.SpecificTeamMembersTabDescription(),
			generate_team_members_table(team_id,access_level)
		]
	elif tab == 'team-events':
		access_level=HELPER_DB.getAccessLevelTeam(g.user,None,team_id)
		if access_level == -1:
			return html.H1("This works, but you need to be on the team to view it.")
			
		return generate_teamevent_history_table(team_id)
	elif tab == 'applications':
		access_level=HELPER_DB.getAccessLevelTeam(g.user,None,team_id)
		if access_level == -1: return ARTICLES.SpecificTeamApplicationsTabDescription()
		return [
			dcc.Link("Quick Link", href=f"/teams/{team_id}?t1=applications"),
			ARTICLES.SpecificTeamApplicationsTabDescription(),
			generate_team_applications_table(team_id,access_level),
			html.Div(id='hidden-div3',style={'display': 'none'})
		]
	elif tab == 'team-wars':
		START_TIME = HELPER_DB.getTeamWarStartTime()
		UPGRADE_START = START_TIME + 3600 * 24 * 2 #2 Days Later
		BATTLE_START = START_TIME + 3600 * 24 * 5 #5 Days Later
		cur_time = int(time.time())
		
		#If it's Monday 5am to Wednesday 5am - default card choices
		#If it's Wednesday 5am to Saturday 5am - default caps
		#If it's Saturday 5am to Monday 5am - default bracket
		target='battle'
		if 't2' in full_search: target=full_search['t2']
		elif cur_time < UPGRADE_START: target='votes'
		elif cur_time < BATTLE_START: target='upgrade'
		else: target='battle'
		
		return [dcc.Tabs(
			id="specific-team-tabs-tw",
			value=target,
			children=[
				dcc.Tab(label='Vote', value='votes', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Upgrade', value='upgrade', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Battle', value='battle', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Summary', value='summary', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='History', value='history', style=tab_style, selected_style=tab_selected_style),
			],persistence=True,
			mobile_breakpoint=0,
			style=tab_styles
		),
		html.Div(id='specific-team-tabs-tw-content')
		]
	elif tab == 'requests' or ('t1' in full_search and 'requests' == full_search['t1']):
		target='requested'
		if 't2' in full_search: target=full_search['t2']
		return [dcc.Tabs(
			id="specific-team-tabs-requests",
			value=target,
			children=[
				dcc.Tab(label='Requested', value='requested', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Donated', value='donated', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Summary', value='summary', style=tab_style, selected_style=tab_selected_style),
				dcc.Tab(label='Queue', value='queue', style=tab_style, selected_style=tab_selected_style),
			],persistence=True,
			mobile_breakpoint=0,
			style=tab_styles
		),
		html.Div(id='specific-team-tabs-requests-content')
		]
		
	else:
		return html.H3("Under Construction: Only members on the team will be able to view this.")
		
@app.callback(dash.dependencies.Output('specific-bracket-tabs-content', 'children'),
              [dash.dependencies.Input('specific-bracket-tabs', 'value'),
			  dash.dependencies.Input('hidden-time-output', 'data'),
			  dash.dependencies.Input('url', 'search'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def league_specific_tabs(tab,gmtOffset,search,lang_index):
	full_search = {}
	if search != None and "?" in search:
		tmp_search = search.strip("?")
		if "&" in tmp_search:
			n_search = tmp_search.split("&")
			for elem in n_search:
				eq_search = elem.split("=")
				if len(eq_search) == 2:
					full_search[eq_search[0]]=eq_search[1]
		else:
			eq_search = tmp_search.split("=")
			if len(eq_search) == 2:
				full_search[eq_search[0]]=eq_search[1]
	if tab == 'gold' or ('t1' in full_search and 'gold' == full_search['t1']):
		return generate_allbracket_table('gold',gmtOffset,lang_index)
	if tab == 'silver' or ('t1' in full_search and 'silver' == full_search['t1']):
		return generate_allbracket_table('silver',gmtOffset,lang_index)
	if tab == 'bronze' or ('t1' in full_search and 'bronze' == full_search['t1']):
		return generate_allbracket_table('bronze',gmtOffset,lang_index)
	if tab == 'wood' or ('t1' in full_search and 'wood' == full_search['t1']):
		return generate_allbracket_table('wood',gmtOffset,lang_index)
	if tab == 'summary' or ('t1' in full_search and 'summary' == full_search['t1']):
		return generate_allbracket_summary(lang_index)
	return html.H3(HELPER.tr('Unknown League',lang_index))
		
@app.callback(dash.dependencies.Output('specific-card-tabs-content', 'children'),
              [dash.dependencies.Input('specific-card-tabs', 'value'),
			  dash.dependencies.Input('url', 'pathname'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def card_specific_tabs(tab,pathname,lang_index):
	card_id=pathname.strip('/cards/')
	match = re.match('^[0-9]+$', card_id, re.I)
	if match == None:
		return html.H3(HELPER.tr('Oops, something went wrong.',lang_index))
	if tab == 'simple':
		return [generate_carddetails_table(card_id,lang_index)]
	if tab == 'detailed':
		return [generate_cardfulldetails_table(card_id,lang_index),
		generate_cardwinrate_table(card_id,lang_index)]
	return html.H3(HELPER.tr('Unknown Tab... How did you get here?',lang_index))
	
@app.callback(dash.dependencies.Output('themes-content', 'children'),
			  [dash.dependencies.Input('themes-dropdown-rank', 'value'),
			  dash.dependencies.Input('themes-dropdown-time', 'value'),
			  dash.dependencies.Input('hidden-time-output','data'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def themes_dropdown(rank,search_time,gmtOffset,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_themes_table(rank,search_time,gmtOffset,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('decks-content', 'children'),
			  [dash.dependencies.Input('decks-dropdown-rank', 'value'),
			  dash.dependencies.Input('hidden-time-output','data'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def decks_dropdown(rank,gmtOffset,lang_index):
	return html.Div(
	className='page',
	children=[
		html.Div(
			id='las-table',
			children=generate_decks_content(rank,gmtOffset,lang_index)
		)]
	)
	
@app.callback(dash.dependencies.Output('footer-content', 'children'),
			  [dash.dependencies.Input('hidden-language-output', 'data')])
def footer_update(lang_index):
	return html.Div(children=[
		html.H5("SPPDReplay.net",style={'display':'block','text-align': 'center'}),
		html.A(html.Img(src='https://i.imgur.com/XpgtidC.jpg',
			style={'width':'40px','height':'40px'}),
			href='https://discord.gg/j4Wchza',
			style={'display': 'block','margin-left': 'auto','margin-right': 'auto','width':'10%'}),
		html.H6(HELPER.tr('Not affiliated with Ubisoft/Redlynx.',lang_index),
			style = {'display': 'block','margin-left': 'auto','margin-right': 'auto','width':'50%','text-align': 'center'}),
		html.Div(children=[
			html.Div(children=[
				html.H6('SPPDReplay.net',style={'font-weight': 'bold','text-align': 'center'}),
				html.A(HELPER.tr('Downloads',lang_index), href='/downloads',
					style={'display':'block','text-align': 'center'}),
				html.A(HELPER.tr('Donate',lang_index), href='/donate',
					style={'display':'block','text-align': 'center'}),
			],
			style={'display':'inline-block','width':'50%','margin-left': 'auto','margin-right': 'auto'}
			),
			html.Div(children=[
				html.H6(HELPER.tr('Support',lang_index),style={'font-weight': 'bold','text-align': 'center'}),
				html.A(HELPER.tr('Contact Us',lang_index), href='https://github.com/rbrasga/SPPD-Deck-Tracker/issues',
					style={'display':'block','text-align': 'center'}),
				html.A(HELPER.tr('About Us',lang_index), href='/about',
					style={'display':'block','text-align': 'center'}),
			],
			style={'display':'inline-block','width':'50%','margin-left': 'auto','margin-right': 'auto'}
			)
		])
	],
	style={'background-color':'#020432'}
	)
	
@app.callback(dash.dependencies.Output('home-live-matches', 'children'),
			  [dash.dependencies.Input('home-interval-two', 'n_intervals'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def home_live_matches(n_intervals,lang_index):
	last_seven_days_total,today_total,user_contrib,match_data = HELPER_DB.get_home_live_match_data()

	pretty_matches=[]
	for ID,MMR1,themes1,MMR2,themes2 in match_data:
		themes1 = ",".join(x for x in themes1)
		themes2 = ",".join(x for x in themes2)
		pretty_matches.append(html.A(f"{themes1} #{MMR1}\tVS\t{themes2} #{MMR2}",href=f'/match/{ID}',
			style={
				'min-width': '300px','min-height': '75px',
				'font-size':'large', 'font-weight': 'bold', 'color': 'white',
				'background-color': '#616161'
			}
		))
		pretty_matches.append(html.Br())
	
	return [html.A(HELPER.tr("Live Matches",lang_index), href='/match', style={'font-size':'x-large', 'font-weight': 'bold'}),
	html.H3(HELPER.tr("Games Last 7 Days: ",lang_index) + str(last_seven_days_total)),
	html.H3(HELPER.tr("Games Today: ",lang_index) + str(today_total)),
	html.Div(children=pretty_matches),
	html.H3(HELPER.tr("Contributors: ",lang_index) + str(user_contrib)),
	html.A(HELPER.tr("Become a Contributor",lang_index),href='/downloads')
	]
	
@app.callback(dash.dependencies.Output('home-best-deck', 'children'),
			  [dash.dependencies.Input('home-interval', 'n_intervals'),
			  dash.dependencies.Input('hidden-language-output', 'data')])
def home_best_deck(n_intervals,lang_index):
	#Randomly select the best deck for the different tiers
	#Display that deck and the tier
	META_FILTER=HELPER_DB.getDistinctNamesFromMetaReport()
	meta_name=random.choice(META_FILTER)
	deck=HELPER_DB.getHomeBestDeck(meta_name)
	themes=HELPER_DB.findThemes(deck)

	html_list=[]
	html_list.append(html.A(HELPER.tr("The best deck in",lang_index), href='/decks', style={'font-size':'large', 'font-weight': 'bold'}))
	html_list.append(html.H3(HELPER.tr(meta_name,lang_index)))
	CARD_NAMES1=[]
	CARD_NAMES2=[]
	for x in range(12):
		target_value = HELPER_DB.getCardName(deck[x])
		if x % 2 == 0:
			CARD_NAMES1.append(target_value)
		else:
			CARD_NAMES2.append(target_value)
	if len(themes) > 2: themes = themes[:2]
	theme1_img,theme2_img=DATABASE.BACKGROUND_MAP[','.join(x for x in themes)]
	html_list.append(html.Div([
		html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES1)],
				style={'display': 'inline-block'}
			)
		]),
		html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES2)],
				style={'display': 'inline-block'}
			)
		])
		],
		style = {
			'background-image': f"url('{theme1_img}'), url('{theme2_img}')",
			'background-repeat': 'no-repeat, no-repeat',
			'background-attachment': 'scroll, scroll',
			'background-position': 'left center, right center',
			'background-size': '50%, 50%',
			#'background-size': ', auto 100%',
			#'height':'231px'
		}
	))
	return html_list
	
def sortCollection():
	sorted_collection=[]
	for key in DATABASE.DECK_MAP.keys():
		if key == 0: continue
		name=DATABASE.DECK_MAP[key][0].upper()
		energy=DATABASE.DECK_MAP[key][1]
		theme=5
		raw_theme=DATABASE.DECK_MAP[key][3]
		if raw_theme == "neu": theme=0
		elif raw_theme == "adv": theme=1
		elif raw_theme == "sci": theme=2
		elif raw_theme == "mys": theme=3
		elif raw_theme == "fan": theme=4
		elif raw_theme == "sup": theme=5
		elif SETTINGS.DEBUG: print("[ERROR] Couldn't find theme for "+str(key)+", "+name+",Theme: "+raw_theme)
		sorted_collection.append([name,energy,theme])
	sorted_l = sorted(sorted_collection, key=lambda x: (x[2], x[1], x[0]))
	return sorted_l
	
def sortCollectionWithKey():
	sorted_collection=[]
	for key in DATABASE.DECK_MAP.keys():
		if key == 0: continue
		name=DATABASE.DECK_MAP[key][0].upper()
		energy=DATABASE.DECK_MAP[key][1]
		theme=5
		raw_theme=DATABASE.DECK_MAP[key][3]
		if raw_theme == "neu": theme=0
		elif raw_theme == "adv": theme=1
		elif raw_theme == "sci": theme=2
		elif raw_theme == "mys": theme=3
		elif raw_theme == "fan": theme=4
		elif raw_theme == "sup": theme=5
		elif SETTINGS.DEBUG: print("[ERROR] Couldn't find theme for "+str(key)+", "+name+",Theme: "+raw_theme)
		sorted_collection.append([name,energy,theme,key])
	sorted_l = sorted(sorted_collection, key=lambda x: (x[2], x[1], x[0]))
	return sorted_l
	
def sortCollectionWithKey_all():
	sorted_collection=[]
	for elem in HELPER_DB.getAllCardsTableData():
		key = elem[0]
		if key == 0: continue
		NAME,COST,TYPE,THEME,RARITY = HELPER_DB.getCardData(key)
		theme=5
		if THEME == "neu": theme=0
		elif THEME == "adv": theme=1
		elif THEME == "sci": theme=2
		elif THEME == "mys": theme=3
		elif THEME == "fan": theme=4
		elif THEME == "sup": theme=5
		elif SETTINGS.DEBUG: print("[ERROR] Couldn't find theme for "+str(key)+", "+NAME+",Theme: "+THEME)
		sorted_collection.append([NAME,COST,theme,key])
	sorted_l = sorted(sorted_collection, key=lambda x: (x[2], x[1], x[0]))
	return sorted_l

def getUpgradesSpentReport(cols,teamid):
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	table_data, blobid_to_time=HELPER_DB.getTeamWarUpgradesSpentTableData(teamid)
	SUMMARY=HELPER_DB.getTeamWarUpgradesSummary(teamid) #TOTAL CARDS CAPS, UNSPENT, TOTAL USERS COLLECTED, UPDATED
	if len(table_data) == 0: return META_REPORT,SUMMARY
	for key in sorted(table_data.keys()): # { blobid: [{userid: spent, userid: spent},{cardid: spent, cardid: spent} ], ...}
		TIME=blobid_to_time[key]
		DATE=time.strftime('%Y-%m-%d %H:%M', time.localtime(TIME))
		USERS,CARDS=table_data[key]
		USERS_STR=[]
		for user in USERS.keys():
			spent=USERS[user]
			USERS_STR.append(f"{user} : {spent}")
		USERS_STR=", ".join(x for x in USERS_STR)
		CARDS_STR=[]
		for card in CARDS.keys():
			spent=CARDS[card]
			CARDS_STR.append(f"{card} : {spent}")
		CARDS_STR=", ".join(x for x in CARDS_STR)
		META_REPORT[cols[0]].append(DATE)
		META_REPORT[cols[1]].append(USERS_STR)
		META_REPORT[cols[2]].append(CARDS_STR)
	return META_REPORT, SUMMARY
	
def getUpgradesCardsReport(cols,teamid):
	#cols = ['id', 'Current Level', '+FF', 'Current Caps', 'Next Level Caps']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	table_data=HELPER_DB.getTeamWarUpgradesCardsTableData(teamid)
	SUMMARY=HELPER_DB.getTeamWarUpgradesSummary(teamid) #TOTAL CARDS CAPS, UNSPENT, TOTAL USERS COLLECTED, UPDATED
	if len(table_data) == 0: return META_REPORT,SUMMARY
	for cardid in table_data.keys(): # { cardid: total, ...}
		total = table_data[cardid]
		level,next_caps,prev_caps=getCardLevelByCaps(cardid,total)
		display_next_caps=next_caps-prev_caps
		cur_caps=total-prev_caps
		card_name=HELPER_DB.getCardName(cardid)
		offset = getWALOffset(cardid) - 4
		META_REPORT[cols[0]].append(card_name)
		META_REPORT[cols[1]].append(level)
		META_REPORT[cols[2]].append(level + offset)
		META_REPORT[cols[3]].append(f'{cur_caps}/{display_next_caps}')
		META_REPORT[cols[4]].append(display_next_caps-cur_caps)
	return META_REPORT, SUMMARY
	
def getThemeMatchups(cols,lang_index):
	#cols = ['Your Themes']
	META_REPORT={}
	data_set,columns=HELPER_DB.getThemeMatchupsData()
	cols.extend(columns)
	for i in cols: META_REPORT[i]=[]
	for theme1 in columns:
		META_REPORT[cols[0]].append(HELPER.tr(theme1,lang_index))
		for theme2 in columns:
			if theme1 == theme2:
				META_REPORT[theme2].append('/')
			else:
				VERSUS = f"{theme1} vs {theme2}"
				WIN = data_set[VERSUS]
				META_REPORT[theme2].append(WIN)
	return META_REPORT,cols
	
def getUpgradesPlayersReport(cols,teamid):
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	table_data,earned_data=HELPER_DB.getTeamWarUpgradesPlayerTableData(teamid)
	no_caps_users=HELPER_DB.getTeamWarUpgradesPlayerTableData_nocaps(teamid)
	SUMMARY=HELPER_DB.getTeamWarUpgradesSummary(teamid) #TOTAL CARDS CAPS, UNSPENT, TOTAL USERS COLLECTED, UPDATED
	if len(table_data) == 0: return META_REPORT,SUMMARY
	total_spent, cumulative_total, total_day1, total_day2, total_day3 = [0,0,0,0,0]
	for username in table_data.keys(): # { player: [spent,total], ...}
		SPENT,TOTAL=table_data[username]
		META_REPORT[cols[0]].append(username)
		META_REPORT[cols[1]].append(SPENT)
		META_REPORT[cols[2]].append(TOTAL)
		result = earned_data[username]
		META_REPORT[cols[3]].append(result[0])
		META_REPORT[cols[4]].append(result[1])
		META_REPORT[cols[5]].append(result[2])
		total_spent+=SPENT
		cumulative_total+=TOTAL
		if type(result[0]) == int: total_day1+=result[0]
		if type(result[1]) == int: total_day2+=result[1]
		if type(result[2]) == int: total_day3+=result[2]
	for username in no_caps_users:
		META_REPORT[cols[0]].append(username)
		META_REPORT[cols[1]].append(0)
		META_REPORT[cols[2]].append(0)
		META_REPORT[cols[3]].append("Pending")
		META_REPORT[cols[4]].append("Pending")
		META_REPORT[cols[5]].append("Pending")
	table_data = ["TOTAL", total_spent, cumulative_total, total_day1, total_day2, total_day3]
	index=0
	for i in cols:
		META_REPORT[i].append(table_data[index])
		index+=1
	return META_REPORT, SUMMARY
	
def getSummaryCardsReport(cols,teamid):
	#cols = ['id','AVG','WAL','1','2','3','4','5','6','7']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	user_cards_map=HELPER_DB.getSummaryCardTableData(teamid) #{ userid: {cardid : [level,upgrades], ...}, ... }
	for elem in sortCollection():
		name=elem[0]
		cardid=DATABASE.LOWER_NAME_TO_ID[name.lower()]
		AVG=[]
		LEVELS=[]
		for user in user_cards_map.keys():
			if cardid in user_cards_map[user]:
				level,upgrades=user_cards_map[user][cardid]
				min_upgrades,max_upgrades=DATABASE.WAL_MAP[level]
				delta_upgrades=max_upgrades-min_upgrades+1
				level_with_upgrades=level+float(upgrades)/delta_upgrades
				AVG.append(level_with_upgrades)
				LEVELS.append(level)
		total_count=[0,0,0,0,0,0,0]
		for level in LEVELS:
			if level > 0 and level < 8:
				total_count[level-1]+=1
		show_avg="0"
		show_wal="0"
		if len(AVG) > 0:
			actual_avg=float(sum(AVG)) / len(AVG)
			show_avg="%.2f" % actual_avg
			show_wal="%.2f" % (actual_avg + getWALOffset(cardid))
		META_REPORT[cols[0]].append(name)
		META_REPORT[cols[1]].append(show_avg)
		META_REPORT[cols[2]].append(show_wal)
		for i in range(len(total_count)):
			level=i+1
			META_REPORT[f"{level}"].append(total_count[i])
	return META_REPORT
	
def getSummaryPlayersReport(cols,teamid):
	#cols = ['id','MMR','NK Level','WAL Rank','WAL','Neu','Adv','Sci','Mys','Fan','Sup']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	team_table_data,_=HELPER_DB.getTeamDetailsTableData(teamid)
	if team_table_data == None: return META_REPORT
	user_cards_map=HELPER_DB.getSummaryCardTableData(teamid) #{ userid: {cardid : [level,upgrades], ...}, ... }
	user_to_wal_map={}
	wal_rank=[]
	for userid in user_cards_map.keys():
		if userid not in user_to_wal_map:
			user_to_wal_map[userid]=[0,0,0,0,0,0,0,0,0,0]
		wal_map={}
		wal_map['all']=[]
		for cardid in user_cards_map[userid].keys():
			if cardid in DATABASE.DECK_MAP:
				THEME = DATABASE.DECK_MAP[cardid][3]
				if THEME not in wal_map:
					wal_map[THEME]=[]
				level,upgrades=user_cards_map[userid][cardid]
				min_upgrades,max_upgrades=DATABASE.WAL_MAP[level]
				delta_upgrades=max_upgrades-min_upgrades+1
				level_with_upgrades=level+float(upgrades)/delta_upgrades
				card_wal=level_with_upgrades+getWALOffset(cardid)
				wal_map[THEME].append(card_wal)
				wal_map['all'].append(card_wal)
		for THEME in wal_map.keys():
			index = -1
			if THEME == 'all': index = 3
			elif THEME == 'neu': index = 4
			elif THEME == 'adv': index = 5
			elif THEME == 'sci': index = 6
			elif THEME == 'mys': index = 7
			elif THEME == 'fan': index = 8
			elif THEME == 'sup': index = 9
			theme_data = wal_map[THEME]
			if index != -1 and len(theme_data) > 0:
				result = float(sum(theme_data))/len(theme_data)
				user_to_wal_map[userid][index] = result
				if THEME == 'all':
					wal_rank.append([userid,result])
	mmr_nk_map={}
	for row in team_table_data:
		#y.ID, y.NAME, y.PLATFORM, x.ROLE, x.MMR, x.NKLEVEL, x.DONATED_CUR, x.JOINDATE
		if row != None:
			userid = row[0]
			name = row[1]
			mmr = row[4]
			nklevel = row[5]
			mmr_nk_map[userid]=[name,mmr,nklevel]
	sorted_wal_rank = sorted(wal_rank, key=lambda x: (x[1], x[0]), reverse=True)
	wal_rank_num=1
	for elem in sorted_wal_rank:
		userid=elem[0]
		user_to_wal_map[userid][2]=wal_rank_num
		wal_rank_num+=1
		name="Unknown"
		if userid in mmr_nk_map:
			name,mmr,nklevel = mmr_nk_map[userid]
			user_to_wal_map[userid][0]=mmr
			user_to_wal_map[userid][1]=nklevel
		if type(name) == str: name = name.upper()
		META_REPORT[cols[0]].append(name)
		index = 1
		for elem in user_to_wal_map[userid]:
			show_elem = elem
			if index > 3: show_elem="%.2f" % elem
			META_REPORT[cols[index]].append(show_elem)
			index += 1
	return META_REPORT
	
def getSummaryPlayersReport_all(cols,teamid):
	#cols = ['id','MMR','NK Level','WAL Rank','WAL']
	META_REPORT={}
	all_cards = sortCollection()
	for elem in all_cards:
		cols.append(elem[0]) #Name
	for i in cols: META_REPORT[i]=[]
	user_cards_map, username_map=HELPER_DB.getSummaryCardTableData_all(teamid)
	#user_cards_map = { userid: {cardid : [level,upgrades], ...}, ... }
	#username_map = { userid: [NAME,MMR,NKLEVEL], ... }
	user_to_all_cards_map={}
	wal_rank=[]
	for userid in user_cards_map.keys():
		all_wal=[]
		user_to_all_cards_map[userid]={}
		for elem in all_cards:
			card_id=DATABASE.LOWER_NAME_TO_ID[elem[0].lower()]
			if card_id not in user_cards_map[userid]:
				user_to_all_cards_map[userid][card_id]=0
			else:
				level,upgrades=user_cards_map[userid][card_id]
				min_upgrades,max_upgrades=DATABASE.WAL_MAP[level]
				delta_upgrades=max_upgrades-min_upgrades+1
				level_with_upgrades=level+float(upgrades)/delta_upgrades
				card_wal=level_with_upgrades+getWALOffset(card_id)
				user_to_all_cards_map[userid][card_id]=round(level_with_upgrades,2)
				all_wal.append(card_wal)
		result = 0
		if len(all_wal) > 0:
			result = float(sum(all_wal))/len(all_wal)
		wal_rank.append([userid,round(result,2)])
	sorted_wal_rank = sorted(wal_rank, key=lambda x: (x[1], x[0]), reverse=True)
	wal_rank_num=1
	for userid,all_wal in sorted_wal_rank:
		#cols = ['id','MMR','NK Level','WAL Rank','WAL']
		META_REPORT[cols[0]].append(username_map[userid][0])
		META_REPORT[cols[1]].append(username_map[userid][1])
		META_REPORT[cols[2]].append(username_map[userid][2])
		META_REPORT[cols[3]].append(wal_rank_num)
		wal_rank_num+=1
		META_REPORT[cols[4]].append(all_wal)
		index = 5
		for elem in all_cards:
			card_name = elem[0]
			card_id=DATABASE.LOWER_NAME_TO_ID[card_name.lower()]
			META_REPORT[cols[index]].append(user_to_all_cards_map[userid][card_id])
			index+=1
	return META_REPORT, cols
	
def getMetaReport_cards(cols,rank,mode,search,theme,type,cost,rarity,keyword,lang_index,limit):
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result, updated, total_decks=HELPER_DB.getMetaCardsTableData(search, rank, limit)
	if result == None: return META_REPORT, updated, total_decks
	for elem in result:
		card_id=elem[0]
		percent=elem[1]
		card_name,card_cost,card_type,card_theme,card_rarity,card_keyword=HELPER_DB.getCardDetails(card_id)
		if (cost == 'All' or cost == card_cost) and \
			(theme == 'All' or theme == card_theme) and \
			(type == 'All' or type == card_type) and \
			(rarity == 'All' or rarity == card_rarity) and \
			(keyword == 'All' or keyword in card_keyword):
			CARD_LINK = f'[{card_id}]({SPPDREPLAY}/cards/{card_id})'
			META_REPORT[cols[0]].append(CARD_LINK)
			META_REPORT[cols[1]].append(HELPER.tr(card_name,lang_index))
			META_REPORT[cols[2]].append(percent)
	return META_REPORT, updated, total_decks
	
def getMetaReport_allcards(cols,theme,type,cost,rarity,keyword,lang_index):
	#cols = ['link', 'id', 'cost', 'theme', 'type', 'rarity']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result=HELPER_DB.getAllCardsTableData()
	if result == None: return META_REPORT
	for elem in result:
		card_id=elem[0]
		if card_id == 0: continue
		card_name,card_cost,card_type,card_theme,card_rarity,card_keyword=HELPER_DB.getCardDetails(card_id)
		if (cost == 'All' or cost == card_cost) and \
			(theme == 'All' or theme == card_theme) and \
			(type == 'All' or type == card_type) and \
			(rarity == 'All' or rarity == card_rarity) and \
			(keyword == 'All' or keyword in card_keyword):
			CARD_LINK = f'[{card_id}]({SPPDREPLAY}/cards/{card_id})'
			META_REPORT[cols[0]].append(CARD_LINK)
			META_REPORT[cols[1]].append(HELPER.tr(card_name,lang_index))
			META_REPORT[cols[2]].append(card_cost)
			META_REPORT[cols[3]].append(HELPER.tr(card_theme,lang_index))
			META_REPORT[cols[4]].append(HELPER.tr(card_type,lang_index))
			META_REPORT[cols[5]].append(HELPER.tr(card_rarity,lang_index))
	return META_REPORT
	
def getMetaReport_cardstats(cols,theme,type,cost,rarity,lang_index):
	#cols = ['link', 'id', 'Time Between Attacks', 'Range', 'Base 4-3-2-1','Max 6-5-4-3','Max 7-6-5-4','Lvl 7']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result=HELPER_DB.getMetaCardstatsTableData()
	if result == None: return META_REPORT
	for row in result:
		#ID,NAME,COST,UNIT,TYPE,THEME,RARITY,TBA,RANG,HB1,HM1,HB2,HM2,HB3,HM3,HB4,HM4,HB5,HM5,HB6,HM6,HB7,AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7
		#ID,NAME,COST,TYPE,THEME,RARITY,TBA,RANG,AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7
		card_id,card_name,card_cost,card_units,card_type,card_theme,card_rarity,TBA,RANG = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
		attack_array = [row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21]]
		#	(type == 'All' or type == card_type) and 
		if (cost == 'All' or cost == card_cost) and \
			(theme == 'All' or theme == card_theme) and \
			(type == 'All' or type == card_type) and \
			(rarity == 'All' or rarity == card_rarity):
			CARD_LINK = f'[{card_id}]({SPPDREPLAY}/cards/{card_id})'
			b4321=0
			m6543=0
			m7654=0
			level_seven=0
			if TBA > 0:
				TBA = float(TBA)
				wal_offset = getWALOffset(card_id)
				if wal_offset == -1: continue
				b4321 = int(float(card_units*attack_array[6 - 2*wal_offset]) / TBA)
				m6543 = int(float(card_units*attack_array[11 - 2*wal_offset]) / TBA)
				m7654_offset = -1
				if wal_offset != 0: m7654_offset = 13 - 2*wal_offset
				m7654 = int(float(card_units*attack_array[m7654_offset]) / TBA)
				level_seven = int(float(card_units*attack_array[-1]) / TBA)
			META_REPORT[cols[0]].append(CARD_LINK)
			META_REPORT[cols[1]].append(HELPER.tr(f"{card_name}".upper(),lang_index))
			META_REPORT[cols[2]].append(TBA)
			META_REPORT[cols[3]].append(RANG)
			META_REPORT[cols[4]].append(b4321)
			META_REPORT[cols[5]].append(m6543)
			META_REPORT[cols[6]].append(m7654)
			META_REPORT[cols[7]].append(level_seven)
	return META_REPORT
	
def getMetaReport_carddetails(cols,card_id,lang_index):
	#cols = ['Level', 'Health', 'Attack', 'Damage Per Second']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	row=HELPER_DB.getMetaCardDetailsTableData(card_id)
	if row == None: return META_REPORT
	#ID,NAME,COST,UNITS,TYPE,THEME,RARITY,TBA,RANG,HB1,HM1,HB2,HM2,HB3,HM3,HB4,HM4,HB5,HM5,HB6,HM6,HB7,AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7
	#ID,NAME,COST,UNITS,TYPE,THEME,RARITY,TBA,RANG,AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7
	card_id,card_name,card_cost,card_units,card_type,card_theme,card_rarity,TBA,RANG = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
	health_array = [row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21]]
	attack_array = [row[22],row[23],row[24],row[25],row[26],row[27],row[28],row[29],row[30],row[31],row[32],row[33],row[34]]
	base_string = HELPER.tr('Base',lang_index)
	max_string = HELPER.tr('Max',lang_index)
	TBA = float(TBA)
	for i in range(13):
		level = ''
		if i % 2 == 0: #BASE
			int_level = int((i+2) / 2)
			level=f'{base_string} {int_level}'
		else: #MAX
			int_level = int((i+1) / 2)
			level=f'{max_string} {int_level}'
		health = health_array[i]
		attack = attack_array[i]
		DPS = 0
		if TBA > 0:
			DPS = int(float(card_units*attack) / TBA)
		META_REPORT[cols[0]].append(level)
		META_REPORT[cols[1]].append(health)
		META_REPORT[cols[2]].append(attack)
		META_REPORT[cols[3]].append(DPS)
	return META_REPORT
	
def getMetaReport_carddetails_multiple(card_ids,lang_index):
	double_cols = [['','Level']]
	META_REPORT={}
	for a,b in double_cols: META_REPORT[b]=[]
	base_string = HELPER.tr('Base',lang_index)
	max_string = HELPER.tr('Max',lang_index)
	for i in range(13):
		level = ''
		if i % 2 == 0: #BASE
			int_level = int((i+2) / 2)
			level=f'{base_string} {int_level}'
		else: #MAX
			int_level = int((i+1) / 2)
			level=f'{max_string} {int_level}'
		META_REPORT[double_cols[0][1]].append(level)
	result=HELPER_DB.getMetaCardDetailsTableData_multiple(card_ids)
	if result == None: return META_REPORT,double_cols
	offset = 0
	index = 0
	for row in result:
		#ID,NAME,COST,UNITS,TYPE,THEME,RARITY,TBA,RANG,HB1,HM1,HB2,HM2,HB3,HM3,HB4,HM4,HB5,HM5,HB6,HM6,HB7,AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7
		#ID,NAME,COST,UNITS,TYPE,THEME,RARITY,TBA,RANG,AB1,AM1,AB2,AM2,AB3,AM3,AB4,AM4,AB5,AM5,AB6,AM6,AB7
		card_id,card_name,card_cost,card_units,card_type,card_theme,card_rarity,TBA,RANG = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
		health_array = [row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21]]
		attack_array = [row[22],row[23],row[24],row[25],row[26],row[27],row[28],row[29],row[30],row[31],row[32],row[33],row[34]]
		TBA = float(TBA)
		card_name = HELPER_DB.getCardName(card_id)
		health_str = f'Health{index}'
		attack_str = f'Attack{index}'
		dps_str = f'DPS{index}'
		double_cols.append([card_name,health_str])
		META_REPORT[health_str]=[]
		double_cols.append([card_name,attack_str])
		META_REPORT[attack_str]=[]
		double_cols.append([card_name,dps_str])
		META_REPORT[dps_str]=[]
		
		for i in range(13):
			health = health_array[i]
			attack = attack_array[i]
			DPS = 0
			if TBA > 0:
				DPS = int(float(card_units*attack) / TBA)
			META_REPORT[double_cols[1+offset][1]].append(health)
			META_REPORT[double_cols[2+offset][1]].append(attack)
			META_REPORT[double_cols[3+offset][1]].append(DPS)
		offset+=3
		index+=1
	return META_REPORT,double_cols
	
def getMetaReport_cardfulldetails(card_id,lang_index):
	#cols = ['Level-Upgrade']
	cols=[]
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result=HELPER_DB.getMetaCardFullDetailsTableData(card_id)
	if result == None: return META_REPORT, cols
	is_spell = HELPER_DB.getCardType(int(card_id))=='spell'
	if is_spell:
			cols.append('Level')
			META_REPORT['Level']=[]
	else:
			cols.append('Level-Upgrade')
			META_REPORT['Level-Upgrade']=[]
			cols.append('Health')
			META_REPORT['Health']=[]
			cols.append('Attack')
			META_REPORT['Attack']=[]
	for row in result:
		#LEVEL,UPGRADE,HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2
		LEVEL,UPGRADE,HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2 = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]]
		level_up = f'{LEVEL}'
		if not is_spell:
			level_up+=f'-{UPGRADE}'
			META_REPORT['Health'].append(HEALTH)
			META_REPORT['Attack'].append(ATTACK)
		META_REPORT[cols[0]].append(level_up)
			
		if STYPE1 != None:
			if STYPE1 in DATABASE.CARD_ABILITIES: STYPE1 = DATABASE.CARD_ABILITIES[STYPE1]
			if STYPE1 not in cols:
				cols.append(STYPE1)
				META_REPORT[STYPE1]=[]
			META_REPORT[STYPE1].append(SPECIAL1)
			
		if STYPE2 != None:
			if STYPE2 in DATABASE.CARD_ABILITIES: STYPE2 = DATABASE.CARD_ABILITIES[STYPE2]
			if STYPE2 not in cols:
				cols.append(STYPE2)
				META_REPORT[STYPE2]=[]
			META_REPORT[STYPE2].append(SPECIAL2)
			
	return META_REPORT, cols
	
def getMetaReport_cardfulldetails_multiple(card_ids,lang_index):
	double_cols = [['','Level-Upgrade']]
	#double_cols = [['','Level-Upgrade'], ['CARD1','Health'], ['CARD1','Attack']]
	META_REPORT={}
	for i in double_cols: META_REPORT[i[1]]=[]
	result=HELPER_DB.getMetaCardFullDetailsTableData_multiple(card_ids)
	if result == None: return META_REPORT, double_cols
	ALL_CARD_STATS={} # { '1-1' : {1234: [a,b,c], 2345: [x,y,x]}, ... }
	CARD_COLS={} # {1234: [a,b,c], 2345: [x,y,x]}
	for row in result:
		#CARDID,LEVEL,UPGRADE,HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2
		CARDID,LEVEL,UPGRADE,HEALTH,ATTACK,SPECIAL1,STYPE1,SPECIAL2,STYPE2 = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
		level_up = f'{LEVEL}-{UPGRADE}'
		if level_up not in ALL_CARD_STATS: ALL_CARD_STATS[level_up]={}
		if CARDID not in ALL_CARD_STATS[level_up]: ALL_CARD_STATS[level_up][CARDID]=[]
		if CARDID not in CARD_COLS: CARD_COLS[CARDID]=[]
		ALL_CARD_STATS[level_up][CARDID].append(HEALTH)
		ALL_CARD_STATS[level_up][CARDID].append(ATTACK)
		if STYPE1 != None:
			if STYPE1 in DATABASE.CARD_ABILITIES: STYPE1 = DATABASE.CARD_ABILITIES[STYPE1]
			if STYPE1 not in CARD_COLS[CARDID]:
				CARD_COLS[CARDID].append(STYPE1)
			ALL_CARD_STATS[level_up][CARDID].append(SPECIAL1)
			
		if STYPE2 != None:
			if STYPE2 in DATABASE.CARD_ABILITIES: STYPE2 = DATABASE.CARD_ABILITIES[STYPE2]
			if STYPE2 not in CARD_COLS[CARDID]:
				CARD_COLS[CARDID].append(STYPE2)
			ALL_CARD_STATS[level_up][CARDID].append(SPECIAL2)
	index = 1
	for cardid in CARD_COLS:
		card_name = HELPER_DB.getCardName(cardid)
		health_str = f'Health{index}'
		META_REPORT[health_str]=[]
		double_cols.append([card_name,health_str])
		attack_str = f'Attack{index}'
		META_REPORT[attack_str]=[]
		double_cols.append([card_name,attack_str])
		for i in CARD_COLS[cardid]:
			special_str = f'{i}{index}'
			META_REPORT[special_str]=[]
			double_cols.append([card_name,special_str])
		index+=1
	
	count = 0
	for level_up in ALL_CARD_STATS:
		index = 0
		META_REPORT[double_cols[index][1]].append(level_up)
		index+=1
		tmp_count = 0
		for cardid in ALL_CARD_STATS[level_up]:
			for elem in ALL_CARD_STATS[level_up][cardid]:
				META_REPORT[double_cols[index][1]].append(elem)
				index+=1
				tmp_count+=1
		if tmp_count > count: count = tmp_count
		while tmp_count < count:
			META_REPORT[double_cols[index][1]].append(0)
			tmp_count+=1
			index+=1
	return META_REPORT, double_cols
	
def getMetaReport_cardwinrate(cols,card_id,lang_index):
	#cols = ["Opponent's Card", 'You Win', 'You Draw', 'You Lose']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result=HELPER_DB.getWinRateCardsTableData(card_id)
	if result == None: return META_REPORT
	#CARDID2,WIN,DRAW,LOSE
	for row in result:
		CARDID2,WIN,DRAW,LOSE = [row[0],row[1],row[2],row[3]]
		cardname='**TOTAL**'
		if CARDID2 != None:
			cardname = HELPER_DB.getCardName(CARDID2)
			cardname = HELPER.tr(cardname,lang_index)
		META_REPORT[cols[0]].append(cardname)
		META_REPORT[cols[1]].append(WIN)
		META_REPORT[cols[2]].append(DRAW)
		META_REPORT[cols[3]].append(LOSE)
	return META_REPORT
	
def getMetaReport_chal_cards(cols,chal_id,lindex):
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result, updated, total_decks=HELPER_DB.getMetaChalCardsTableData(chal_id)
	if result == None: return META_REPORT, updated, total_decks
	for elem in result:
		card_id=elem[0]
		percent=elem[1]
		card_name = "Unknown..."
		if card_id in DATABASE.DECK_MAP:
			card_name = DATABASE.DECK_MAP[card_id][0]
			if type(card_name) == str: card_name=card_name.upper()
		card_name = HELPER.tr(card_name, lindex)
		CARD_LINK = f'[{card_id}]({SPPDREPLAY}/cards/{card_id})'
		META_REPORT[cols[0]].append(CARD_LINK)
		META_REPORT[cols[1]].append(card_name)
		META_REPORT[cols[2]].append(percent)
	return META_REPORT, updated, total_decks
	
def getMetaReport_tw_cards(cols,eventid,league,lang_index):
	meta_deck = []
	#cols = ['Choice 1', 'Percent 1', 'Choice 2', 'Percent 2', 'Unknown']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result, total_decks=HELPER_DB.getMetaTWCardsTableData(eventid,league)
	if result == None: return META_REPORT, total_decks, meta_deck
	for CHOICE1,COUNT1,CHOICE2,COUNT2 in result:
		card_name = "Unknown..."
		if CHOICE1 in DATABASE.DECK_MAP:
			card_name = DATABASE.DECK_MAP[CHOICE1][0]
			if type(card_name) == str: card_name=card_name.upper()
		META_REPORT[cols[0]].append(HELPER.tr(card_name,lang_index))
		percent = int(100 * COUNT1 / total_decks)
		META_REPORT[cols[1]].append(percent)
		card_name = "Unknown..."
		if CHOICE2 in DATABASE.DECK_MAP:
			card_name = DATABASE.DECK_MAP[CHOICE2][0]
			if type(card_name) == str: card_name=card_name.upper()
		META_REPORT[cols[2]].append(HELPER.tr(card_name,lang_index))
		percent = int(100 * COUNT2 / total_decks)
		META_REPORT[cols[3]].append(percent)
		percent = int(100 * (total_decks - (COUNT1+COUNT2)) / total_decks)
		META_REPORT[cols[4]].append(percent)
		HIGH_CHOICE = CHOICE1
		if COUNT1 < COUNT2: HIGH_CHOICE = CHOICE2
		meta_deck.append(HIGH_CHOICE)
	return META_REPORT, total_decks, meta_deck
	
def getMetaReport_twmeta_cards(cols,eventid,league,lang_index):
	meta_deck = []
	#cols = ['Choice 1', 'AVG SCORE 1 ', 'Choice 2', 'AVG SCORE 2', 'Best Choice', 'Difference']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result=HELPER_DB.getWinRateTVTByCard(eventid,league)
	if result == None: return META_REPORT, meta_deck
	for CHOICE1,AVG1,CHOICE2,AVG2 in result:
		BEST_CHOICE = "Unknown..."
		DIFFERENCE = 0
		card_name = "Unknown..."
		if CHOICE1 in DATABASE.DECK_MAP:
			card_name = DATABASE.DECK_MAP[CHOICE1][0]
			if type(card_name) == str: card_name=card_name.upper()
			BEST_CHOICE = card_name
			DIFFERENCE = AVG1-AVG2
		META_REPORT[cols[0]].append(HELPER.tr(card_name,lang_index))
		META_REPORT[cols[1]].append(round(AVG1,1))
		card_name = "Unknown..."
		if CHOICE2 in DATABASE.DECK_MAP:
			card_name = DATABASE.DECK_MAP[CHOICE2][0]
			if type(card_name) == str: card_name=card_name.upper()
			if AVG2 > AVG1:
				BEST_CHOICE = card_name
				DIFFERENCE = AVG2-AVG1
		META_REPORT[cols[2]].append(HELPER.tr(card_name,lang_index))
		META_REPORT[cols[3]].append(round(AVG2,1))
		META_REPORT[cols[4]].append(BEST_CHOICE)
		META_REPORT[cols[5]].append(round(DIFFERENCE,1))
		HIGH_CHOICE = CHOICE1
		if AVG1 < AVG2: HIGH_CHOICE = CHOICE2
		meta_deck.append(HIGH_CHOICE)
	return META_REPORT, meta_deck
	
def getMetaReport_themes(cols,rank,search,lang_index):
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result, updated, total_decks=HELPER_DB.getMetaThemesTableData(search, rank)
	if result == None: return META_REPORT, updated, total_decks
	for elem in result:
		theme_str=elem[0]
		percent=elem[1]
		if cols[0] not in META_REPORT:
			META_REPORT[cols[0]]=[]
		if cols[1] not in META_REPORT:
			META_REPORT[cols[1]]=[]
		META_REPORT[cols[0]].append(HELPER.tr(theme_str,lang_index))
		META_REPORT[cols[1]].append(percent)
	return META_REPORT, updated, total_decks
	
def getMetaReport_decks(rank,lang_index):
	META_DECKS=[]
	graph_data=[]
	result, updated, total_decks, deckid_map, cost_data=HELPER_DB.getMetaDecksData(rank)
	if result == None: return META_DECKS, updated, total_decks, graph_data
	if deckid_map == None: return META_DECKS, updated, total_decks, graph_data
	for elem in result:
		theme_str=HELPER.tr(elem[0],lang_index)
		percent=elem[1]
		deckid=elem[2]
		if deckid != None and deckid in deckid_map:
			array_of_cards=deckid_map[deckid]
			META_DECKS.append([theme_str,percent,array_of_cards])
	if cost_data != None:
		if type(cost_data) == tuple: cost_data = [cost_data]
		for row in cost_data:
			cost = row[0]
			total = row[1]
			graph_data.append({'x': [cost], 'y': [total]})
	return META_DECKS, updated, total_decks, graph_data
	
def getMetaReport_chal_decks(chal_id):
	META_DECKS=[]
	result, deckid_map=HELPER_DB.getMetaChalDecksData(chal_id)
	if result == None: return META_DECKS
	if deckid_map == None: return META_DECKS
	for elem in result:
		theme_str=elem[0]
		percent=elem[1]
		deckid=elem[2]
		if deckid != None and deckid in deckid_map:
			array_of_cards=deckid_map[deckid]
			META_DECKS.append([theme_str,percent,array_of_cards])
	return META_DECKS
	
def getTeamMembersReport(cols,team_id,access_level=-1):
	#cols = ['id', 'Name', 'MMR', 'NK Level', 'Donated', 'Role', 'Join Date', 'Collection']
	graph_data=[]
	pie_chart=[]
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	members_map={}
	team_table_data,collection_map=HELPER_DB.getTeamDetailsTableData(team_id,access_level)
	if team_table_data == None:
		return META_REPORT, graph_data, pie_chart
	platforms=[0,0] #iOS, Android
	for row in team_table_data:
		#y.ID, y.NAME, y.PLATFORM, x.ROLE, x.MMR, x.NKLEVEL, x.DONATED_CUR, x.JOINDATE
		if row != None:
			user_id = row[0]
			name = row[1]
			PLATFORM = row[2]
			role = row[3]
			mmr = row[4]
			nklevel = row[5]
			donated = row[6]
			joindate = row[7]
			if type(name) == str: name=name.upper()
			members_map[user_id]=[role,mmr,nklevel,donated,joindate,name]
			#role, mmr, nklevel, donated, joindate, #NAME#
			graph_data.append({'x': [mmr], 'y': [nklevel]})
			if "gamecenter" == PLATFORM: platforms[0]+=1
			elif "google" == PLATFORM: platforms[1]+=1
	pie_chart.append({'labels': ["iOS", "Android"], 'values': platforms, 'type': 'pie'})
	for key in members_map.keys():
		member_details=members_map[key]
		for column_name in cols:
			target="unknown"
			if column_name == 'id': target=f'[{key}]({SPPDREPLAY}/player/{key})'
			elif column_name == 'Name': target = member_details[5]
			elif column_name == 'Role': target = member_details[0]
			elif column_name == 'MMR': target = member_details[1]
			elif column_name == 'NK Level': target = member_details[2]
			elif column_name == 'Donated': target = member_details[3]
			elif column_name == 'Join Date': target = member_details[4]
			elif column_name == 'Collection':
				target="N/A"
				if access_level!=-1:
					target=0
					if key in collection_map:
						target=collection_map[key]
			META_REPORT[column_name].append(target)
	return META_REPORT, graph_data, pie_chart
	
def getMyMatchesReport(cols,g_user,gmtOffset):
	#cols = ['id', 'Time', 'Name', 'Team', 'Mode', 'Score', 'MMR']
	win_pie=[]
	nk_pie=[]
	score_pie=[]
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	matches_map={}
	mymatches_table_data,oppname_map,oppteam_map=HELPER_DB.getMyMatchesTableData(g_user)
	if mymatches_table_data == None:
		return META_REPORT,win_pie,nk_pie,score_pie
	win_vals=[0,0,0] #Win, Loss, Draw
	nk_vals=[0] * 25 #1-25
	score_vals=[0,0,0,0] #0,1,2,3
	for row in mymatches_table_data:
		ID = row[0]
		TIME = row[1]
		USERID2 = row[2]
		NK2 = row[3]
		TEAM2 = row[4]
		MODE = row[5]
		RESULT1 = row[6]
		SCORE1 = row[7]
		SCORE2 = row[8]
		MMR = row[9]
		unique_user_id=""
		for column_name in cols:
			if column_name == 'id':
				match_link=f'[{ID}]({SPPDREPLAY}/match/{ID})'
				META_REPORT[column_name].append(match_link)
			elif column_name == 'Time':
				TIME = TIME - gmtOffset*60
				start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(TIME))
				META_REPORT[column_name].append(start_pretty)
			elif column_name == 'Name':
				tmp_name="Unknown..."
				if USERID2 in oppname_map:
					unique_user_id,user_name = oppname_map[USERID2]
					if type(user_name) == str: user_name = user_name.upper()
					tmp_name=f'[{user_name}]({SPPDREPLAY}/player/{unique_user_id})'
				META_REPORT[column_name].append(tmp_name)
			elif column_name == 'Team':
				team_name = "Unknown..."
				if TEAM2 in oppteam_map: team_name = oppteam_map[TEAM2]
				if type(team_name) == str: team_name = team_name.upper()
				META_REPORT[column_name].append(team_name)
			elif column_name == 'Mode':
				mode="Unknown..."
				if MODE == 1: mode="PVP"
				elif MODE == 5: mode="FF"
				elif MODE == 6: mode="Challenge"
				elif MODE == 7: mode="TVT"
				elif MODE == 0: mode="PVE"
				META_REPORT[column_name].append(mode)
			elif column_name == 'Score':
				META_REPORT[column_name].append(f'{SCORE1}:{SCORE2}')
			elif column_name == 'MMR':
				META_REPORT[column_name].append(MMR)
		#Win Rate
		w_index=2 #DRAW
		if RESULT1==1: #WIN
			w_index=0
		elif RESULT1==0: #LOSS
			w_index=1
		win_vals[w_index]+=1
		#Opponent's NK Level
		if NK2 > 0: nk_vals[NK2-1]+=1
		#Phones Destroyed Per Match
		score_vals[SCORE1]+=1
	nk_labels = [x for x in range(1,26)]
	index = 0
	while index < len(nk_vals):
		if nk_vals[index] == 0:
			nk_vals.pop(index)
			nk_labels.pop(index)
		else: index +=1
	win_pie.append({'labels': ["Win", "Loss", "Draw"], 'values': win_vals, 'type': 'pie'})
	nk_pie.append({'labels': nk_labels, 'values': nk_vals, 'type': 'pie'})
	score_pie.append({'labels': [0,1,2,3], 'values': score_vals, 'type': 'pie'})
	return META_REPORT,win_pie,nk_pie,score_pie
	
def getSpecificPlayerMatchesReport(cols,unique_user_id,gmtOffset):
	#cols = ['id', 'Time', 'Name', 'Team', 'Mode', 'Score', 'MMR']
	win_pie=[]
	nk_pie=[]
	score_pie=[]
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	matches_map={}
	mymatches_table_data=HELPER_DB.getSpecificPlayerMatchesTableData(unique_user_id)
	if mymatches_table_data == None:
		return META_REPORT,win_pie,nk_pie,score_pie
	win_vals=[0,0,0] #Win, Loss, Draw
	nk_vals=[0] * 25 #1-25
	score_vals=[0,0,0,0] #0,1,2,3
	for row in mymatches_table_data:
		MATCHID, TIME, PLAYERID, PLAYERNAME, NK2, TEAMNAME, MODE, RESULT1, SCORE1, SCORE2, MMR2 = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]]
		MATCHID = f'[{MATCHID}]({SPPDREPLAY}/match/{MATCHID})'
		TIME = TIME - gmtOffset*60
		start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(TIME))
		if type(PLAYERNAME)==str: PLAYERNAME = PLAYERNAME.upper()
		if type(TEAMNAME)==str: TEAMNAME = TEAMNAME.upper()
		PLAYERNAME=f'[{PLAYERNAME}]({SPPDREPLAY}/player/{PLAYERID})'
		mode="Unknown..."
		if MODE == 1: mode="PVP"
		elif MODE == 5: mode="FF"
		elif MODE == 6: mode="Challenge"
		elif MODE == 7: mode="TVT"
		elif MODE == 0: mode="PVE"
		table_data = [MATCHID,start_pretty,PLAYERNAME,TEAMNAME,mode,f'{SCORE1}:{SCORE2}',MMR2] #'Score', 'MMR']
		index=0
		for i in cols:
			META_REPORT[i].append(table_data[index])
			index+=1
		#Win Rate
		w_index=2 #DRAW
		if RESULT1==1: #WIN
			w_index=0
		elif RESULT1==0: #LOSS
			w_index=1
		win_vals[w_index]+=1
		#Opponent's NK Level
		if NK2 > 0: nk_vals[NK2-1]+=1
		#Phones Destroyed Per Match
		score_vals[SCORE1]+=1
	nk_labels = [x for x in range(1,26)]
	index = 0
	while index < len(nk_vals):
		if nk_vals[index] == 0:
			nk_vals.pop(index)
			nk_labels.pop(index)
		else: index +=1
	win_pie.append({'labels': ["Win", "Loss", "Draw"], 'values': win_vals, 'type': 'pie'})
	nk_pie.append({'labels': nk_labels, 'values': nk_vals, 'type': 'pie'})
	score_pie.append({'labels': [0,1,2,3], 'values': score_vals, 'type': 'pie'})
	return META_REPORT,win_pie,nk_pie,score_pie
	
def getLiveMatchesReport(cols,rank,mode,gmtOffset):
	#cols = ['id', 'Time', 'MMR1', 'NK1', 'MMR2', 'NK2', 'Mode', 'Score']
	QUERY=''
	if rank != "All":
		if rank == '8500+':
			QUERY='WHERE (MMR1 >= 8500 OR MMR2 >= 8500)'
		else:
			for i in range(8500, 0, -1000):
				min_rank=i-1000
				if rank == f'{min_rank}-{i}':
					QUERY=f'WHERE ((MMR1 >= {min_rank} AND MMR1 < {i}) OR (MMR2 >= {min_rank} AND MMR2 < {i}))'
					break
	if mode != "All":
		if QUERY=='': QUERY='WHERE MODE = '
		else: QUERY+=' AND MODE = '
		if mode == 'Ranked': QUERY+='1'
		elif mode == 'Challenge': QUERY+='6'
		elif mode == 'Friendly Fight': QUERY+='5'
		elif mode == 'Team Wars': QUERY+='7'
		else: QUERY = ''
	win_pie=[]
	nk_pie=[]
	score_pie=[]
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	live_matches_table_data=HELPER_DB.getLiveMatchesTableData(QUERY)
	if live_matches_table_data == None:
		return META_REPORT,win_pie,nk_pie,score_pie
	win_vals=[0,0,0] #Win, Loss, Draw
	nk_vals=[0] * 25 #1-25
	score_vals=[0,0,0,0] #0,1,2,3
	for row in live_matches_table_data:
		ID = row[0]
		TIME = row[1]
		MMR1 = row[2]
		NK1 = row[3]
		MMR2 = row[4]
		NK2 = row[5]
		MODE = row[6]
		SCORE1 = row[7]
		SCORE2 = row[8]
		RESULT1 = row[9]
		unique_user_id=""
		for column_name in cols:
			if column_name == 'id':
				match_link=f'[{ID}]({SPPDREPLAY}/match/{ID})'
				META_REPORT[column_name].append(match_link)
			elif column_name == 'Time':
				TIME = TIME - gmtOffset*60
				start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(TIME))
				META_REPORT[column_name].append(start_pretty)
			elif column_name == 'MMR1':
				META_REPORT[column_name].append(MMR1)
			elif column_name == 'NK1':
				META_REPORT[column_name].append(NK1)
			elif column_name == 'MMR2':
				META_REPORT[column_name].append(MMR2)
			elif column_name == 'NK2':
				META_REPORT[column_name].append(NK2)
			elif column_name == 'Mode':
				mode="Unknown..."
				if MODE == 1: mode="PVP"
				elif MODE == 5: mode="FF"
				elif MODE == 6: mode="Challenge"
				elif MODE == 7: mode="TVT"
				elif MODE == 0: mode="PVE"
				META_REPORT[column_name].append(mode)
			elif column_name == 'Score':
				META_REPORT[column_name].append(f'{SCORE1}:{SCORE2}')
		#Win Rate
		w_index=2 #DRAW
		if RESULT1==1: #WIN
			w_index=0
		elif RESULT1==0: #LOSS
			w_index=1
		win_vals[w_index]+=1
		#Opponent's NK Level
		if NK2 > 0: nk_vals[NK2-1]+=1
		#Phones Destroyed Per Match
		score_vals[SCORE1]+=1
	nk_labels = [x for x in range(1,26)]
	index = 0
	while index < len(nk_vals):
		if nk_vals[index] == 0:
			nk_vals.pop(index)
			nk_labels.pop(index)
		else: index +=1
	win_pie.append({'labels': ["Win", "Loss", "Draw"], 'values': win_vals, 'type': 'pie'})
	nk_pie.append({'labels': nk_labels, 'values': nk_vals, 'type': 'pie'})
	score_pie.append({'labels': [0,1,2,3], 'values': score_vals, 'type': 'pie'})
	return META_REPORT,win_pie,nk_pie,score_pie
	
def getTeamwarsReport(cols,gmtOffset):
	#cols = ['id', 'Upgrade Days', 'Name']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	tw_table_data=HELPER_DB.getTeamwarsTableData()
	if tw_table_data == None:
		return META_REPORT
	for row in tw_table_data:
		ID = row[0]
		TIME = row[1]
		NAME = row[2]
		tw_link=f'[{ID}]({SPPDREPLAY}/teamwars/{ID})'
		META_REPORT[cols[0]].append(tw_link)
		TIME = TIME - gmtOffset*60
		start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(TIME))
		META_REPORT[cols[1]].append(start_pretty)
		META_REPORT[cols[2]].append(NAME)
	return META_REPORT
	
def getTWMetaReport(cols,gmtOffset):
	#cols = ['id', 'Upgrade Days', 'Name']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	tw_table_data=HELPER_DB.getTeamwarsTableData()
	if tw_table_data == None:
		return META_REPORT
	for row in tw_table_data:
		ID = row[0]
		TIME = row[1]
		NAME = row[2]
		tw_link=f'[{ID}]({SPPDREPLAY}/twmeta/{ID})'
		META_REPORT[cols[0]].append(tw_link)
		TIME = TIME - gmtOffset*60
		start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(TIME))
		META_REPORT[cols[1]].append(start_pretty)
		META_REPORT[cols[2]].append(NAME)
	return META_REPORT
	
def getChallengesReport(cols,rank,gmtOffset,lang_index):
	#cols = ['id', 'Time', 'Challenge']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	chal_table_data=HELPER_DB.getChalTableData()
	if chal_table_data == None:
		return META_REPORT
	for row in chal_table_data:
		ID = row[0]
		TIME = row[1]
		NAME = row[2]
		NAME = HELPER.tr(NAME, lang_index)
		chal_link=f'[{ID}]({SPPDREPLAY}/challenge/{ID})'
		META_REPORT[cols[0]].append(chal_link)
		TIME = TIME - gmtOffset*60
		start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(TIME))
		META_REPORT[cols[1]].append(start_pretty)
		META_REPORT[cols[2]].append(NAME)
	return META_REPORT
	
def getTeamApplicationsReport(cols,team_id,access_level=-1):
	#cols = ['id', 'name', 'status', 'role']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	#ingame_team_id=HELPER_DB.getInGameTeamID(team_id)
	if team_id == None: return META_REPORT
	members_map={}
	team_members,_=HELPER_DB.getTeamDetailsTableData(team_id)
	team_applications=HELPER_DB.getTeamApplicationsTableData(team_id,access_level)
	if team_members == None: return META_REPORT
	#USERID, STATUS, ROLE
	for row in team_members:
		#y.ID, y.NAME, y.PLATFORM, x.ROLE, x.MMR, x.NKLEVEL, x.DONATED_CUR, x.JOINDATE
		user_id = row[0]
		name = row[1]
		if type(name) == str: name = name.upper()
		role = row[3]
		members_map[user_id]=['ignore', role, name]
	if team_applications == None: team_applications=[]
	for row in team_applications:
		user_id = row[0]
		name = row[1]
		if type(name) == str: name = name.upper()
		status = row[2]
		role = row[3]
		members_map[user_id]=[status,role,name]
	for key in members_map.keys():
		member_details=members_map[key]
		META_REPORT[cols[0]].append(f'[{key}]({SPPDREPLAY}/player/{key})') #Link
		META_REPORT[cols[1]].append(member_details[2]) #Name
		META_REPORT[cols[2]].append(member_details[0]) #Status
		META_REPORT[cols[3]].append(member_details[1]) #Role
	return META_REPORT
	
def getCardRequestReport(cols,team_id,access_level=-1):
	max_updated=-1
	#cols = ['Created', 'Player', 'Card']
	META_REPORT={}
	card_pie=[]
	for i in cols: META_REPORT[i]=[]
	ingame_team_id=HELPER_DB.getInGameTeamID(team_id)
	if ingame_team_id==None: return META_DECKS, max_updated,card_pie
	request_table_data=HELPER_DB.getCardRequestTableData(ingame_team_id,access_level)
	if request_table_data == None: return META_REPORT, max_updated,card_pie
	graph_data = {}
	usernames_map = HELPER_DB.getAllUserNames(ingame_team_id)
	for row in request_table_data:
		if row != None:
			created = row[0]
			if max_updated < created: max_updated=created
			userid = row[1]
			card = row[2]
			username="Unknown-"+userid[:4]
			if userid in usernames_map:
				username=usernames_map[userid]
			cardname = HELPER_DB.getCardName(card)
			created_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(created))
			META_REPORT[cols[0]].append(created_pretty)
			META_REPORT[cols[1]].append(username)
			META_REPORT[cols[2]].append(cardname)
			if cardname not in graph_data:
				graph_data[cardname] = 0
			graph_data[cardname] += 1
	more_data = [[key,value] for key,value in graph_data.items()]
	sorted_l = sorted(more_data, key=lambda x: (x[1], x[0]), reverse=True)
	card_labels=[]
	card_vals=[]
	for i in range(min(10,len(sorted_l))):
		key,value = sorted_l[i]
		card_labels.append(key)
		card_vals.append(value)
	card_pie.append({'labels': card_labels, 'values': card_vals, 'type': 'pie'})
	return META_REPORT, max_updated,card_pie
	
def getCardDonationReport(cols,team_id,access_level=-1):
	max_updated=-1
	#cols = ['Created', 'Sender', 'Receiver', 'Card']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	ingame_team_id=HELPER_DB.getInGameTeamID(team_id)
	if ingame_team_id==None: return META_DECKS, max_updated
	donation_table_data=HELPER_DB.getCardDonationTableData(ingame_team_id,access_level)
	if donation_table_data == None: return META_REPORT, max_updated
	usernames_map = HELPER_DB.getAllUserNames(ingame_team_id)
	for row in donation_table_data:
		if row != None:
			created = row[0]
			if max_updated < created: max_updated=created
			receiver = row[1]
			sender = row[2]
			card = row[3]
			receiver_name="Unknown-"+receiver[:4]
			if receiver in usernames_map:
				receiver_name=usernames_map[receiver]
			sender_name="Unknown-"+sender[:4]
			if sender in usernames_map:
				sender_name=usernames_map[sender]
			cardname = HELPER_DB.getCardName(card)
			created_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(created))
			META_REPORT[cols[0]].append(created_pretty)
			META_REPORT[cols[1]].append(sender_name)
			META_REPORT[cols[2]].append(receiver_name)
			META_REPORT[cols[3]].append(cardname)
	return META_REPORT, max_updated
	
def getCardSummaryHistoryReport(team_id):
	cols=['id','ratio','r7com','r7rar','r7epi','r30com','r30rar','r30epi',
		'd7com','d7rar','d7epi','d30com','d30rar','d30epi']
	max_updated=-1
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	ingame_team_id=HELPER_DB.getInGameTeamID(team_id)
	if ingame_team_id==None: return META_DECKS, max_updated
	# { userid : ['r7com','r7rar','r7epi','r30com','r30rar','r30epi',
	#	'd7com','d7rar','d7epi','d30com','d30rar','d30epi'], ...}
	card_summary_map={}
	for i in range(4):
		table_data=None
		if i == 0:
			table_data=HELPER_DB.getCardRequestTableDataTime(ingame_team_id,7)
		elif i == 1:
			table_data=HELPER_DB.getCardRequestTableDataTime(ingame_team_id,30)
		elif i == 2:
			table_data=HELPER_DB.getCardDonationTableDataTime(ingame_team_id,7)
		elif i == 3:
			table_data=HELPER_DB.getCardDonationTableDataTime(ingame_team_id,30)
		if table_data == None: return META_REPORT, max_updated
		for row in table_data:
			index=3*i
			if row != None:
				if i < 2:
					created = row[0]
					if max_updated < created: max_updated=created
					userid = row[1]
					if userid not in card_summary_map:
						card_summary_map[userid] = [0,0,0,0,0,0,0,0,0,0,0,0]
					card = row[2]
					offset=getWALOffset(card)
					index += offset
					amount = 1
					if offset == 0: #common
						amount=12
					elif offset == 1: #rare
						amount=3
					card_summary_map[userid][index]+=amount
				else:
					created = row[0]
					if max_updated < created: max_updated=created
					receiver = row[1]
					sender = row[2]
					card = row[3]
					if sender not in card_summary_map:
						card_summary_map[sender] = [0,0,0,0,0,0,0,0,0,0,0,0]
					offset=getWALOffset(card)
					index += offset
					card_summary_map[sender][index]+=1
					
	usernames_map = HELPER_DB.getAllUserNames(ingame_team_id)
	for userid in card_summary_map.keys():
		username="Unknown-"+userid[:4]
		if userid in usernames_map:
			username=usernames_map[userid]
		META_REPORT[cols[0]].append(username)
		donations = (
			float(card_summary_map[userid][9])/12 +
			float(card_summary_map[userid][10])/3 +
			float(card_summary_map[userid][11])
			)
		requests = (
			float(card_summary_map[userid][3])/12 +
			float(card_summary_map[userid][4])/3 +
			float(card_summary_map[userid][5])
			)
		result = -1
		if requests > 0: result = donations / requests
		donation_request_ratio = "%.2f" % result
		META_REPORT[cols[1]].append(donation_request_ratio)
		for i in range(12):
			META_REPORT[cols[i+2]].append(card_summary_map[userid][i])
	return META_REPORT, max_updated

def getWALOffset(id):
	if id in DATABASE.DECK_MAP:
		if "leg" in DATABASE.DECK_MAP[id]: return 3
		if "epi" in DATABASE.DECK_MAP[id]: return 2
		if "rar" in DATABASE.DECK_MAP[id]: return 1
		if "com" in DATABASE.DECK_MAP[id]: return 0
	else:
		result = HELPER_DB.getCardData(id)
		if result == None: return -1
		RARITY=result[4]
		if "leg" == RARITY: return 3
		if "epi" == RARITY: return 2
		if "rar" == RARITY: return 1
		if "com" == RARITY: return 0
	return -1
	
def getCapsByCardLevel(cardid,level):
	rarity="com"
	if cardid in DATABASE.DECK_MAP:
		rarity=DATABASE.DECK_MAP[cardid][4]
	return DATABASE.CAPS_PER_RARITY[rarity][level-1] #Arrays start at 0
	
def getCardLevelByCaps(cardid,caps):
	rarity="com"
	if cardid in DATABASE.DECK_MAP:
		rarity=DATABASE.DECK_MAP[cardid][4]
	prev_caps = 0
	next_caps = 0
	level=0
	for req_caps in DATABASE.CAPS_PER_RARITY[rarity]:
		if req_caps > caps:
			next_caps=req_caps
			break
		prev_caps=req_caps
		level+=1
	if level == 7: next_caps=prev_caps
	return level,next_caps,prev_caps
	
def isSpellCard(card_id):
	return card_id in DATABASE.DECK_MAP and ("spell" in DATABASE.DECK_MAP[card_id] or "tower" in DATABASE.DECK_MAP[card_id])

def getCardComparisonReport(cols,team_id):
	#cols = ['Choice', 'id', 'WAL', 'Avg Level', '+1FF', '+2FF', '+3FF', '+4FF', Leader Vote, Target Level, Caps]
	META_REPORT={}
	restricted_levels=[]
	for i in cols: META_REPORT[i]=[]
	cards_map={}
	ordered_cards, card_comparison, leader_choice=HELPER_DB.getCardComparisonTableData(team_id)
	process_card_data={}
	if card_comparison != None:
		for card_data in card_comparison:
			# CARDID, LEVEL, UPGRADES
			CARDID=card_data[0]
			LEVEL=card_data[1]
			UPGRADES=card_data[2]
			min_upgrades,max_upgrades=DATABASE.WAL_MAP[LEVEL]
			delta_upgrades=max_upgrades-min_upgrades+1
			WAL=LEVEL+(float(UPGRADES)/delta_upgrades)+getWALOffset(CARDID)
			AVG=LEVEL+(float(UPGRADES)/delta_upgrades)
			PLUS1FF=0
			PLUS2FF=0
			PLUS3FF=0
			PLUS4FF=0
			is_spell = isSpellCard(CARDID)
			if (is_spell and WAL > 7) or (not is_spell and WAL >= 7):
				PLUS4FF=1
			if (is_spell and WAL > 6) or (not is_spell and WAL >= 6):
				PLUS3FF=1
			if (is_spell and WAL > 5) or (not is_spell and WAL >= 5):
				PLUS2FF=1
			if (is_spell and WAL > 4) or (not is_spell and WAL >= 4):
				PLUS1FF=1
			if CARDID not in process_card_data:
				process_card_data[CARDID]=[[],[],0,0,0,0] #'WAL', 'Avg Level', '+1FF', '', '', ''
			process_card_data[CARDID][0].append(WAL) #WAL
			process_card_data[CARDID][1].append(AVG) #AVG Level
			process_card_data[CARDID][2]+=PLUS1FF #+1FF
			process_card_data[CARDID][3]+=PLUS2FF #+2FF
			process_card_data[CARDID][4]+=PLUS3FF #+3FF
			process_card_data[CARDID][5]+=PLUS4FF #+4FF
	leader_choice_data={}
	if leader_choice != None:
		for row in leader_choice: #CARDID, VOTE, LEVEL
			CARDID=row[0]
			VOTE=int(row[1])
			LEVEL=row[2] #Arrays start at 0
			leader_choice_data[CARDID]=[VOTE,LEVEL]
	choices=1
	index=0
	WAL=[]
	total_caps=0
	for card in ordered_cards:
		if card not in process_card_data:
			process_card_data[card]=[[0],[0],0,0,0,0] #'WAL', 'Avg Level', '+1FF', '', '', ''
		card_name=HELPER_DB.getCardName(card).upper()
		this_cards_target_level=4-getWALOffset(card)
		restricted_levels.append([card_name,this_cards_target_level])
		card_data=[0,0]
		if card in leader_choice_data:
			card_data=leader_choice_data[card]
		for column_name in cols:
			if column_name == 'id':
				META_REPORT[column_name].append(card_name)
			elif column_name == 'Choice':
				META_REPORT[column_name].append(choices)
			elif column_name == 'WAL':
				data=process_card_data[card][0]
				raw_avg=float(sum(data)/len(data))
				avg="%.2f" % raw_avg
				META_REPORT[column_name].append(avg)
				if card_data[0] == 1:
					WAL.append(raw_avg)
			elif column_name == 'Avg Level':
				data=process_card_data[card][1]
				avg="%.2f" % float(sum(data)/len(data))
				META_REPORT[column_name].append(avg)
			elif column_name == '+1FF':
				total=process_card_data[card][2]
				META_REPORT[column_name].append(total)
			elif column_name == '+2FF':
				total=process_card_data[card][3]
				META_REPORT[column_name].append(total)
			elif column_name == '+3FF':
				total=process_card_data[card][4]
				META_REPORT[column_name].append(total)
			elif column_name == '+4FF':
				total=process_card_data[card][5]
				META_REPORT[column_name].append(total)
			elif column_name == 'Leader Vote':
				vote="Yes" if card_data[0] == 1 else "No"
				META_REPORT[column_name].append(vote)
			elif column_name == 'Target Level':
				target=card_data[1]
				if target < this_cards_target_level:
					target=this_cards_target_level
				META_REPORT[column_name].append(target)
			elif column_name == 'Caps':
				caps=0
				if card_data[0] == 1:
					caps=getCapsByCardLevel(card,card_data[1])
					total_caps+=caps
				META_REPORT[column_name].append(caps)
			else:
				META_REPORT[column_name].append(0)
		if index%2 == 1: choices+=1
		index+=1
	for column_name in cols:
		if column_name not in META_REPORT:
			META_REPORT[column_name]=[]
		if column_name == 'id':
			META_REPORT[column_name].append("TOTAL")
		elif column_name == 'WAL':
			avg=0
			if len(WAL)>0:
				avg="%.2f" % ( float(sum(WAL)) / len(WAL) )
			META_REPORT[column_name].append(avg)
		elif column_name == 'Caps':
			META_REPORT[column_name].append(total_caps)
		else:
			META_REPORT[column_name].append("")
	return META_REPORT, restricted_levels
	
def getTeamwarBracketReport(cols,team_id,email=None,bracketid=None):
	#cols = ['Rank', 'Team Name', 'Score', 'Runs', 'Average', 'Members', 'Projected', 'Maximum']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	bracket_data=None
	updated=None
	if bracketid == None:
		bracket_data, updated=HELPER_DB.getTeamwarBracketData(team_id)
	else:
		bracket_data, updated=HELPER_DB.getSpecificBracketData(bracketid)
	if len(bracket_data) == 0: return META_REPORT, updated
	subscriptions = None
	if email != None:
		subscriptions = HELPER_DB.getBracketSubscribe(email)
	sorted_bracket_data=[]
	for team_data in bracket_data: #[rank,TEAMNAME,RUNS,MEMBERS,SCORE]
		ID,RANK,TEAMNAME,RUNS,MEMBERS,SCORE = team_data
		avg = 0
		if RUNS > 0:
			avg="%.2f" % (float(SCORE) / RUNS)
		projected_num = int(float(avg) * MEMBERS)
		projected = "--"
		maximum = "--"
		if MEMBERS > RUNS:
			projected="%d" % int(float(avg) * MEMBERS)
			maximum="%d" % ( SCORE + (114 * (MEMBERS - RUNS)))
		if MEMBERS < 50 and RUNS < 50:
			projected+=" / %d" % int(float(avg) * 50)
			maximum+=" / %d" % ( SCORE + (114 * (50 - RUNS)))
		sorted_bracket_data.append([ID,RANK,TEAMNAME,SCORE,RUNS,float(avg),MEMBERS,projected,maximum])
	sorted_bracket_data = sorted(sorted_bracket_data, key=lambda x: (x[5]), reverse=True)
	for ID,RANK,TEAMNAME,SCORE,RUNS,avg,MEMBERS,projected,maximum in sorted_bracket_data:
		tmp_team_name = TEAMNAME.upper()
		if ID != None:
			tmp_team_name = f'[{tmp_team_name}]({SPPDREPLAY}/teams/{ID})'
		if RANK == None: RANK = "N/A"
		META_REPORT[cols[0]].append(RANK)
		META_REPORT[cols[1]].append(tmp_team_name)
		META_REPORT[cols[2]].append(SCORE)
		META_REPORT[cols[3]].append(RUNS)
		META_REPORT[cols[4]].append(avg)
		META_REPORT[cols[5]].append(MEMBERS)
		META_REPORT[cols[6]].append(projected)
		META_REPORT[cols[7]].append(maximum)
		subscribed = "No"
		if subscriptions != None and TEAMNAME in subscriptions and subscriptions[TEAMNAME]==1:
			subscribed = "Yes"
		META_REPORT[cols[8]].append(subscribed)
	return META_REPORT, updated
	
def getTeamwarBracketHistoryReport(cols,team_id,gmtOffset):
	#cols = ['id', 'Time', 'Team Name', 'Score', 'Runs', 'Average']
	META_REPORT={}
	x=[] # Dates (ordered)
	y=[] # Average Score
	for i in cols: META_REPORT[i]=[]
	bracket_data=HELPER_DB.getTeamwarBracketHistoryData(team_id)
	if len(bracket_data) == 0: return META_REPORT, x, y
	for BRACKETID,UPDATED,TEAMNAME,RUNS,SCORE in bracket_data:
		#ID,RANK,TEAMNAME,RUNS,MEMBERS,SCORE = team_data
		avg = 0
		if RUNS > 0:
			avg="%.2f" % (float(SCORE) / RUNS)
		BRACKETID=f'[{BRACKETID}]({SPPDREPLAY}/brackets/{BRACKETID})'
		UPDATED = UPDATED - gmtOffset*60
		updated_pretty=time.strftime('%Y-%m-%d %H:%M', time.gmtime(UPDATED))
		updated_date_only = time.strftime('%Y-%m-%d', time.gmtime(UPDATED))
		WEEK=0
		if int(time.strftime('%u', time.gmtime(UPDATED))) < 2:
			WEEK=int(time.strftime('%W', time.gmtime(UPDATED))) - 1
		else:
			WEEK=int(time.strftime('%W', time.gmtime(UPDATED)))
		if WEEK == 0:
			WEEK = 52
		table_data=[BRACKETID,updated_pretty,WEEK,TEAMNAME,SCORE,RUNS,float(avg)]
		index=0
		for i in cols:
			META_REPORT[i].append(table_data[index])
			index+=1
		x.append(updated_date_only)
		y.append(float(avg))
	return META_REPORT, x, y

def getAllTeamwarBracketReport(cols,league,limit=None):
	#cols = ['id', 'Rank', 'Team Name', 'Score', 'Runs', 'Average', 'Members', 'Projected', 'Maximum']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	bracket_data, updated=HELPER_DB.getAllTeamwarBracketData(league,limit)
	if len(bracket_data) == 0: return META_REPORT, updated
	average_list=[]
	for id, rank, TEAMNAME,RUNS,MEMBERS,SCORE in bracket_data: #[rank,TEAMNAME,RUNS,MEMBERS,SCORE]
		avg = 0
		if RUNS > 0:
			avg=float(SCORE) / RUNS
		average_list.append([TEAMNAME,avg])
	average_list = sorted(average_list, key=lambda x: (x[1]), reverse=True)
	avg_tracker={}
	index=1
	for TEAMNAME, _ in average_list:
		avg_tracker[TEAMNAME]=index
		index+=1
	sorted_bracket_data=[]
	for team_data in bracket_data: #[rank,TEAMNAME,RUNS,MEMBERS,SCORE]
		id, rank, TEAMNAME,RUNS,MEMBERS,SCORE = team_data
		avg = 0
		if RUNS > 0:
			avg="%.2f" % (float(SCORE) / RUNS)
		projected="%d" % int(float(avg) * MEMBERS)
		maximum="%d" % ( SCORE + (114 * (MEMBERS - RUNS)))
		if MEMBERS < 50:
			projected+=" / %d" % int(float(avg) * 50)
			maximum+=" / %d" % ( SCORE + (114 * (50 - RUNS)))
		sorted_bracket_data.append([id,rank,TEAMNAME,SCORE,RUNS,float(avg),MEMBERS,projected,maximum])
	sorted_bracket_data = sorted(sorted_bracket_data, key=lambda x: (x[3]), reverse=True)
	for id,rank,TEAMNAME,SCORE,RUNS,avg,MEMBERS,projected,maximum in sorted_bracket_data:
		avg_rank = avg_tracker[TEAMNAME]
		bracket_link = f"[{id} #{avg_rank}]({SPPDREPLAY}/brackets/{id})"
		META_REPORT[cols[0]].append(bracket_link)
		META_REPORT[cols[1]].append(rank)
		META_REPORT[cols[2]].append(TEAMNAME)
		META_REPORT[cols[3]].append(SCORE)
		META_REPORT[cols[4]].append(RUNS)
		META_REPORT[cols[5]].append(avg)
		META_REPORT[cols[6]].append(MEMBERS)
		META_REPORT[cols[7]].append(projected)
		META_REPORT[cols[8]].append(maximum)
	return META_REPORT, updated

def getAllTeamwarSummary():
	teams_by_league={
		"gold" : [[],[]],
		"silver" : [[],[]],
		"bronze" : [[],[]],
		"wood" : [[],[]]
	} #{league : [x,y], ...}
	teams_members_counts={ #teams, members
		"gold" : [0,0],
		"silver" : [0,0],
		"bronze" : [0,0],
		"wood" : [0,0]
	} #{league : [x,y], ...}
	members_count={
		"gold" : {},
		"silver" : {},
		"bronze" : {},
		"wood" : {}
	} #{league : {members : count}, ...}
	result = HELPER_DB.getAllTeamwarBracketSummary() # [ [TROPHIES, MEMBERS], ... ]
	for TROPHIES, MEMBERS in result:
		league = "wood"
		if TROPHIES >= 3500:
			league = "gold"
		elif TROPHIES >= 1500:
			league = "silver"
		elif TROPHIES >= 500:
			league = "bronze"
		if MEMBERS not in members_count[league]:
			members_count[league][MEMBERS]=0
		members_count[league][MEMBERS]+=1
		teams_members_counts[league][0]+=1
		teams_members_counts[league][1]+=MEMBERS
	for league in members_count.keys():
		for i in range(10,51):
			teams_by_league[league][0].append(i)
			if i in members_count[league]:
				teams_by_league[league][1].append(members_count[league][i])
			else:
				teams_by_league[league][1].append(0)
	return teams_by_league, teams_members_counts
	
def getEventsReport(cols,gmtOffset,lindex):
	#cols = ['Name', 'Solo/Team', 'Start', 'End', 'Total Packs', '1', '2', '3', '4', '5', '6', '7', '8']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	event_data=HELPER_DB.getEventData(int(time.time()))
	if len(event_data) == 0: return META_REPORT
	for key in event_data.keys():
		NAME, TEAM, TYPE, STARTTIME, ENDTIME, FINALPACK, PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8 = event_data[key]
		#if FINALPACK == None: continue
		NAME = HELPER.tr(NAME,lindex)
		NAME_LINK = f"[{NAME}]({SPPDREPLAY}/events/{key})"
		META_REPORT[cols[0]].append(NAME_LINK)
		META_REPORT[cols[1]].append(HELPER.tr("Solo+Team",lindex) if TEAM == 1 else HELPER.tr("Solo",lindex))
		STARTTIME = STARTTIME - gmtOffset*60
		start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(STARTTIME))
		META_REPORT[cols[2]].append(start_pretty)
		ENDTIME = ENDTIME - gmtOffset*60
		end_pretty=time.strftime('%m-%d %H:%M', time.gmtime(ENDTIME))
		META_REPORT[cols[3]].append(end_pretty)
		META_REPORT[cols[4]].append(0 if FINALPACK == None else FINALPACK)
		META_REPORT[cols[5]].append(0 if PACK1 == None else PACK1)
		META_REPORT[cols[6]].append(0 if PACK2 == None else PACK2)
		META_REPORT[cols[7]].append(0 if PACK3 == None else PACK3)
		META_REPORT[cols[8]].append(0 if PACK4 == None else PACK4)
		META_REPORT[cols[9]].append(0 if PACK5 == None else PACK5)
		META_REPORT[cols[10]].append(0 if PACK6 == None else PACK6)
		META_REPORT[cols[11]].append(0 if PACK7 == None else PACK7)
		META_REPORT[cols[12]].append(0 if PACK8 == None else PACK8)
	return META_REPORT
	
def getLastMonthsEventsReport(cols,gmtOffset,lindex):
	#cols = ['Name', 'Solo/Team', 'Start', 'End', 'Total Packs', '1', '2', '3', '4', '5', '6', '7', '8']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	event_data=HELPER_DB.getEventData(int(time.time()) - 3600 * 24 * 30)
	if len(event_data) == 0: return META_REPORT
	for key in event_data.keys():
		NAME, TEAM, TYPE, STARTTIME, ENDTIME, FINALPACK, PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8 = event_data[key]
		#if FINALPACK == None: continue
		NAME = HELPER.tr(NAME,lindex)
		NAME_LINK = f"[{NAME}]({SPPDREPLAY}/events/{key})"
		META_REPORT[cols[0]].append(NAME_LINK)
		META_REPORT[cols[1]].append(HELPER.tr("Solo+Team",lindex) if TEAM == 1 else HELPER.tr("Solo",lindex))
		STARTTIME = STARTTIME - gmtOffset*60
		start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(STARTTIME))
		META_REPORT[cols[2]].append(start_pretty)
		ENDTIME = ENDTIME - gmtOffset*60
		end_pretty=time.strftime('%m-%d %H:%M', time.gmtime(ENDTIME))
		META_REPORT[cols[3]].append(end_pretty)
		META_REPORT[cols[4]].append(0 if FINALPACK == None else FINALPACK)
		META_REPORT[cols[5]].append(0 if PACK1 == None else PACK1)
		META_REPORT[cols[6]].append(0 if PACK2 == None else PACK2)
		META_REPORT[cols[7]].append(0 if PACK3 == None else PACK3)
		META_REPORT[cols[8]].append(0 if PACK4 == None else PACK4)
		META_REPORT[cols[9]].append(0 if PACK5 == None else PACK5)
		META_REPORT[cols[10]].append(0 if PACK6 == None else PACK6)
		META_REPORT[cols[11]].append(0 if PACK7 == None else PACK7)
		META_REPORT[cols[12]].append(0 if PACK8 == None else PACK8)
	return META_REPORT
	
#NAME,TYPE,START,END,pack_data = getSpecificEventReport(cols,gmtOffset,event_id)
def getSpecificEventReport(cols,gmtOffset,event_id,lindex):
	#cols = ['Number', 'Type', 'Score', 'Common', 'Rare', 'Epic', 'Legendary', 'Coins', 'Cash', 'PVP Tickets', 'Bronze', 'Silver', 'Gold', 'Details']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	NAME,TYPE,START,END,pack_data=HELPER_DB.getSpecificEventData(event_id)
	START = START - gmtOffset*60
	start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(START))
	END = END - gmtOffset*60
	end_pretty=time.strftime('%m-%d %H:%M', time.gmtime(END))
	event_type = "Unknown"
	if TYPE == 2: event_type = "Card Usage"
	elif TYPE == 3: event_type = "Locker Tokens"
	elif TYPE == 4: event_type = "Challenge"
	elif TYPE == 5: event_type = "Team Wars"
	elif TYPE == 6: event_type = "Battle Pass"
	elif TYPE == 7: event_type = "Mission"
	if len(pack_data) == 0: return NAME,event_type,start_pretty,end_pretty,META_REPORT
	TOTAL=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	#CARDS0,CARDSP0,CARDS1,CARDSP1,CARDS2,CARDSP2,CARDS3,CARDSP3,CUR1,CUR2,CUR3,CUR4,UPS0,UPSP0,UPS1,UPSP1,UPS2,UPSP2
	for elem in pack_data:
		tmp_elem = []
		for number in elem:
			if type(number) == decimal.Decimal and number % 1 == 0:
				tmp_elem.append(int(number))
			else:
				tmp_elem.append(number)
		TEAM,PACKNUM,SCORE,\
			CARDS0,CARDSP0,\
			CARDS1,CARDSP1,\
			CARDS2,CARDSP2,\
			CARDS3,CARDSP3,\
			CUR1,CUR2,CUR3,CUR4,\
			UPS0,UPSP0,\
			UPS1,UPSP1,\
			UPS2,UPSP2,\
			SUBPACK = tmp_elem
		subpack_string = []
		if len(SUBPACK) > 0:
			for sub_elem in SUBPACK:
				for key,value in sub_elem.items():
					if key in DATABASE.DECK_MAP.keys():
						rarity = getWALOffset(key)
						if rarity == 3: CARDS3+=value
						elif rarity == 2: CARDS2+=value
						elif rarity == 1: CARDS1+=value
						elif rarity == 0: CARDS0+=value
						card_name = HELPER_DB.getCardName(key)
						subpack_string.append(f"{card_name}:{value}")
					elif key in DATABASE.UNPLAYABLE.keys():
						if "cur" in DATABASE.UNPLAYABLE[key]:
							if "Coins" in DATABASE.UNPLAYABLE[key]: CUR1+=value
							elif "Cash" in DATABASE.UNPLAYABLE[key]: CUR2+=value
							elif "PVP Tickets" in DATABASE.UNPLAYABLE[key]: CUR3+=value
						elif "mat" in DATABASE.UNPLAYABLE[key]:
							if "bronze" in DATABASE.UNPLAYABLE[key]: UPS0+=value
							elif "silver" in DATABASE.UNPLAYABLE[key]: UPS1+=value
							elif "gold" in DATABASE.UNPLAYABLE[key]: UPS2+=value
						item_name = DATABASE.UNPLAYABLE[key][0]
						item_name = HELPER.tr(item_name,lindex)
						subpack_string.append(f"{item_name}:{value}")
		subpack_string = ",".join(x for x in subpack_string)
		META_REPORT[cols[0]].append(PACKNUM)
		META_REPORT[cols[1]].append(HELPER.tr("Team",lindex) if int(TEAM) == 1 else HELPER.tr("Solo",lindex))
		META_REPORT[cols[2]].append(SCORE)
		if CARDSP0 > 0: META_REPORT[cols[3]].append(f"{CARDS0} ({CARDSP0}%)")
		else: META_REPORT[cols[3]].append(f"{CARDS0}")
		if CARDSP1 > 0: META_REPORT[cols[4]].append(f"{CARDS1} ({CARDSP1}%)")
		else: META_REPORT[cols[4]].append(f"{CARDS1}")
		if CARDSP2 > 0: META_REPORT[cols[5]].append(f"{CARDS2} ({CARDSP2}%)")
		else: META_REPORT[cols[5]].append(f"{CARDS2}")
		if CARDSP3 > 0: META_REPORT[cols[6]].append(f"{CARDS3} ({CARDSP3}%)")
		else: META_REPORT[cols[6]].append(f"{CARDS3}")
		META_REPORT[cols[7]].append(CUR1)
		META_REPORT[cols[8]].append(CUR2)
		META_REPORT[cols[9]].append(CUR3)
		if UPSP0 > 0: META_REPORT[cols[10]].append(f"{UPS0} ({UPSP0}%)")
		else: META_REPORT[cols[10]].append(f"{UPS0}")
		if UPSP1 > 0: META_REPORT[cols[11]].append(f"{UPS1} ({UPSP1}%)")
		else: META_REPORT[cols[11]].append(f"{UPS1}")
		if UPSP2 > 0: META_REPORT[cols[12]].append(f"{UPS2} ({UPSP2}%)")
		else: META_REPORT[cols[12]].append(f"{UPS2}")
		META_REPORT[cols[13]].append(subpack_string)
		META_REPORT[cols[14]].append(CUR4)
		subtotal = [CARDS0,CARDSP0,CARDS1,CARDSP1,CARDS2,CARDSP2,CARDS3,CARDSP3,CUR1,CUR2,CUR3,UPS0,UPSP0,UPS1,UPSP1,UPS2,UPSP2]
		for i in range(len(subtotal)):
			TOTAL[i]+=subtotal[i]
	#Total
	tmp_elem = []
	for number in TOTAL:
		if type(number) == decimal.Decimal and number % 1 == 0:
			tmp_elem.append(int(number))
		else:
			tmp_elem.append(number)
	CARDS0,CARDSP0,CARDS1,CARDSP1,CARDS2,CARDSP2,CARDS3,CARDSP3,CUR1,CUR2,CUR3,UPS0,UPSP0,UPS1,UPSP1,UPS2,UPSP2=tmp_elem
	META_REPORT[cols[0]].append(HELPER.tr("Total",lindex))
	META_REPORT[cols[1]].append(HELPER.tr("N/A",lindex))
	META_REPORT[cols[2]].append(HELPER.tr("N/A",lindex))
	if CARDSP0 > 0:
		if CARDSP0 > 100: CARDSP0=int(CARDSP0)
		META_REPORT[cols[3]].append(f"{CARDS0} ({CARDSP0}%)")
	else: META_REPORT[cols[3]].append(f"{CARDS0}")
	if CARDSP1 > 0:
		if CARDSP1 > 100: CARDSP1=int(CARDSP1)
		META_REPORT[cols[4]].append(f"{CARDS1} ({CARDSP1}%)")
	else: META_REPORT[cols[4]].append(f"{CARDS1}")
	if CARDSP2 > 0:
		if CARDSP2 > 100: CARDSP2=int(CARDSP2)
		META_REPORT[cols[5]].append(f"{CARDS2} ({CARDSP2}%)")
	else: META_REPORT[cols[5]].append(f"{CARDS2}")
	if CARDSP3 > 0:
		if CARDSP3 > 100: CARDSP3=int(CARDSP3)
		META_REPORT[cols[6]].append(f"{CARDS3} ({CARDSP3}%)")
	else: META_REPORT[cols[6]].append(f"{CARDS3}")
	META_REPORT[cols[7]].append(CUR1)
	META_REPORT[cols[8]].append(CUR2)
	META_REPORT[cols[9]].append(CUR3)
	if UPSP0 > 0:
		if UPSP0 > 100: UPSP0=int(UPSP0)
		META_REPORT[cols[10]].append(f"{UPS0} ({UPSP0}%)")
	else: META_REPORT[cols[10]].append(f"{UPS0}")
	if UPSP1 > 0:
		if UPSP1 > 100: UPSP1=int(UPSP1)
		META_REPORT[cols[11]].append(f"{UPS1} ({UPSP1}%)")
	else: META_REPORT[cols[11]].append(f"{UPS1}")
	if UPSP2 > 0:
		if UPSP2 > 100: UPSP2=int(UPSP2)
		META_REPORT[cols[12]].append(f"{UPS2} ({UPSP2}%)")
	else: META_REPORT[cols[12]].append(f"{UPS2}")
	META_REPORT[cols[13]].append("")
	META_REPORT[cols[14]].append("")
	return NAME,event_type,start_pretty,end_pretty,META_REPORT
	
def getTeamwarHistoryReport(team_id,weeks_ago,filter_list):
	#cols = ['id', 'Avg', ...]
	cols=['id', 'Avg', 'Weeks']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	history_data,all_dates=HELPER_DB.getTeamwarHistoryData(team_id,weeks_ago)
	if len(history_data) == 0: return META_REPORT, cols
	META_REPORT={}
	if len(filter_list) > 0:
		new_all_dates=[]
		for i in range(len(all_dates)):
			if i in filter_list:
				new_all_dates.append(all_dates[i])
			else:
				for user in history_data.keys():
					history_data[user].pop(all_dates[i], None)
		all_dates = new_all_dates
	cols.extend(all_dates)
	for i in cols: META_REPORT[i]=[]
	for USER in history_data.keys():
		avg=[]
		weeks=0
		for key in history_data[USER]:
			val=history_data[USER][key]
			if val != "N/A":
				if val == "X": val = 0
				avg.append(val)
		if len(avg) > 0:
			weeks=len(avg)
			avg = float(sum(avg)) / weeks
			avg = float("%.1f" % avg)
		else:
			avg = "N/A"
		META_REPORT[cols[0]].append(USER)
		META_REPORT[cols[1]].append(avg)
		META_REPORT[cols[2]].append(weeks)
		for cur_date in all_dates:
			val = "--"
			if cur_date in history_data[USER]:
				val = history_data[USER][cur_date]
				if val == "N/A": val = "--"
			META_REPORT[cur_date].append(val)
	return META_REPORT, cols, all_dates
	
def getTeamwarHistoryCapsReport(team_id,weeks_ago):
	#cols = ['id', 'Avg', ...]
	cols=['id', 'Avg', 'Weeks']
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	history_data,all_dates=HELPER_DB.getTeamwarHistoryCapsData(team_id,weeks_ago)
	if len(history_data) == 0: return META_REPORT, cols
	META_REPORT={}
	cols.extend(all_dates)
	for i in cols: META_REPORT[i]=[]
	time_tracker={}
	for USER in history_data.keys():
		avg=[]
		weeks=0
		for key in history_data[USER]:
			val=history_data[USER][key]
			if val != "N/A":
				if val == "X": val = 0
				avg.append(val)
		if len(avg) > 0:
			weeks=len(avg)
			avg = float(sum(avg)) / weeks
			avg = float("%.1f" % avg)
		else:
			avg = "N/A"
		META_REPORT[cols[0]].append(USER)
		META_REPORT[cols[1]].append(avg)
		META_REPORT[cols[2]].append(weeks)
		for cur_date in all_dates:
			val = "--"
			if cur_date in history_data[USER]:
				val = history_data[USER][cur_date]
				if val == "N/A": val = "--"
			META_REPORT[cur_date].append(val)
			if cur_date not in time_tracker:
				time_tracker[cur_date]=0
			if type(val) == int: time_tracker[cur_date]+=val
	totals=["TOTAL", "", ""]
	for cur_date in all_dates:
		totals.append(time_tracker[cur_date])
	index = 0
	for i in cols:
		META_REPORT[i].append(totals[index])
		index+=1
	return META_REPORT, cols
		
def getTeamEventHistoryReport(team_id):
	#cols = ['id', 'Avg', 'Weeks', '2020-01-05-Score', '2020-01-05-Packs', ...score...packs...]
	#name_array=['id','Avg Packs %','Weeks','Score','Packs']
	#name_map={ 0:['','id'],1:['','Avg Packs %'],2:['','Weeks'],3:['','2020-01-05-Score'],4:['','2020-01-05-Packs'] }
	cols_name=['id', 'Avg Packs %', 'Events']
	cols_ids_map={ 0:['','id'],1:['','Avg Packs %'],2:['','Events'] }
	META_REPORT={}
	for key in cols_ids_map: META_REPORT[cols_ids_map[key][1]]=[]
	history_data,all_events=HELPER_DB.getTeamEventHistoryData(team_id)
	if len(history_data) == 0: return META_REPORT, cols_name, cols_ids_map
	sorted_event_list=[]
	for key in all_events:
		result = all_events[key]
		if result != None:
			NAME,PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8,FINALPACK,STARTTIME=result
			event_time_pretty=time.strftime('%Y-%m-%d', time.localtime(STARTTIME))
			sorted_event_list.append([key,event_time_pretty])
	sorted_event_list=sorted(sorted_event_list, key=lambda x: (x[1]), reverse=True)
	seen_event_dict={}
	for elem in sorted_event_list:
		eventid,event_time_pretty=elem
		result = all_events[eventid]
		if result != None:
			NAME,PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8,FINALPACK,STARTTIME=result
			if NAME not in seen_event_dict:
				seen_event_dict[NAME]=0
			seen_event_dict[NAME]+=1
			TARGET_NAME=NAME[:12]
			if "Card Usage:" in NAME:
				TARGET_NAME="C:"+NAME.strip("Card Usage:")[:10]
			elif "Token:" in NAME:
				TARGET_NAME="T:"+NAME.strip("Token:")[:10]
			elif "Mission:" in NAME:
				TARGET_NAME="M:"+NAME.strip("Mission:")[:10]
			elif "Mission" in NAME:
				TARGET_NAME="M:"+NAME.strip("Mission")[:10]
			if seen_event_dict[NAME] > 1:
				TARGET_NAME+=f" {seen_event_dict[NAME]}"
			cols_ids_map[len(cols_name)]=[f'{TARGET_NAME}',f'{event_time_pretty}-Score']
			cols_name.append("Score")
			cols_ids_map[len(cols_name)]=[f'{TARGET_NAME}',f'{event_time_pretty}-Packs']
			cols_name.append("Packs")
	META_REPORT={}	
	for key in cols_ids_map: META_REPORT[cols_ids_map[key][1]]=[]
	for USER in history_data.keys():
		avg=[]
		for eventid in history_data[USER]:
			result = all_events[eventid]
			if result != None:
				raw_val=int(history_data[USER][eventid])
				NAME,PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8,FINALPACK,STARTTIME=result
				for i in range(FINALPACK,-1,-1):
					if i == 8 and raw_val >= int(PACK8):
						avg.append(float(i)/FINALPACK)
						break
					elif i == 7 and raw_val >= int(PACK7):
						avg.append(float(i)/FINALPACK)
						break
					elif i == 6 and raw_val >= int(PACK6):
						avg.append(float(i)/FINALPACK)
						break
					elif i == 5 and raw_val >= int(PACK5):
						avg.append(float(i)/FINALPACK)
						break
					elif i == 4 and raw_val >= int(PACK4):
						avg.append(float(i)/FINALPACK)
						break
					elif i == 3 and raw_val >= int(PACK3):
						avg.append(float(i)/FINALPACK)
						break
					elif i == 2 and raw_val >= int(PACK2):
						avg.append(float(i)/FINALPACK)
						break
					elif i == 1 and raw_val >= int(PACK1):
						avg.append(float(i)/FINALPACK)
						break
					elif i == 0:
						avg.append(0)
						break
		weeks=0
		if len(avg) > 0:
			weeks=len(avg)
			avg = 100 * float(sum(avg)) / weeks
			avg = float("%.1f" % avg)
		else:
			avg = "N/A"
		META_REPORT[cols_ids_map[0][1]].append(USER)
		META_REPORT[cols_ids_map[1][1]].append(avg)
		META_REPORT[cols_ids_map[2][1]].append(weeks)
		index=3
		for elem in sorted_event_list:
			eventid,pretty_date_str=elem
			result = all_events[eventid]
			SCORE = "--"
			PACKS = "--"
			if USER in history_data and eventid in history_data[USER]:
				SCORE=int(history_data[USER][eventid])
				NAME,PACK1,PACK2,PACK3,PACK4,PACK5,PACK6,PACK7,PACK8,FINALPACK,STARTTIME=result
				for i in range(FINALPACK,-1,-1):
					if i == 8 and SCORE >= int(PACK8):
						PACKS=i
						break
					elif i == 7 and SCORE >= int(PACK7):
						PACKS=i
						break
					elif i == 6 and SCORE >= int(PACK6):
						PACKS=i
						break
					elif i == 5 and SCORE >= int(PACK5):
						PACKS=i
						break
					elif i == 4 and SCORE >= int(PACK4):
						PACKS=i
						break
					elif i == 3 and SCORE >= int(PACK3):
						PACKS=i
						break
					elif i == 2 and SCORE >= int(PACK2):
						PACKS=i
						break
					elif i == 1 and SCORE >= int(PACK1):
						PACKS=i
						break
					elif i == 0:
						PACKS=0
						break
			META_REPORT[cols_ids_map[index][1]].append(SCORE)
			META_REPORT[cols_ids_map[index+1][1]].append(PACKS)
			index+=2
	return META_REPORT, cols_name, cols_ids_map
		
def getTeamReport(cols,rank,members,nklevel,status,lang_index):
	#cols = ['id', 'Rank', 'Trend', 'Score', 'Country', 'Members', 'Status', 'Min NK Level', "Member's Avg Rank"]
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result = HELPER_DB.getTeamsTableData(rank,members,nklevel,status)
	if result == None: return META_REPORT
	#x.ID, y.NAME, x.RANK, x.LASTRANK, x.TROPHIES, x.COUNTRY, x.MEMBERS, x.STATUS, x.NKLEVEL, x.UPDATED
	for row in result:
		ID, NAME, RANK, LASTRANK, TROPHIES, COUNTRY, MEMBERS, STATUS, NKLEVEL, MMR, UPDATED = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]]
		if type(NAME) == str: NAME=NAME.upper()
		NAME=f'[{NAME}]({SPPDREPLAY}/teams/{ID})'
		trend=""
		if MMR != None:
			MMR = int(MMR)
		if LASTRANK != None and LASTRANK != 0: trend=LASTRANK-RANK
		if STATUS == 'AutoAccepted': STATUS='Open'
		STATUS = HELPER.tr(STATUS,lang_index)
		table_data = [NAME, RANK, trend, TROPHIES, COUNTRY, MEMBERS, STATUS, NKLEVEL, MMR]
		index=0
		for i in cols:
			META_REPORT[i].append(table_data[index])
			index+=1
	return META_REPORT
	
def getPlayersReport(cols,rank,sort,name):
	#cols = ['id', 'Team', 'Rank', 'Trend', 'MMR', 'NK', 'Donated', 'TW Caps', 'PVP', 'PVP Perfect', 'CHLG', 'TW', 'FF', 'FF Perfect']
	QUERY='RANK <= 50 AND RANK <> 0'
	if rank == 'Top 250': QUERY='RANK <= 250 AND RANK <> 0'
	elif rank == 'Top 1000': QUERY='RANK <= 1000 AND RANK <> 0'
	else:
		for i in range(8500, 0, -100):
			min_rank=i-100
			if rank == f'{min_rank}-{i}':
				QUERY=f'MMR >= {min_rank} AND MMR < {i}'
				break
	META_REPORT={}
	for i in cols: META_REPORT[i]=[]
	result = HELPER_DB.getPlayersTableData(QUERY,sort,name)
	if result == None: return META_REPORT
	for row in result:
		unique_player_id, player_name, unique_team_id, team_name, RANK, LASTRANK, MMR, NKLEVEL, DONATED_ALL, TW_TOKENS, WINS_PVP, WINS_PVPP, WINS_CHLG, WINS_TW, WINS_FF, WINS_FFP, UPDATED = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]]
		if type(player_name) == str: player_name=player_name.upper()
		player_name = f'[{player_name}]({SPPDREPLAY}/player/{unique_player_id})'
		if type(team_name) == str: team_name=team_name.upper()
		team_name = f'[{team_name}]({SPPDREPLAY}/teams/{unique_team_id})'
		tmp_rank = ""
		if RANK != None and RANK != 0: trend = tmp_rank=RANK
		trend = ""
		if LASTRANK != None and LASTRANK != 0: trend = LASTRANK-RANK
		table_data = [player_name,team_name,tmp_rank,trend,MMR,NKLEVEL,DONATED_ALL,TW_TOKENS,WINS_PVP,WINS_PVPP,WINS_CHLG,WINS_TW,WINS_FF,WINS_FFP]
		index = 0
		for i in cols:
			META_REPORT[i].append(table_data[index])
			index+=1
	return META_REPORT
	
def getSpecificTeam(team_id):
	META_REPORT = ['', '', '', '', '', '', '', '']
	result=HELPER_DB.getSpecificTeamTableData(team_id)
	if result == None: return META_REPORT
	RANK=result[0]
	TROPHIES=result[1]
	MEMBERS=result[2]
	NKLEVEL=result[3]
	COUNTRY=result[4]
	STATUS=result[5]
	if STATUS=='AutoAccepted': STATUS='Open'
	DESC=result[6]
	team_name=HELPER_DB.getTeamName(team_id)
	META_REPORT=[team_name, RANK, TROPHIES, MEMBERS, NKLEVEL, COUNTRY, STATUS, DESC]
	return META_REPORT

def generate_team_members_table(team_id,access_level=-1):
	cols = ['id', 'Name', 'MMR', 'NK Level', 'Donated', 'Role', 'Join Date', 'Collection']
	cols = [HELPER.tr(x) for x in cols]
	team_members_report,graph_data,pie_chart=getTeamMembersReport(cols, team_id, access_level)
	df = pandas.DataFrame(OrderedDict([
		(i, team_members_report[i]) for i in cols
	]))
	columns_list=[]
	for i in cols:
		if i == 'id': columns_list.append({'id': i, 'name': i, 'presentation': 'markdown'})
		else: columns_list.append({'id': i, 'name': i})
	return html.Div(children=[
	html.Div(children=[
		dcc.Graph(
			figure=dict(
				data=graph_data,
				layout=dict(
					title='New Kid Level vs MMR',
					margin=dict(l=40, r=0, t=40, b=30),
					showlegend=False,
					xaxis=dict(title='MMR'),
					yaxis=dict(title='NK'),
					plot_bgcolor='rgb(30,30,30)',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
			)
		)],
		style={'display': 'inline-block', 'width': "50%", 'height': 400}
	),
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=pie_chart,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title='iOS vs Android',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "50%", 'height': 400}
	),
	html.Br(),
	html.Br(),
	dt.DataTable(
		id='team-members-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)])

def generate_team_applications_table(team_id,access_level=-1):
	cols = ['id', 'name', 'status', 'role']
	cols = [HELPER.tr(x) for x in cols]
	team_members_report=getTeamApplicationsReport(cols, team_id, access_level)
	df = pandas.DataFrame(OrderedDict([
		(i, team_members_report[i]) for i in cols
	]))
	return dt.DataTable(
		id='team-applications-table',
		data=df.to_dict('records'),
		columns=[
			{'id': 'id', 'name': 'id', 'presentation': 'markdown'},
			{'id': 'name', 'name': 'Name'},
			{'id': 'status', 'name': 'Accept/Reject', 'presentation': 'dropdown'},
			{'id': 'role', 'name': 'Role', 'presentation': 'dropdown'},
		],
		page_size = 5,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		dropdown={
			'status': {
				'options': [
					{'label': 'Accept', 'value': 'accept'},
					{'label': 'Reject', 'value': 'reject'},
					{'label': 'Ignore', 'value': 'ignore'},
				],
			},
			'role': {
				'options': [
					{'label': "Regular", 'value': "regular"},
					{'label': "Elder", 'value': "elder"},
					{'label': "Co-Leader", 'value': "co_leader"},
					{'label': "Leader", 'value': "leader"},
				],
			},
		},
		sort_action='native',
		filter_action='native',
		editable=access_level!=-1,
		row_deletable=False,
	)
	
def generate_card_requests_table(team_id,access_level=-1):
	cols = ['Created', 'Player', 'Card']
	cols = [HELPER.tr(x) for x in cols]
	card_requests_report,updated,card_pie=getCardRequestReport(cols, team_id, access_level)
	df = pandas.DataFrame(OrderedDict([
		(i, card_requests_report[i]) for i in cols
	]))
	last_refresh_pretty=""
	if updated != -1:
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(updated))
	return [ html.H3(f"Last Refresh {last_refresh_pretty} PST"),
	ARTICLES.CardRequestTabDescription(),
	dcc.Graph(
		figure=dict(
			data=card_pie,
			layout=dict(
				margin=dict(l=40, r=0, t=40, b=30),
				title='Top 10 Card Requests',
				paper_bgcolor='rgb(0,0,0)',
				font = {
					'family': 'Segoe UI', 
					'color': "#f9f9f9"
				},
			)
		)
	),
	dt.DataTable(
		id='team-card-requests-table',
		data=df.to_dict('records'),
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			#'padding': '15px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)]
	
def generate_card_donations_table(team_id,access_level=-1):
	cols = ['Created', 'Sender', 'Receiver', 'Card']
	cols = [HELPER.tr(x) for x in cols]
	card_requests_report,updated=getCardDonationReport(cols, team_id, access_level)
	df = pandas.DataFrame(OrderedDict([
		(i, card_requests_report[i]) for i in cols
	]))
	last_refresh_pretty=""
	if updated != -1:
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(updated))
	return [ html.H3(f"Last Refresh {last_refresh_pretty} PST"),
	ARTICLES.CardDonationTabDescription(),
	dt.DataTable(
		id='team-card-donations-table',
		data=df.to_dict('records'),
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			#'padding': '15px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)]
	
def generate_card_summary_table(team_id):
	#cols = ['id', 'Avg', 'Weeks', '2020-01-05-Score', '2020-01-05-Packs', ...score...packs...]
	name_array=['id','Don/Req Ratio','com','rar','epi','com','rar','epi','com','rar','epi','com','rar','epi']
	name_map={ 0:['','','id'],
		1:['','','ratio'],
		2:['Requests','Last 7 days','r7com'],
		3:['Requests','Last 7 days','r7rar'],
		4:['Requests','Last 7 days','r7epi'],
		5:['Requests','Last 30 days','r30com'],
		6:['Requests','Last 30 days','r30rar'],
		7:['Requests','Last 30 days','r30epi'],
		8:['Donations','Last 7 days','d7com'],
		9:['Donations','Last 7 days','d7rar'],
		10:['Donations','Last 7 days','d7epi'],
		11:['Donations','Last 30 days','d30com'],
		12:['Donations','Last 30 days','d30rar'],
		13:['Donations','Last 30 days','d30epi'],
	}
	card_summary_report,updated=getCardSummaryHistoryReport(team_id)
	df = pandas.DataFrame(OrderedDict([
		(name_map[key][2], card_summary_report[name_map[key][2]]) for key in name_map.keys()
	]))
	last_refresh_pretty=""
	if updated != -1:
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(updated))
	return [ html.H3(f"Last Refresh {last_refresh_pretty} PST"),
	dt.DataTable(
		id='summary-request-table',
		data=df.to_dict('records'),
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			#'padding': '15px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		columns=[
			{"name": [name_map[i][0],name_map[i][1],name_array[i]], "id": name_map[i][2]} for i in name_map.keys()
		],
		merge_duplicate_headers=True,
		sort_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)]

def generate_card_comparison_table(team_id):
	cols = ['Choice', 'id', 'WAL', 'Avg Level', '+1FF', '+2FF', '+3FF', '+4FF', 'Leader Vote', 'Target Level', 'Caps']
	cols = [HELPER.tr(x) for x in cols]
	card_comparison_report,restricted_levels=getCardComparisonReport(cols, team_id)
	df = pandas.DataFrame(OrderedDict([
		(i, card_comparison_report[i]) for i in cols
	]))
	return dt.DataTable(
		id='card-comparison-table',
		data=df.to_dict('records'),
		columns=[
			{'id': 'Choice', 'name': 'Choice'},
			{'id': 'id', 'name': 'id'},
			{'id': 'WAL', 'name': 'WAL'},
			{'id': 'Avg Level', 'name': 'Avg Level'},
			{'id': '+1FF', 'name': '+1FF'},
			{'id': '+2FF', 'name': '+2FF'},
			{'id': '+3FF', 'name': '+3FF'},
			{'id': '+4FF', 'name': '+4FF'},
			{'id': 'Leader Vote', 'name': 'Leader Vote', 'presentation': 'dropdown'},
			{'id': 'Target Level', 'name': 'Target Level', 'presentation': 'dropdown'},
			{'id': 'Caps', 'name': 'Caps'},
		],
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'background-color': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			#'padding': '15px',
			'width': 'auto',
			'textAlign': 'center',
			'font-weight': 'bold'
		},
		style_data_conditional=[
			{
				'if': {'column_id':'Leader Vote'},
				'color': 'gold'
			},
			{
				'if': {'column_id':'Target Level'},
				'color': 'gold'
			},
			*({
				'if': {'row_index': i},
				'background-color': 'rgb(80, 80, 80)'
			} for i in [2,3,6,7,10,11,14,15,18,19,22,23]),
			*({
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection())
		],
		tooltip_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()
		],
		dropdown={
			'Leader Vote': {
				'options': [
					{'label': 'Yes', 'value': 'Yes'},
					{'label': 'No', 'value': 'No'},
				],
			},
			'Target Level': {
				'options': [
					{'label': "N/A", 'value': "0"}
				],
			},
		},
		dropdown_conditional=[
			{
				'if': {
					'column_id':'Target Level',
					'filter_query': '{id} eq "%s"' % (card_name)
				},
				'options': [
							{'label': i, 'value': i} for i in range(base_level,8)
				]
			} for card_name,base_level in restricted_levels
		],
		sort_action='native',
		filter_action='native',
		editable=True,
		row_deletable=True,
		#hidden_columns=['+1FF', '+2FF', '>+3FF'],
	)
	
def generate_teamwar_bracket_table(team_id,gmtOffset,email=None):
	cols = ['Rank', 'Team Name', 'Score', 'Runs', 'Average', 'Members', 'Projected', 'Maximum', 'Subscribe']
	cols = [HELPER.tr(x) for x in cols]
	teamwar_bracket_report, updated=getTeamwarBracketReport(cols, team_id, email)
	df = pandas.DataFrame(OrderedDict([
		(i, teamwar_bracket_report[i]) for i in cols
	]))
	b_data = HELPER_DB.generate_bracket_history(gmtOffset,team_id,True)
	last_refresh_pretty=""
	if updated != None:
		updated = updated - gmtOffset * 60
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.gmtime(updated))
	return [ html.Div(id='hidden-div4'),
	ARTICLES.TWBattleDescription(),
	html.H3(f"Last Refresh {last_refresh_pretty}"),
	dcc.Graph(
		figure=dict(
			data=b_data,
			layout=dict(
				title='Bracket Runs',
				showlegend=True,
				legend=dict(
					x=0,
					y=1.0
				),
				margin=dict(l=40, r=0, t=40, b=30),
				plot_bgcolor='rgb(30,30,30)',
				paper_bgcolor='rgb(0,0,0)',
				font = {
					'family': 'Segoe UI', 
					'color': "#f9f9f9"
				},
			)
		),
		config=dict(staticPlot=True,scrollZoom=False),
		style={'height': 300},
	),
	dt.DataTable(
		id='tw-bracket-table',
		data=df.to_dict('records'),
		columns=[
			{'id': 'Rank', 'name': 'Rank'},
			{'id': 'Team Name', 'name': 'Team Name', 'presentation': 'markdown'},
			{'id': 'Score', 'name': 'Score'},
			{'id': 'Runs', 'name': 'Runs'},
			{'id': 'Average', 'name': 'Average'},
			{'id': 'Members', 'name': 'Members'},
			{'id': 'Projected', 'name': 'Projected'},
			{'id': 'Maximum', 'name': 'Maximum'},
			{'id': 'Subscribe', 'name': 'Subscribe', 'presentation': 'dropdown'},
		],
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		dropdown={
			'Subscribe': {
				'options': [
					{'label': 'Yes', 'value': 'Yes'},
					{'label': 'No', 'value': 'No'}
				]
			}
		},
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		editable=True,
		row_deletable=False,
	)]
	
def generate_teamwar_bracket_history_table(team_id,gmtOffset):
	cols = ['id', 'Time', 'Week', 'Team Name', 'Score', 'Runs', 'Average']
	cols = [HELPER.tr(x) for x in cols]
	teamwar_bracket_report,history_by_date,avg_by_date=getTeamwarBracketHistoryReport(cols, team_id, gmtOffset)
	df = pandas.DataFrame(OrderedDict([
		(i, teamwar_bracket_report[i]) for i in cols
	]))
	return [
	dcc.Graph(
		figure=dict(
			data=[
				dict(
					x=history_by_date,
					y=avg_by_date,
					name='Score',
					marker=dict(
						color='rgb(55, 83, 109)'
					)
				),
			],
			layout=dict(
				title=f'Average Score History',
				showlegend=True,
				legend=dict(
					x=0,
					y=1.0
				),
				margin=dict(l=40, r=0, t=40, b=30),
				plot_bgcolor='rgb(30,30,30)',
				paper_bgcolor='rgb(0,0,0)',
				font = {
					'family': 'Segoe UI', 
					'color': "#f9f9f9"
				},
			)
		),
		style={'height': 300},
	),
	dt.DataTable(
		id='tw-bracket-table',
		data=df.to_dict('records'),
		columns=[
			{'id': 'id', 'name': 'id', 'presentation': 'markdown'},
			{'id': 'Time', 'name': 'Time'},
			{'id': 'Week', 'name': 'Week'},
			{'id': 'Team Name', 'name': 'Team Name'},
			{'id': 'Score', 'name': 'Score'},
			{'id': 'Runs', 'name': 'Runs'},
			{'id': 'Average', 'name': 'Average'}
		],
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		dropdown={
			'Subscribe': {
				'options': [
					{'label': 'Yes', 'value': 'Yes'},
					{'label': 'No', 'value': 'No'}
				]
			}
		},
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		editable=True,
		row_deletable=False,
	)]
	
def generate_specific_bracket(gmtOffset,bracket_id,email=None):
	cols = ['Rank', 'Team Name', 'Score', 'Runs', 'Average', 'Members', 'Projected', 'Maximum', 'Subscribe']
	cols = [HELPER.tr(x) for x in cols]
	teamwar_bracket_report, updated=getTeamwarBracketReport(cols, None, email, bracket_id)
	df = pandas.DataFrame(OrderedDict([
		(i, teamwar_bracket_report[i]) for i in cols
	]))
	b_data = HELPER_DB.generate_bracket_history(gmtOffset,bracket_id)
	last_refresh_pretty=""
	if updated != None:
		updated = updated - gmtOffset * 60
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.gmtime(updated))
	return [ html.Div(id='hidden-div4'),
	ARTICLES.SpecificBracketDescription(),
	html.H3(f"Last Refresh {last_refresh_pretty}"),
	dcc.Graph(
		figure=dict(
			data=b_data,
			layout=dict(
				title='Bracket Runs',
				showlegend=True,
				legend=dict(
					x=0,
					y=1.0
				),
				margin=dict(l=40, r=0, t=40, b=30),
				plot_bgcolor='rgb(30,30,30)',
				paper_bgcolor='rgb(0,0,0)',
				font = {
					'family': 'Segoe UI', 
					'color': "#f9f9f9"
				},
			)
		),
		config=dict(staticPlot=False,scrollZoom=False),
		style={'height': 300},
	),
	dt.DataTable(
		id='tw-bracket-table',
		data=df.to_dict('records'),
		columns=[
			{'id': 'Rank', 'name': 'Rank'},
			{'id': 'Team Name', 'name': 'Team Name', 'presentation': 'markdown'},
			{'id': 'Score', 'name': 'Score'},
			{'id': 'Runs', 'name': 'Runs'},
			{'id': 'Average', 'name': 'Average'},
			{'id': 'Members', 'name': 'Members'},
			{'id': 'Projected', 'name': 'Projected'},
			{'id': 'Maximum', 'name': 'Maximum'},
			{'id': 'Subscribe', 'name': 'Subscribe', 'presentation': 'dropdown'},
		],
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		dropdown={
			'Subscribe': {
				'options': [
					{'label': 'Yes', 'value': 'Yes'},
					{'label': 'No', 'value': 'No'}
				]
			}
		},
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		editable=True,
		row_deletable=False,
	)]
	
def generate_allbracket_table(league,gmtOffset=0,lang_index=0):
	cols = ['id', 'Rank', 'Team Name', 'Score', 'Runs', 'Average', 'Members', 'Projected', 'Maximum']
	teamwar_bracket_report, updated=getAllTeamwarBracketReport(cols, league)
	df = pandas.DataFrame(OrderedDict([
		(i, teamwar_bracket_report[i]) for i in cols
	]))
	last_refresh_pretty=""
	if updated != None:
		updated = updated - gmtOffset * 60
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.gmtime(updated))
	columns_list=[]
	for i in cols:
		if i == 'id': columns_list.append({'id': i, 'name': HELPER.tr(i,lang_index), 'presentation': 'markdown'})
		else: columns_list.append({'id': i, 'name': HELPER.tr(i,lang_index)} )
	last_refresh_str = HELPER.tr('Last Refresh',lang_index)
	return [ html.H3(f"{last_refresh_str} {last_refresh_pretty}"),
	dt.DataTable(
		id='tw-all-bracket-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
	)]
	
def generate_allbracket_summary(lang_index=0):
	cols = ['id', 'Rank', 'Team Name', 'Score', 'Runs', 'Average', 'Members', 'Projected', 'Maximum']
	teamwar_bracket_report,teams_members_counts=getAllTeamwarSummary() #{league : [x,y], ...}
	html_list=[]
	league_str = HELPER.tr('League',lang_index)
	teams_str = HELPER.tr('Teams',lang_index)
	players_str = HELPER.tr('Players',lang_index)
	players_per_team_str = HELPER.tr('Players Per Team',lang_index)
	for league in teamwar_bracket_report.keys():
		actual_league_str = HELPER.tr(league.upper(),lang_index)
		html_list.append(dbc.Container([
			dbc.Row([html.H1(f"{actual_league_str} {league_str},\t{teams_str}: {teams_members_counts[league][0]},\t{players_str}: {teams_members_counts[league][1]}")], justify="center", align="center")
		]))
		html_list.append(dcc.Graph(
			figure=dict(
				data=[
					dict(
						x=teamwar_bracket_report[league][0],
						y=teamwar_bracket_report[league][1],
						name=players_str,
						type='bar',
						marker=dict(
							color='rgb(55, 83, 109)'
						)
					),
				],
				layout=dict(
					title=f'{players_per_team_str} - {actual_league_str} {league_str}',
					showlegend=True,
					legend=dict(
						x=0,
						y=1.0
					),
					margin=dict(l=40, r=0, t=40, b=30),
					plot_bgcolor='rgb(30,30,30)',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
			),
			style={'height': 300},
		))
		"""
		html_list.append(dcc.Graph(
			figure={
				'data': [{
					'x': teamwar_bracket_report[league][0],
					'y': teamwar_bracket_report[league][1],
					'type': 'bar'
				}]
			}
		))
		"""
	return html_list
	
def generate_events_table(gmtOffset,lindex):
	cols = ['Name', 'Solo/Team', 'Start', 'End', 'Total Packs', '1', '2', '3', '4', '5', '6', '7', '8']
	double_cols = [['','Name'],['','Solo/Team'],['','Start'],['','End'],['','Total Packs'],['Points Required For Pack','1'],['Points Required For Pack','2'],['Points Required For Pack','3'],['Points Required For Pack','4'],['Points Required For Pack','5'],['Points Required For Pack','6'],['Points Required For Pack','7'],['Points Required For Pack','8']]
	events_report=getEventsReport(cols,gmtOffset,lindex)
	df = pandas.DataFrame(OrderedDict([
		(i, events_report[i]) for i in cols
	]))
	long_events_report = getLastMonthsEventsReport(cols,gmtOffset,lindex)
	df2 = pandas.DataFrame(OrderedDict([
		(i, long_events_report[i]) for i in cols
	]))
	columns_list=[]
	for i in double_cols:
		first,second = i
		first = HELPER.tr(first,lindex)
		second = HELPER.tr(second,lindex)
		modified_i = [first,second]
		if i[1] == 'Name': columns_list.append({"name": modified_i, "id": i[1], 'presentation': 'markdown'})
		else: columns_list.append({"name": modified_i, "id": i[1]})
	return html.Div(children=[
	html.H2(HELPER.tr("Today's Events",lindex)),
	dt.DataTable(
		id='events-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=False,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		merge_duplicate_headers=True,
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
	),
	html.Br(),
	html.H2(HELPER.tr("Events History - 1 Month", lindex)),
	dt.DataTable(
		id='events-table',
		data=df2.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=False,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		merge_duplicate_headers=True,
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
	)])
	
def generate_specific_events_table(gmtOffset,event_id,lindex):
	cols = ['Number', 'Type', 'Score', 'Common', 'Rare', 'Epic', 'Legendary', 'Coins', 'Cash', 'PVP Tickets', 'Bronze', 'Silver', 'Gold', 'Details', 'Cheesy Poofs']
	double_cols = [['','Number'],['','Type'],['','Score'],['Cards','Common'],['Cards','Rare'],['Cards','Epic'],['Cards','Legendary'],['Currency','Coins'],['Currency','Cash'],['Currency','PVP Tickets'],['Materials','Bronze'],['Materials','Silver'],['Materials','Gold'],['','Details'],['','Cheesy Poofs']]
	NAME,TYPE,START,END,pack_data = getSpecificEventReport(cols,gmtOffset,event_id,lindex)
	df = pandas.DataFrame(OrderedDict([
		(i, pack_data[i]) for i in cols
	]))
	columns_list=[]
	for i in double_cols:
		first,second = i
		first = HELPER.tr(first,lindex)
		second = HELPER.tr(second,lindex)
		modified_i = [first,second]
		columns_list.append({"name": modified_i, "id": i[1]})
	type_str=HELPER.tr('Type',lindex)
	actual_type_str=HELPER.tr(f'{TYPE}',lindex)
	start_str=HELPER.tr('Start',lindex)
	end_str=HELPER.tr('End',lindex)
	packs_details_str=HELPER.tr('Packs details: Guaranteed (chance for one extra)',lindex)
	return html.Div(children=[
	html.H2(HELPER.tr(NAME,lindex)),
	html.H3(f"{type_str}:\t{actual_type_str}"),
	html.H3(f"{start_str}:\t{START}"),
	html.H3(f"{end_str}:\t{END}"),
	html.H5(packs_details_str),
	dt.DataTable(
		id='events-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=False,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		merge_duplicate_headers=True,
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
	)])
	
def generate_card_builder(lindex):
	style_dropdown={
		'text-transform': 'lowercase',
		'font-variant': 'all-small-caps',
		'color': 'black',
		'display': 'inline-block',
		'width': "75%"
	}
	THEMES = ["Adventure","Fantasy","Mystical","Neutral","Sci-fi","Superheroes"]
	RARITY = ["Common","Rare","Epic","Legendary"]
	TYPE = ["Assassin","Fighter","Ranged","Spell","Tank","Totem","Trap"]
	return html.Div(children=[
		html.Div(children=[
			dcc.Store(id='builder-session', storage_type='session'),
			html.H1(children=HELPER.tr('CARD BUILDER',lindex)),
			html.Div(children=[
				html.P(children=HELPER.tr("Theme",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Dropdown(
					id='builder-theme',
					options=[{'label': HELPER.tr(i,lindex), 'value': i} for i in THEMES],
					value=THEMES[0],
					searchable=False,
					clearable=False,
					style=style_dropdown
				)
			]),
			html.Div(children=[
				html.P(children=HELPER.tr("Rarity",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Dropdown(
					id='builder-rarity',
					options=[{'label': HELPER.tr(i,lindex), 'value': i} for i in RARITY],
					value=RARITY[0],
					searchable=False,
					clearable=False,
					style=style_dropdown
				)
			]),
			html.Div(children=[
				html.P(children=HELPER.tr("Type",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Dropdown(
					id='builder-type',
					options=[{'label': HELPER.tr(i,lindex), 'value': i} for i in TYPE],
					value=TYPE[0],
					searchable=False,
					clearable=False,
					style=style_dropdown
				)
			]),
			html.Div(children=[
				html.P(children=HELPER.tr("Name",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Input(id='builder-name', type="text", placeholder="Custom Card Name", value='', style=style_dropdown)
			]),
			html.Div(children=[
				html.P(children=HELPER.tr("Level",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Dropdown(
					id='builder-level',
					options=[{'label': i, 'value': i} for i in range(1,8)],
					value=1,
					searchable=False,
					clearable=False,
					style=style_dropdown
				)
			]),
			html.Div(children=[
				html.P(children=HELPER.tr("Cost",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Dropdown(
					id='builder-cost',
					options=[{'label': i, 'value': i} for i in range(0,10)],
					value=3,
					searchable=False,
					clearable=False,
					style=style_dropdown
				)
			]),
			html.Div(children=[
				html.P(children=HELPER.tr("Health",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Input(id='builder-health', type="text", placeholder="150", value='', style=style_dropdown)
			]),
			html.Div(children=[
				html.P(children=HELPER.tr("Attack",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Input(id='builder-attack', type="text", placeholder="50", value='', style=style_dropdown)
			]),
			html.Div(children=[
				html.P(children=HELPER.tr("Description",lindex),style={'display': 'inline-block', 'width': "25%"}),
				dcc.Input(id='builder-desc', type="text", placeholder="Description", value='', style=style_dropdown)
			]),
			dcc.Upload(
				[HELPER.tr('Drag and Drop or ',lindex),
				html.A(HELPER.tr('Select a File',lindex))],
				style={
					'width': '100%',
					'height': '60px',
					'lineHeight': '60px',
					'borderWidth': '1px',
					'borderStyle': 'dashed',
					'borderRadius': '5px',
					'textAlign': 'center'},
				max_size=1048576, #1MB
				id='builder-upload',
			),
			html.Button(HELPER.tr('Apply',lindex),
				className="w3-button",
				id='builder-apply-button',
				disabled=False
			),
			html.P(children=HELPER.tr("Please allow up to 30 seconds to generate the image.",lindex)),
		],style={'display': 'inline-block', 'width': "33%"}),
		html.Div(id='builder-content',style={'display': 'inline-block', 'width': "66%"}),
		html.P(children=HELPER.tr("Thanks to PichuZapper#8383 for the materials",lindex)),
		dcc.Interval(
			id='builder-interval',
			interval=5*1000, # in milliseconds
			n_intervals=0
		)
	])

def generate_teamwar_history_table(team_id,weeks_ago,filter_list=[]):
	#cols = ['id', 'Avg', 'Weeks', '2020-01', ...]
	teamwar_history_report, cols, all_dates=getTeamwarHistoryReport(team_id,weeks_ago,filter_list)
	df = pandas.DataFrame(OrderedDict([
		(i, teamwar_history_report[i]) for i in cols
	]))
	return [ ARTICLES.TeamWarHistoryDescription(),
	dt.DataTable(
		id='tw-history-table',
		data=df.to_dict('records'),
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '15px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)], all_dates

def generate_teamwar_history_caps_table(team_id,weeks_ago):
	#cols = ['id', 'Avg', 'Weeks', '2020-01', ...]
	teamwar_history_report, cols=getTeamwarHistoryCapsReport(team_id,weeks_ago)
	df = pandas.DataFrame(OrderedDict([
		(i, teamwar_history_report[i]) for i in cols
	]))
	return [ ARTICLES.TeamWarHistoryCapsDescription(),
	dt.DataTable(
		id='tw-history-table',
		data=df.to_dict('records'),
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '15px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)]

def generate_teamevent_history_table(team_id):
	#cols = ['id', 'Avg', 'Weeks', '2020-01-05-Score', '2020-01-05-Packs', ...score...packs...]
	#name_array=['id','Avg Packs %','Score','Packs']
	#name_map={ 0:['','id'],1:['','Avg Packs %'],2:['','Weeks'],3:['','2020-01-05-Score'],4:['','2020-01-05-Packs'] }
	teamevent_history_report, cols_name, cols_ids_map=getTeamEventHistoryReport(team_id)
	df = pandas.DataFrame(OrderedDict([
		(cols_ids_map[key][1], teamevent_history_report[cols_ids_map[key][1]]) for key in cols_ids_map.keys()
	]))
	return [
		ARTICLES.TeamEventsDescription(),
		dt.DataTable(
		id='te-history-table',
		data=df.to_dict('records'),
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=False,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '15px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		columns=[
			{"name": [cols_ids_map[i][0],cols_name[i]], "id": cols_ids_map[i][1]} for i in cols_ids_map.keys()
		],
		merge_duplicate_headers=True,
		sort_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
		)
	]

def generate_teamwar_upgrades_data(team_id):
	#Grab everyone's MMR
	upgrade_assignment=""
	userid_to_mmr = HELPER_DB.getTeamsMMR(team_id, True)
	ordered_cards, leader_choice = HELPER_DB.getUpgradeTabData(team_id)
	ingame_team_id=HELPER_DB.getInGameTeamID(team_id)
	if ingame_team_id==None: dcc.Markdown(upgrade_assignment)
	user_name_map = HELPER_DB.getAllUserNames(ingame_team_id)
	leader_choice_data={}
	if leader_choice != None:
		for row in leader_choice: #CARDID, VOTE, LEVEL
			CARDID=row[0]
			VOTE=int(row[1])
			LEVEL=row[2] #Arrays start at 0
			leader_choice_data[CARDID]=[VOTE,LEVEL]
	#Grab the cards and their target levels - figure out the caps
	#card_name, card_level, card_caps
	preprocessing_data=[]
	choices=1
	index=0
	for card in ordered_cards:
		card_name=HELPER_DB.getCardName(card)
		card_caps=0
		vote,card_level=[0,0]
		if card in leader_choice_data:
			vote,card_level=leader_choice_data[card]
		if vote == 1 and len(preprocessing_data) < choices:
			card_caps=getCapsByCardLevel(card,card_level)
			preprocessing_data.append([card_name, card_level, card_caps])
		if index%2 == 1: choices+=1
		index+=1
	"""
	total_caps=0
	for mmr in mmr_list.values():
		
	return total_caps*3
	"""
	#Write out the assignments
	#Remove Leaders/Co-Leaders from the equation as reserves
	userid_to_caps={}
	leaders_to_caps={}
	for userid in userid_to_mmr.keys():
		caps=0
		mmr,role=userid_to_mmr[userid]
		for arena in DATABASE.ARENA_MAP.keys():
			mmr_min,mmr_max=DATABASE.ARENA_MAP[arena]
			if mmr_max == None and mmr >= mmr_min:
				caps=DATABASE.PROJECTED_CAPS[arena]*3
				break
			elif mmr >= mmr_min and mmr < mmr_max:
				caps=DATABASE.PROJECTED_CAPS[arena]*3
				break
		if role != None and ('leader' in role or 'elder' in role): leaders_to_caps[userid]=[caps,role]
		else: userid_to_caps[userid]=caps
	already_picked_users=[]
	for card_name, card_level, card_caps in preprocessing_data:
		upgrade_assignment+=f'* **{card_name} Level {card_level}**'
		subtotal=0
		local_players_str=""
		if card_caps != 0:
			for userid in userid_to_caps.keys():
				if userid in already_picked_users: continue
				next_caps=userid_to_caps[userid]
				if next_caps+subtotal < card_caps:
					player_name="Unknown-"+userid[:4]
					if userid in user_name_map: player_name=user_name_map[userid]
					local_players_str+=f'   * {player_name} - {next_caps}\n'
					already_picked_users.append(userid)
					subtotal+=next_caps
			for userid in leaders_to_caps.keys():
				if userid in already_picked_users: continue
				next_caps=leaders_to_caps[userid][0]
				if next_caps+subtotal < card_caps:
					player_name="Unknown-"+userid[:4]
					if userid in user_name_map: player_name=user_name_map[userid]
					local_players_str+=f'   * {player_name} - {next_caps}\n'
					already_picked_users.append(userid)
					subtotal+=next_caps
		if subtotal == 0:
			upgrade_assignment+=f', Do not level\n'
		else:
			upgrade_assignment+=f', Subtotal - {subtotal} / {card_caps}\n'
		upgrade_assignment+=local_players_str+"\n"
	if len(already_picked_users) < len(userid_to_mmr.keys()):
		upgrade_assignment+=f'* **Reserve**\n'
		for userid in userid_to_mmr.keys():
			if userid not in already_picked_users:
				player_name="Unknown-"+userid[:4]
				if userid in user_name_map: player_name=user_name_map[userid]
				if userid not in leaders_to_caps:
					next_caps=userid_to_caps[userid]
					upgrade_assignment+=f'   * {player_name} - {next_caps}\n'
					already_picked_users.append(userid)
		for userid in userid_to_mmr.keys():
			if userid not in already_picked_users:
				player_name="Unknown-"+userid[:4]
				if userid in user_name_map: player_name=user_name_map[userid]
				next_caps, role=leaders_to_caps[userid]
				upgrade_assignment+=f'   * {player_name} - {next_caps} - {role}\n'
	return dcc.Markdown(upgrade_assignment)

def generate_collections_table(unique_user_id_override=None,access_level=1,need_collection=False):
	sorted_collection=sortCollection()
	CARDS={}
	COST={}
	deck = None
	themes = None
	if need_collection:
		deck,themes = HELPER_DB.getUsersDeck(unique_user_id_override)
	USERS_COLLECTION=HELPER_DB.getUsersCollection(g.user,unique_user_id_override,access_level)
	if USERS_COLLECTION==None: USERS_COLLECTION={}
	for elem in sorted_collection:
		if access_level == -1 and elem[0] not in USERS_COLLECTION:
			continue
		raw_theme=elem[2]
		theme="neu"
		if raw_theme == 0: theme="neu"
		elif raw_theme == 1: theme="adv"
		elif raw_theme == 2: theme="sci"
		elif raw_theme == 3: theme="mys"
		elif raw_theme == 4: theme="fan"
		elif raw_theme == 5: theme="sup"
		if theme not in CARDS:
			CARDS[theme]=[]
		if theme not in COST:
			COST[theme]=[]
		CARDS[theme].append(elem[0]) #Name
		COST[theme].append(elem[1]) #Cost
	tables_list=[]
	LEVELS=[0,1,2,3,4,5,6,7]
	UPGRADES=[]
	for key in DATABASE.WAL_MAP.keys():
		value=DATABASE.WAL_MAP[key]
		min_upgrade=value[0]
		max_upgrade=value[1]
		for i in range(max_upgrade-min_upgrade+1):
			upper=i+min_upgrade
			lower=max_upgrade
			UPGRADES.append(f"{upper}/{lower}")
	restricted_upgrades=[]
	for card_id in DATABASE.DECK_MAP.keys():
		if "spell" not in DATABASE.DECK_MAP[card_id]:
			name=DATABASE.DECK_MAP[card_id][0]
			for key in DATABASE.WAL_MAP.keys():
				restricted_upgrades.append([key,name])
	for theme in CARDS.keys():
		DISPLAY_LEVELS=[]
		DISPLAY_UPGRADES=[]
		for card_name in CARDS[theme]:
			if card_name in USERS_COLLECTION:
				level,upgrades=USERS_COLLECTION[card_name]
				DISPLAY_LEVELS.append(level)
				display_upgrades=HELPER_DB.convertUpgrades(level,upgrades)
				DISPLAY_UPGRADES.append(display_upgrades)
			else:
				DISPLAY_LEVELS.append(0)
				DISPLAY_UPGRADES.append("0/0")
		
		df = pandas.DataFrame(OrderedDict([
			('id', CARDS[theme]),
			('Cost', COST[theme]),
			('Level', DISPLAY_LEVELS),
			('Upgrades', DISPLAY_UPGRADES)
		]))
		tables_list.append(
		dt.DataTable(
			id=f'collections-table-{theme}',
			data=df.to_dict('records'),
			columns=[
				{'id': 'id', 'name': 'id'},
				{'id': 'Cost', 'name': 'Cost'},
				{'id': 'Level', 'name': 'Level', 'presentation': 'dropdown'},
				{'id': 'Upgrades', 'name': 'Upgrades', 'presentation': 'dropdown'},
			],
			css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'} ],
			style_as_list_view=True,
			style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
			style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
			style_cell={
				'backgroundColor': 'rgb(50, 50, 50)',
				'color': 'white',
				'padding': '10px',
				'width': 'auto',
				'textAlign': 'center',
				'font-weight': 'bold'
			},
			style_data_conditional=[
				{
					'if': {'row_index': 'odd'},
					'backgroundColor': 'rgb(80, 80, 80)'
				},
				{
					'if': {
						'column_id':'id',
					},
					'background-color': DATABASE.THEME_COLORS[theme],
				},
			],
			tooltip_conditional=[
				{
					'if': {
						'column_id':'id',
						'filter_query': '{id} eq "%s"' % key.upper()
					},
					'type': 'markdown',
					'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
				} for key in CARDS[theme]
			],
			sort_action='native',
			filter_action='native',
			editable=access_level==1,
			row_deletable=False,
			dropdown={
				'Level': {
					'options': [
						{'label': i, 'value': i}
						for i in LEVELS
					],
				},
				'Upgrades': {
					'options': [
						{'label': "N/A", 'value': "0"}
					],
				},
			},
			dropdown_conditional=[
				{
					'if': {
						'column_id':'Upgrades',
						'filter_query': '({Level} eq %d) && ({id} eq "%s")' % (key, card_name.upper())
					},
					'options': [
								{'label': i, 'value': i} for i in UPGRADES[DATABASE.WAL_MAP[key][0]+key:DATABASE.WAL_MAP[key][1]+key+1]
					]
				} for key,card_name in restricted_upgrades
			]
		)
		)
	tables_list.append(html.Div(id='hidden-div',style={'display': 'none'}))
	if need_collection:
		return tables_list,USERS_COLLECTION,deck,themes
	return tables_list

def generate_specific_player(user_id,lang_index=0):
	result,deck,theme=HELPER_DB.getOneTeamMember(user_id)
	history_by_date,mmr_by_date=HELPER_DB.generate_mmr_history(user_id)
	name=role=joindate=rank=max_mmr=mmr=nklevel=wins_pvp=wins_tw=wins_chlg=wins_pve=wins_ff=wins_ffp=wins_pvpp=chlg_runs=chlg_max_score=donated_cur=donated_all=team_name=platform=past_names=past_teams="Unknown"
	updated=None
	team_name_link='/teams'
	if result != None:
		name,role,joindate,rank,mmr,nklevel,wins_pvp,wins_tw,wins_chlg,wins_pve,wins_ff,wins_ffp,wins_pvpp,donated_cur,donated_all,team_name,team_name_link,updated,max_mmr,chlg_runs,chlg_max_score,platform,past_names,past_teams=result
	else: name="This user's team does not exist! You need to request your team to be added!"
	last_refresh_pretty=""
	if updated != None:
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(updated))
	past_names_pretty=""
	if len(past_names) > 0:
		past_names_pretty = "* Past Names: " + ", ".join(str(x) for x in past_names)
	past_teams_pretty=""
	if len(past_teams) > 0:
		past_teams_pretty = "* Past Teams: " + ", ".join(str(x) for x in past_teams)
	html_list=[]
	html_list.extend([
		html.Div(children=[
			html.Button('Close',
				id='player-sidebar-button-close',
				n_clicks=0,
				className="w3-bar-item w3-button w3-large"
			),
			html.Div(children=HELPER.getSideBar("/player", user_id, lindex=lang_index))
			],
			className="w3-sidebar w3-bar-block w3-dark-grey w3-animate-left",
			style={'display':'none'},
			id='player-sidebar',
		),
		html.Div(children=[
			html.Button('>>>',
				id='player-sidebar-button-open',
				n_clicks=0,
				className="w3-button w3-white w3-xxlarge"
			),
			html.H3(f"Last Refresh {last_refresh_pretty} PST"),
			html.Div(children=[
				html.Div(children=[
					dcc.Markdown(f'''
**{name}**

* RANK: {rank}
* Max MMR: {max_mmr}
* MMR: {mmr}
* NK Level: {nklevel}
* Donated Current: {donated_cur}
* Donated All: {donated_all}
* Wins:
   * PVP: {wins_pvp}
   * PVP Perfect: {wins_pvpp}
   * FF: {wins_ff}
   * FF Perfect: {wins_ffp}
   * Challenge: {wins_chlg}
      * Best Score (Wins): {chlg_max_score}
      * Completed (12 wins): {chlg_runs}
   * PVE: {wins_pve}
   * TW: {wins_tw}
* Team: [{team_name}]({team_name_link})
   * Role: {role}
   * Join Date: {joindate}
* Platform: {platform}
{past_names_pretty}
{past_teams_pretty}
					'''),
					],
					style={'display': 'inline-block', 'width': "50%", 'vertical-align': 'bottom'}
				),
				html.Div(id='new_kid_art',
					style={'display': 'inline-block', 'width': "50%", 'max-width': '200px', 'vertical-align': 'bottom'}
				)
			])
		]),
		dcc.Graph(
			figure=dict(
				data=[
					dict(
						x=history_by_date,
						y=mmr_by_date,
						name='MMR',
						marker=dict(
							color='rgb(55, 83, 109)'
						)
					),
				],
				layout=dict(
					title=f'MMR History - {name}',
					showlegend=True,
					legend=dict(
						x=0,
						y=1.0
					),
					margin=dict(l=40, r=0, t=40, b=30),
					plot_bgcolor='rgb(30,30,30)',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
			),
			style={'height': 300},
		),
	])
	html_list.append(html.Br())
	html_list.append(html.Div(
			className="w3-container",
			id='specific-player-content'
		))
	return html_list

def generate_players_table(rank,sort,name,gmtOffset,lang_index):
	cols = ['id', 'Team', 'Rank', 'Trend', 'MMR', 'NK', 'Donated', 'TW Caps', 'PVP', 'PVP Perfect', 'CHLG', 'TW', 'FF', 'FF Perfect']
	double_cols=[['','id'],['','Team'],['','Rank'],
		['','Trend'],['','MMR'],['','NK'],['','Donated'],['','TW Caps'],
		['WINS','PVP'],['WINS','PVP Perfect'],['WINS','CHLG'],
		['WINS','TW'],['WINS','FF'],['WINS','FF Perfect']]
	players_report=getPlayersReport(cols,rank,sort,name)
	unique_nk_levels,num_nk_level=HELPER.generate_nklevel_graph(players_report['NK'])
	df = pandas.DataFrame(OrderedDict([
		(i, players_report[i]) for i in cols
	]))
	columns_list=[]
	for i in double_cols:
		first,second=i
		first = HELPER.tr(first,lang_index)
		second = HELPER.tr(second,lang_index)
		modified_i = [first,second]
		if i[1] == 'id' or i[1] == 'Team': columns_list.append({"name": modified_i, "id": i[1], 'presentation': 'markdown'})
		else: columns_list.append({"name": modified_i, "id": i[1]})
	filter_str = HELPER.tr('Filter',lang_index)
	rank_str = HELPER.tr('Rank',lang_index)
	actual_rank_str = HELPER.tr(f'{rank}',lang_index)
	percent_str = HELPER.tr('Percent',lang_index)
	new_kid_level_str = HELPER.tr('New Kid Level',lang_index)
	return [html.H5(f"{filter_str}: {rank_str}: {actual_rank_str}"),
	dcc.Graph(
		figure=dict(
			data=[
				dict(
					x=unique_nk_levels,
					y=num_nk_level,
					name=f'{percent_str}',
					marker=dict(
						color='rgb(55, 83, 109)'
					)
				),
			],
			layout=dict(
				title=f'{new_kid_level_str} - {actual_rank_str}',
				showlegend=True,
				legend=dict(
					x=0,
					y=1.0
				),
				margin=dict(l=40, r=0, t=40, b=30),
				plot_bgcolor='rgb(30,30,30)',
				paper_bgcolor='rgb(0,0,0)',
				font = {
					'family': 'Segoe UI', 
					'color': "#f9f9f9"
				},
			)
		),
		style={'height': 300},
	),
	dt.DataTable(
		id='players-table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			},
			{
				'if': {
					'column_id':'Trend',
					'filter_query': '{Trend} > 0'
				},
				'color': 'green',
			},
			{
				'if': {
					'column_id':'Trend',
					'filter_query': '{Trend} < 0'
				},
				'color': 'red',
			},
		],
		data=df.to_dict('records'),
		merge_duplicate_headers=True,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)
	]

def generate_teams_table(rank,members,nklevel,status,lang_index):
	cols = ['id', 'Rank', 'Trend', 'Score', 'Country', 'Members', 'Status', 'Min NK Level', "Member's Avg Rank"]
	team_report=getTeamReport(cols,rank,members,nklevel,status,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, team_report[i]) for i in cols
	]))
	filter_str = HELPER.tr('Filter',lang_index)
	rank_str = HELPER.tr('Rank',lang_index)
	actual_rank_str = HELPER.tr(f'{rank}',lang_index)
	columns = []
	for i in range(len(cols)):
		if i == 0: columns.append({'id': cols[i], 'name': HELPER.tr(cols[i],lang_index), 'presentation': 'markdown'})
		else:  columns.append({'id': cols[i], 'name': HELPER.tr(cols[i],lang_index)})
	return [html.H5(f"{filter_str}: {rank_str}: {actual_rank_str}"),
	dt.DataTable(
		id='teams-table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		columns=columns,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			},
			{
				'if': {
					'column_id':'Trend',
					'filter_query': '{Trend} > 0'
				},
				'color': 'green',
			},
			{
				'if': {
					'column_id':'Trend',
					'filter_query': '{Trend} < 0'
				},
				'color': 'red',
			},
			{
				'if': {
					'column_id':'Score',
					'filter_query': '{Score} < 1500',
				},
				'color': 'brown',
			},
			{
				'if': {
					'column_id':'Score',
					'filter_query': '{Score} >= 1500'
				},
				'color': 'silver',
			},
			{
				'if': {
					'column_id':'Score',
					'filter_query': '{Score} >= 3500'
				},
				'color': 'gold',
			},
		],
		data=df.to_dict('records'),
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)
	]

def generate_mymatches_table(g_user,gmtOffset):
	cols = ['id', 'Time', 'Name', 'Team', 'Mode', 'Score', 'MMR']
	cols = [HELPER.tr(x) for x in cols]
	mymatches_report,win_pie,nk_pie,score_pie=getMyMatchesReport(cols, g_user, gmtOffset)
	df = pandas.DataFrame(OrderedDict([
		(i, mymatches_report[i]) for i in cols
	]))
	columns_list=[]
	for i in cols:
		if i == 'id' or i == 'Name': columns_list.append({'id': i, 'name': i, 'presentation': 'markdown'})
		else: columns_list.append({'id': i, 'name': i})
	return html.Div(children=[
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=win_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title='Win Rate',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=nk_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title="New Kid",
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=score_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title='Scores',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	dt.DataTable(
		id='my-matches-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)])

def generate_specific_players_matches(unique_user_id,gmtOffset):
	cols = ['id', 'Time', 'Opponent', 'Team', 'Mode', 'Score', 'MMR']
	cols = [HELPER.tr(x) for x in cols]
	mymatches_report,win_pie,nk_pie,score_pie=getSpecificPlayerMatchesReport(cols, unique_user_id, gmtOffset)
	df = pandas.DataFrame(OrderedDict([
		(i, mymatches_report[i]) for i in cols
	]))
	columns_list=[]
	for i in cols:
		if i == 'id' or i == 'Opponent': columns_list.append({'id': i, 'name': i, 'presentation': 'markdown'})
		else: columns_list.append({'id': i, 'name': i})
	return html.Div(children=[
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=win_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title='Win Rate',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=nk_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title="New Kid",
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=score_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title='Scores',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	dt.DataTable(
		id='my-matches-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False,
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)])

def generate_match_table(gmtOffset,rank,mode,lang_index):
	cols = ['id', 'Time', 'MMR1', 'NK1', 'MMR2', 'NK2', 'Mode', 'Score']
	double_cols = [['','id'],['','Time'],['Player 1','MMR1'],['Player 1','NK1'],['Player 2','MMR2'],['Player 2','NK2'],['','Mode'],['','Score']]
	live_matches_report,win_pie,nk_pie,score_pie=getLiveMatchesReport(cols,rank,mode,gmtOffset)
	df = pandas.DataFrame(OrderedDict([
		(i, live_matches_report[i]) for i in cols
	]))
	columns_list=[]
	for i in double_cols:
		first,second = i
		first = HELPER.tr(first,lang_index)
		second = HELPER.tr(second,lang_index)
		modified_i = [first,second]
		if i[1] == 'id': columns_list.append({"name": modified_i, "id": i[1], 'presentation': 'markdown'})
		else: columns_list.append({"name": modified_i, "id": i[1]})
	show_labels=True
	if len(nk_pie) > 0 and 'labels' in nk_pie[0] and len(nk_pie[0]['labels'])>5:
		show_labels=False
	return [
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=win_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title=HELPER.tr('Win Rate',lang_index),
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            ),
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=nk_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title=HELPER.tr('New Kid',lang_index),
					showlegend=show_labels,
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	html.Div(children=[
		dcc.Graph(
            figure=dict(
				data=score_pie,
				layout=dict(
					margin=dict(l=40, r=0, t=40, b=30),
					title=HELPER.tr('Scores',lang_index),
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
            )
        )],
		style={'display': 'inline-block', 'width': "33%", 'height': 400}
	),
	dt.DataTable(
		id='live-match-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		merge_duplicate_headers=True,
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False
	)]

def generate_challenge_table(gmtOffset,rank,lang_index):
	cols = ['id', 'Time', 'Challenge']
	cols = [HELPER.tr(x) for x in cols]
	chal_report=getChallengesReport(cols,rank,gmtOffset,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, chal_report[i]) for i in cols
	]))
	columns_list=[]
	for i in cols:
		if i == 'id': columns_list.append({"name": HELPER.tr(i,lang_index), "id": i, 'presentation': 'markdown'})
		else: columns_list.append({"name": HELPER.tr(i,lang_index), "id": i})
	return [
	dt.DataTable(
		id='challenge-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=False,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False
	)]

def generate_teamwars_table(gmtOffset,lang_index):
	cols = ['id', 'Upgrade Days', 'Name']
	cols = [HELPER.tr(x,lang_index) for x in cols]
	tw_report=getTeamwarsReport(cols,gmtOffset)
	df = pandas.DataFrame(OrderedDict([
		(i, tw_report[i]) for i in cols
	]))
	columns_list=[]
	for i in range(len(cols)):
		if i == 0: columns_list.append({"name": HELPER.tr(cols[i],lang_index), "id": cols[i], 'presentation': 'markdown'})
		else: columns_list.append({"name": HELPER.tr(cols[i],lang_index), "id": cols[i]})
	return [
	dt.DataTable(
		id='teamwars-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=False,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False
	)]
	
def generate_twmeta_table(gmtOffset,lang_index):
	cols = ['id', 'Upgrade Days', 'Name']
	cols = [HELPER.tr(x,lang_index) for x in cols]
	tw_report=getTWMetaReport(cols,gmtOffset)
	df = pandas.DataFrame(OrderedDict([
		(i, tw_report[i]) for i in cols
	]))
	columns_list=[]
	for i in range(len(cols)):
		if i == 0: columns_list.append({"name": HELPER.tr(cols[i],lang_index), "id": cols[i], 'presentation': 'markdown'})
		else: columns_list.append({"name": HELPER.tr(cols[i],lang_index), "id": cols[i]})
	return [
	dt.DataTable(
		id='teamwars-table',
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=False,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		sort_action='native',
		filter_action='native',
		editable=False,
		row_deletable=False
	)]
	
def generate_teamwar_summary_cards(team_id):
	cols = ['id','AVG','WAL','1','2','3','4','5','6','7']
	cols = [HELPER.tr(x) for x in cols]
	cards_report=getSummaryCardsReport(cols,team_id)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))		
	return dt.DataTable(
		id='table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '5px',
			#'padding': '10px',
			#'width': 'auto',
			'textAlign': 'center',
		},
		#style_data={
		#	'whiteSpace': 'normal',
		#	'height': 'auto',
		#},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			},
			*({
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection())
		],
		tooltip_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()
		],
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		data=df.to_dict('records')
	)
	
def generate_teamwar_summary_players(team_id):
	cols = ['id','MMR','NK Level','WAL Rank','WAL','Neu','Adv','Sci','Mys','Fan','Sup']
	cols = [HELPER.tr(x) for x in cols]
	players_report=getSummaryPlayersReport(cols,team_id)
	df = pandas.DataFrame(OrderedDict([
		(i, players_report[i]) for i in cols
	]))		
	return dt.DataTable(
		id='table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '5px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		#style_data={
		#	'whiteSpace': 'normal',
		#	'height': 'auto',
		#},
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		data=df.to_dict('records')
	)
	
def generate_teamwar_summary_players_all(team_id):
	cols = ['id','MMR','NK Level','WAL Rank','WAL']
	cols = [HELPER.tr(x) for x in cols]
	players_report,cols=getSummaryPlayersReport_all(cols,team_id)
	df = pandas.DataFrame(OrderedDict([
		(i, players_report[i]) for i in cols
	]))		
	return dt.DataTable(
		id='table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '5px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		#style_data={
		#	'whiteSpace': 'normal',
		#	'height': 'auto',
		#},
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		data=df.to_dict('records')
	)
	
def generate_teamwar_upgrades_spent(team_id):
	# { time: [{userid: spent, userid: spent},{cardid: spent, cardid: spent} ], ...}
	cols = ['Time', 'Player(s)', 'Card(s)']
	cols = [HELPER.tr(x) for x in cols]
	cards_report, SUMMARY=getUpgradesSpentReport(cols,team_id)
	spent,unspent,total,updated=SUMMARY #TOTAL CARDS CAPS, UNSPENT, TOTAL USERS COLLECTED, UPDATED
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	last_refresh_pretty=""
	if updated != None:
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(updated))			
	return [ html.H3(f"Last Refresh {last_refresh_pretty} PST"),
	html.H5(f"Spent: {spent}, Unspent: {unspent}, Total: {total}"),
	dt.DataTable(
		id='table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '15px',
			#'padding': '10px',
			'minWidth': '180px',
			'width': '180px',
			'maxWidth': '180px',
			'textAlign': 'center',
		},
		style_data={
			'whiteSpace': 'normal',
			'height': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		data=df.to_dict('records'),
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)
	]
	
def generate_teamwar_upgrades_cards(team_id):
	# { time: [{userid: spent, userid: spent},{cardid: spent, cardid: spent} ], ...}
	cols = ['id', 'Current Level', '+FF', 'Current Caps', 'Next Level Caps']
	cols = [HELPER.tr(x) for x in cols]
	cards_report, SUMMARY=getUpgradesCardsReport(cols,team_id)
	spent,unspent,total,updated=SUMMARY #TOTAL CARDS CAPS, UNSPENT, TOTAL USERS COLLECTED, UPDATED
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	last_refresh_pretty=""
	if updated != None:
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(updated))			
	return [ html.H3(f"Last Refresh {last_refresh_pretty} PST"),
	html.H5(f"Spent: {spent}, Unspent: {unspent}, Total: {total}"),
	dt.DataTable(
		id='table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		#	'minWidth': '180px',
		#	'width': '180px',
		#	'maxWidth': '180px',
		},
		style_data={
			'whiteSpace': 'normal',
			'height': 'auto',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			},
			*({
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection())
		],
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		data=df.to_dict('records'),
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)
	]
	
def generate_teamwar_upgrades_players(team_id):
	# { time: [{userid: spent, userid: spent},{cardid: spent, cardid: spent} ], ...}
	cols = ['id', 'Spent', 'Total', 'Day 1', 'Day 2', 'Day 3']
	cols = [HELPER.tr(x) for x in cols]
	cards_report, SUMMARY=getUpgradesPlayersReport(cols,team_id)
	spent,unspent,total,updated=SUMMARY #TOTAL CARDS CAPS, UNSPENT, TOTAL USERS COLLECTED, UPDATED
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	last_refresh_pretty=""
	if updated != None:
		last_refresh_pretty=time.strftime('%Y-%m-%d %H:%M', time.localtime(updated))			
	return [ html.H3(f"Last Refresh {last_refresh_pretty} PST"),
	html.H5(f"Spent: {spent}, Unspent: {unspent}, Total: {total}"),
	dt.DataTable(
		id='table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		#style_data={
		#	'whiteSpace': 'normal',
		#	'height': 'auto',
		#},
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		data=df.to_dict('records'),
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)
	]
	
def generate_players_collection_and_deck(g_user, unique_user_id):
	access_level=HELPER_DB.getAccessLevelTeam(g_user,unique_user_id)
	html_list=[]
	table_list, users_collection, deck, themes = generate_collections_table(unique_user_id,access_level,True)
	if deck != None and len(deck) == 12:
		CARD_NAMES1=[]
		CARD_NAMES2=[]
		CARD_NAMES1_LEVELS={}
		CARD_NAMES2_LEVELS={}
		for x in range(12):
			level_info=" "
			target_value = HELPER_DB.getCardName(deck[x])
			if target_value in users_collection:
				level,upgrades=users_collection[target_value]
				min_upgrades,max_upgrades=DATABASE.WAL_MAP[level]
				delta_upgrades=max_upgrades-min_upgrades+1
				level_with_upgrades=level+float(upgrades)/delta_upgrades
				level_info+='%.2f' % level_with_upgrades
			if x % 2 == 0:
				CARD_NAMES1.append(target_value)
				CARD_NAMES1_LEVELS[target_value]=level_info
			else:
				CARD_NAMES2.append(target_value)
				CARD_NAMES2_LEVELS[target_value]=level_info
		html_list.append(html.H3(f"Theme: {themes}"))
		
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(x+CARD_NAMES1_LEVELS[x], style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES1)])
		]))
		
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES1)],
				style={'display': 'inline-block'}
			)
		]))
		
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(x+CARD_NAMES2_LEVELS[x], style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES2)])
		]))
		
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES2)],
				style={'display': 'inline-block'}
			)
		]))
	html_list.append(html.H3('Leader/Co-Leader? You can modify the card levels they may or may not have input.'))
	for elem in table_list:
		html_list.append(
			html.Div(children=elem)
		)
		#Needed so the tables don't overlap
		html_list.append(html.Br())
		html_list.append(html.Br())
	if access_level > -1:
		html_list.append(html.H1('Bulk Insert'))
		html_list.append(html.H3('Will overwrite the levels for cards listed, Refresh the page after ~10 seconds.'))
		html_list.append(dcc.Input(id="bulk-card-input", type="text", placeholder="Dogpoo:4.40,Gizmo Ike:2,...", value='',style={
			'text-transform': 'lowercase',
			'font-variant': 'all-small-caps',
			'color': 'black'
		}))
		html_list.append(html.Button('Add',
					className="w3-button",
					id='collections-add-button',
					#disabled=access_level != 1
					disabled=access_level == -1
			)
		)
	return html_list
	
def generate_cards_table(rank='Top 1000',mode=None,search="Last 1 day",theme='All',type='All',cost='All',rarity='All',keyword='All',gmtOffset=0,lang_index=0,limit=None):
	cols = ['link', 'id', 'In % of decks']
	cards_report, updated, total_decks=getMetaReport_cards(cols,rank,mode,search,theme,type,cost,rarity,keyword,lang_index,limit)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	columns = []
	for i in range(len(cols)):
		if i == 0:
			columns.append({'id': cols[i], 'name': HELPER.tr('id',lang_index), 'presentation': 'markdown'})
		elif i == 1:
			columns.append({'id': cols[i], 'name': HELPER.tr('Name',lang_index), 'presentation': 'markdown'})
		else: columns.append({'id': cols[i], 'name': cols[i]})
	last_refresh_pretty=""
	if updated != None:
		updated = updated - gmtOffset*60
		last_refresh_pretty=time.strftime('%m-%d %H:%M', time.gmtime(updated))
	last_refresh_str = HELPER.tr('Last Refresh',lang_index)
	total_decks_str = HELPER.tr('Total Decks',lang_index)
	filter_str = HELPER.tr('Filter',lang_index)
	rank_str = HELPER.tr('Rank',lang_index)
	actual_rank_str = HELPER.tr(f'{rank}',lang_index)
	actual_search_str = HELPER.tr(f'{search}',lang_index)
	time_frame_str = HELPER.tr('Time Frame',lang_index)
	
	style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'}
	style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'}
	faction = 'native'
	saction = 'native'
	html_list=[]
	if limit != None:
		faction='none'
		saction='none'
		style_header={'backgroundColor': 'rgb(30, 30, 30)'}
		style_table={}
		html_list.append(html.A(HELPER.tr("Top Cards",lang_index), href='/cards', style={'font-size':'x-large', 'font-weight': 'bold'}))
		html_list.append(html.Br())
		html_list.append(html.Br())
	else:
		html_list.append(html.H3(f"{last_refresh_str} {last_refresh_pretty}, {total_decks_str}: {total_decks}"))
		html_list.append(html.H5(f"{filter_str}: {rank_str}: {actual_rank_str}, {time_frame_str}: {actual_search_str}"))
	html_list.append(dt.DataTable(
		id='cards-table',
		columns=columns,
		sort_action=saction,
		filter_action=faction,
		row_deletable=limit==None,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table=style_table,
		style_header=style_header,
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
				
			} for elem in sortCollection()
		],
		tooltip_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()
		],
		data=df.to_dict('records')
	))
	return html_list
	
def generate_allcards_table(theme,type,cost,rarity,keyword,lang_index):
	cols = ['link', 'id', 'cost', 'theme', 'type', 'rarity']
	cards_report=getMetaReport_allcards(cols,theme,type,cost,rarity,keyword,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	columns = []
	for i in range(len(cols)):
		if i == 0:
			columns.append({'id': cols[i], 'name': HELPER.tr('id',lang_index), 'presentation': 'markdown'})
		elif i == 1:
			columns.append({'id': cols[i], 'name': HELPER.tr('Name',lang_index), 'presentation': 'markdown'})
		else: columns.append({'id': cols[i], 'name': cols[i]})
	
	style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'}
	style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'}
	faction = 'native'
	saction = 'native'
	html_list=[]
	html_list.append(dt.DataTable(
		id='allcards-table',
		columns=columns,
		sort_action=saction,
		filter_action=faction,
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table=style_table,
		style_header=style_header,
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
				
			} for elem in sortCollection()
		],
		tooltip_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()
		],
		data=df.to_dict('records')
	))
	return html_list
	
def generate_cardstats_table(theme,type,cost,rarity,lang_index):
	cols = ['link', 'id', 'Time Between Attacks', 'Range', 'Base 4-3-2-1','Max 6-5-4-3','Max 7-6-5-4','Lvl 7']
	double_cols = [['','link'], ['','id'], ['','Time Between Attacks'], ['','Range'], ['Damage Per Second','Base 4-3-2-1'],['Damage Per Second','Max 6-5-4-3'],['Damage Per Second','Max 7-6-5-4'],['Damage Per Second','Lvl 7']]
	cards_report=getMetaReport_cardstats(cols,theme,type,cost,rarity,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	columns = []
	for i in double_cols:
		first,second=i
		first = HELPER.tr(first,lang_index)
		second = HELPER.tr(second,lang_index)
		modified_i = [first,second]
		if i[1] == 'link':
			columns.append({'id': i[1], 'name': modified_i, 'presentation': 'markdown'})
		else: columns.append({'id': i[1], 'name': modified_i})
	return [dt.DataTable(
		id='cardstats-table',
		columns=columns,
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
				
			} for elem in sortCollection()
		],
		tooltip_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()
		],
		data=df.to_dict('records'),
		merge_duplicate_headers=True
	)
	]
	
def generate_carddetails_table(card_id,lang_index):
	cols = ['Level', 'Health', 'Attack', 'Damage Per Second']
	cards_report=getMetaReport_carddetails(cols,card_id,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	columns = []
	for i in cols: columns.append({'id': i, 'name': HELPER.tr(i,lang_index)})
	return dt.DataTable(
		id='cardstats-table',
		columns=columns,
		sort_action='none',
		filter_action='none',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		data=df.to_dict('records'),
	)
	
def generate_carddetails_multiple_table(card_ids,lang_index):
	cards_report,double_cols=getMetaReport_carddetails_multiple(card_ids,lang_index)
	columns_list=[]
	for i in double_cols:
		first,second = i
		first = HELPER.tr(first,lang_index)
		second = HELPER.tr(second,lang_index)
		modified_i = [first,second]
		columns_list.append({"name": modified_i, "id": i[1]})
	df = pandas.DataFrame(OrderedDict([
		(b, cards_report[b]) for a,b in double_cols
	]))
	return dt.DataTable(
		id='cardstats-table',
		columns=columns_list,
		sort_action='none',
		filter_action='none',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		data=df.to_dict('records'),
		merge_duplicate_headers=True,
		fixed_rows={'headers': True}
	)
	
def generate_cardfulldetails_table(card_id,lang_index):
	#cols = ['Level-Upgrade']
	cards_report,cols=getMetaReport_cardfulldetails(card_id,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	columns = []
	for i in cols: columns.append({'id': i, 'name': HELPER.tr(i,lang_index)})
	return dt.DataTable(
		id='cardstats-table',
		columns=columns,
		sort_action='none',
		filter_action='none',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		data=df.to_dict('records'),
		export_columns='all',
		export_format='csv',
		export_headers='ids'
	)
	
def generate_cardfulldetails_multiple_table(card_ids,lang_index):
	cards_report,double_cols=getMetaReport_cardfulldetails_multiple(card_ids,lang_index)
	columns_list=[]
	for i in double_cols:
		first,second = i
		first = HELPER.tr(first,lang_index)
		second = HELPER.tr(second,lang_index)
		modified_i = [first,second]
		columns_list.append({"name": modified_i, "id": i[1]})
	df = pandas.DataFrame(OrderedDict([
		(b, cards_report[b]) for a,b in double_cols
	]))
	return dt.DataTable(
		id='cardstats-table',
		columns=columns_list,
		sort_action='none',
		filter_action='none',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		data=df.to_dict('records'),
		export_columns='all',
		export_format='csv',
		export_headers='ids',
		merge_duplicate_headers=True,
		fixed_rows={'headers': True}
	)
	
def generate_cardwinrate_table(card_id,lang_index):
	cols = ["Opponent's Card", 'You Win', 'You Draw', 'You Lose']
	cards_report=getMetaReport_cardwinrate(cols,card_id,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	columns = []
	for i in cols: columns.append({'id': i, 'name': HELPER.tr(i,lang_index)})
	return dt.DataTable(
		id='cardstats-table',
		columns=columns,
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		data=df.to_dict('records'),
	)
	
def generate_chal_cards_table(chal_id,gmtOffset,lindex):
	cols = ['link', 'id', 'In % of decks']
	cards_report, updated, total_decks=getMetaReport_chal_cards(cols,chal_id,lindex)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	last_refresh_pretty=""
	if updated != None:
		updated = updated - gmtOffset*60
		last_refresh_pretty=time.strftime('%m-%d %H:%M', time.gmtime(updated))
	last_refresh_str=HELPER.tr('Last Refresh', lindex)
	total_decks_str=HELPER.tr('Total Decks', lindex)
	columns = []
	for i in range(len(cols)):
		if i == 0:
			columns.append({'id': cols[i], 'name':HELPER.tr('id',lindex), 'presentation': 'markdown'},)
		elif i == 1:
			columns.append({'id': cols[i], 'name': HELPER.tr('Name',lindex)})
		else:
			columns.append({'id': cols[i], 'name': HELPER.tr(cols[i],lindex)})
	return [ html.H3(f"{last_refresh_str} {last_refresh_pretty}, {total_decks_str}: {total_decks}"),
	dt.DataTable(
		id='cards-table',
		columns=columns,
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			#'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			},
			*({
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection())
		],
		tooltip_conditional=[
			{
				'if': {
					'column_id':'id',
					'filter_query': '{id} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()
		],
		data=df.to_dict('records')
	)
	]
	
def generate_teamwars_cards_table(eventid,league,gmtOffset,lang_index):
	cols = ['Choice 1', 'Percent 1', 'Choice 2', 'Percent 2', 'Unknown']
	cols = [HELPER.tr(x,lang_index) for x in cols]
	cards_report, total_decks, meta_deck=getMetaReport_tw_cards(cols,eventid,league,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	html_list = []
	total_decks_str = HELPER.tr('Total Decks',lang_index)
	html_list.append(html.H3(f"{total_decks_str}: {total_decks}"))
	html_list.extend(generate_tw_meta_deck_content(meta_deck,lang_index))
	html_list.append(dt.DataTable(
		id='cards-table',
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			#'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			},
			*({
				'if': {
					'column_id':'Choice 1',
					'filter_query': '{Choice 1} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection()),
			*({
				'if': {
					'column_id':'Choice 2',
					'filter_query': '{Choice 2} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection())
		],
		tooltip_conditional=[
			*({
				'if': {
					'column_id':'Choice 1',
					'filter_query': '{Choice 1} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()),
			*({
				'if': {
					'column_id':'Choice 2',
					'filter_query': '{Choice 2} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys())
		],
		data=df.to_dict('records')
	))
	return html_list
	
def generate_twmeta_cards_table(eventid,league,gmtOffset,lang_index):
	cols = ['Choice 1', 'Avg Score 1', 'Choice 2', 'Avg Score 2', 'Best Choice', 'Difference']
	cols = [HELPER.tr(x,lang_index) for x in cols]
	cards_report, meta_deck=getMetaReport_twmeta_cards(cols,eventid,league,lang_index)
	df = pandas.DataFrame(OrderedDict([
		(i, cards_report[i]) for i in cols
	]))
	html_list = []
	html_list.extend(generate_tw_meta_deck_content(meta_deck,lang_index))
	html_list.append(dt.DataTable(
		id='cards-table',
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '10px',
			#'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			},
			*({
				'if': {
					'column_id':'Choice 1',
					'filter_query': '{Choice 1} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection()),
			*({
				'if': {
					'column_id':'Choice 2',
					'filter_query': '{Choice 2} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection()),
			*({
				'if': {
					'column_id':'Best Choice',
					'filter_query': '{Best Choice} eq "%s"' % elem[0].upper()
				},
				'background-color': DATABASE.THEME_COLORS[elem[2]],
			} for elem in sortCollection())
		],
		tooltip_conditional=[
			*({
				'if': {
					'column_id':'Choice 1',
					'filter_query': '{Choice 1} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()),
			*({
				'if': {
					'column_id':'Choice 2',
					'filter_query': '{Choice 2} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys()),
			*({
				'if': {
					'column_id':'Best Choice',
					'filter_query': '{Best Choice} eq "%s"' % key.upper()
				},
				'type': 'markdown',
				'value': f'![{key}]({DATABASE.IMAGE_MAP[key]})'
			} for key in DATABASE.IMAGE_MAP.keys())
		],
		data=df.to_dict('records')
	))
	return html_list
	
def getThemesTooltip():
	all_tool_tips=[]
	for x in DATABASE.THEMES:
		for y in DATABASE.THEMES:
			if x != y:
				all_tool_tips.append({
					'if': {
						'column_id':'Themes',
						'filter_query': '{Themes} eq "%s,%s"' % (x,y)
					},
					'type': 'markdown',
					'value': f'![{x}]({DATABASE.THEME_PATH[x]}) ![{y}]({DATABASE.THEME_PATH[y]})'
				})
	return all_tool_tips

def generate_themes_table(rank,search,gmtOffset,lang_index):
	cols = ['Themes', 'In % of decks']
	cols = [HELPER.tr(x,lang_index) for x in cols]
	themes_report, updated, total_decks=getMetaReport_themes(cols,rank,search,lang_index)

	df = pandas.DataFrame(OrderedDict([
		(i, themes_report[i]) for i in cols
	]))
	last_refresh_pretty=""
	if updated != None:
		updated = updated - gmtOffset*60
		last_refresh_pretty=time.strftime('%m-%d %H:%M', time.gmtime(updated))
	last_refresh_str = HELPER.tr('Last Refresh',lang_index)
	total_decks_str = HELPER.tr('Total Decks',lang_index)
	filter_str = HELPER.tr('Filter',lang_index)
	rank_str = HELPER.tr('Rank',lang_index)
	actual_search_str = HELPER.tr(f'{search}',lang_index)
	actual_rank_str = HELPER.tr(f'{rank}',lang_index)
	time_frame_str = HELPER.tr('Time Frame',lang_index)
	return [ html.H3(f"{last_refresh_str} {last_refresh_pretty}, {total_decks_str}: {total_decks}"),
	html.H5(f"{filter_str}: {rank_str}: {actual_rank_str}, {time_frame_str}: {actual_search_str}"),
	dt.DataTable(
		id='table',
		sort_action='native',
		filter_action='native',
		row_deletable=True,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_table={'font-size':'large', 'font-weight': 'bold', 'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)','font-size':'large', 'font-weight': 'bold'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		tooltip_conditional=getThemesTooltip(),
		columns=[
			{'id': i, 'name': i} for i in cols
		],
		data=df.to_dict('records')
	)
	]

def generate_decks_content(rank,gmtOffset,lang_index):
	meta_decks, updated, total_decks, graph_data=getMetaReport_decks(rank,lang_index)
	html_list=[]
	last_refresh_pretty=""
	if updated != None:
		updated = updated - gmtOffset*60
		last_refresh_pretty=time.strftime('%m-%d %H:%M', time.gmtime(updated))
	last_refresh_str = HELPER.tr('Last Refresh',lang_index)
	total_decks_str = HELPER.tr('Total Decks',lang_index)
	filter_str = HELPER.tr('Filter',lang_index)
	rank_str = HELPER.tr('Rank',lang_index)
	actual_search_str = HELPER.tr('Last 1 day',lang_index)
	actual_rank_str = HELPER.tr(f'{rank}',lang_index)
	time_frame_str = HELPER.tr('Time Frame',lang_index)
	avg_deck_cost_str = HELPER.tr('Average Deck Cost',lang_index)
	energy_str = HELPER.tr('Energy',lang_index)
	theme_str = HELPER.tr('Theme',lang_index)
	percent_str = HELPER.tr('Percent',lang_index)
	html_list.append(html.H3(f"{last_refresh_str} {last_refresh_pretty}, {total_decks_str}: {total_decks}"))
	html_list.append(html.H5(f"{filter_str}: {rank_str}: {actual_rank_str}, {time_frame_str}: {actual_search_str}"))
	html_list.append(
		dcc.Graph(
			figure=dict(
				data=graph_data,
				layout=dict(
					title=f'{avg_deck_cost_str} - {actual_rank_str}',
					margin=dict(l=40, r=0, t=40, b=30),
					showlegend=False,
					xaxis=dict(title=f'{energy_str}'),
					#yaxis=dict(title='Count')
					plot_bgcolor='rgb(30,30,30)',
					paper_bgcolor='rgb(0,0,0)',
					font = {
						'family': 'Segoe UI', 
						'color': "#f9f9f9"
					},
				)
			),
			style={'height': 300},
		)
	)
	for deck in meta_decks:
		theme=deck[0]
		percent=deck[1]
		cardids=deck[2]
		CARD_NAMES1=[]
		CARD_NAMES2=[]
		if len(cardids) != 12: continue
		for x in range(12):
			if x % 2 == 0:
				CARD_NAMES1.append(HELPER_DB.getCardName(cardids[x]))
			else:
				CARD_NAMES2.append(HELPER_DB.getCardName(cardids[x]))
		
		html_list.append(html.H3(f"{theme_str}: {theme}, {percent_str}: {percent}"))
		'''
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(x, style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES1)],
			)
		]))
		'''
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES1)],
				style={'display': 'inline-block'}
			)
		]))
		'''
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(x, style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES2)],
			)
		]))
		'''
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES2)],
				style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Br())
	return html_list
	
def generate_chal_decks_content(chal_id,lindex):
	meta_decks=getMetaReport_chal_decks(chal_id)
	html_list=[]
	theme_str = HELPER.tr('Theme',lindex)
	percent_str = HELPER.tr('Percent',lindex)
	for deck in meta_decks:
		theme=deck[0]
		percent=deck[1]
		cardids=deck[2]
		CARD_NAMES1=[]
		CARD_NAMES2=[]
		if len(cardids) != 12: continue
		for x in range(12):
			if x % 2 == 0:
				CARD_NAMES1.append(HELPER_DB.getCardName(cardids[x]))
			else:
				CARD_NAMES2.append(HELPER_DB.getCardName(cardids[x]))
		actual_theme_str = HELPER.tr(theme,lindex)
		html_list.append(html.H3(f"{theme_str}: {actual_theme_str}, {percent_str}: {percent}"))
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(HELPER.tr(x,lindex), style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES1)],
				#style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES1)],
				style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(HELPER.tr(x,lindex), style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES2)],
				#style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES2)],
				style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Br())
	return html_list
	
def generate_tw_meta_deck_content(cardids,lang_index):
	html_list=[]
	CARD_NAMES1=[]
	CARD_NAMES2=[]
	if len(cardids) != 12: return []
	for x in range(12):
		if x % 2 == 0:
			CARD_NAMES1.append(HELPER_DB.getCardName(cardids[x]))
		else:
			CARD_NAMES2.append(HELPER_DB.getCardName(cardids[x]))
	
	html_list.append(html.Div(children=[
		html.Div(children=[*(html.Div(HELPER.tr(x,lang_index), style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES1)],
			#style={'display': 'inline-block'}
		)
	]))
	html_list.append(html.Div(children=[
		html.Div(children=[*(
			html.Img(src=DATABASE.IMAGE_MAP[x],
				style={
					'border': '0',
					'alt': "",
					'width': "16%"
				}
			) for x in CARD_NAMES1)],
			style={'display': 'inline-block'}
		)
	]))
	html_list.append(html.Div(children=[
		html.Div(children=[*(html.Div(HELPER.tr(x,lang_index), style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES2)],
			#style={'display': 'inline-block'}
		)
	]))
	html_list.append(html.Div(children=[
		html.Div(children=[*(
			html.Img(src=DATABASE.IMAGE_MAP[x],
				style={
					'border': '0',
					'alt': "",
					'width': "16%"
				}
			) for x in CARD_NAMES2)],
			style={'display': 'inline-block'}
		)
	]))
	html_list.append(html.Br())
	return html_list

def get_specific_match(match_id,gmtOffset,g_user,lindex):
	if not HELPER_DB.isValidMatch(match_id):
		return dcc.Markdown(HELPER.tr('''
			Oops, this match doesn't exist.
		''',lindex))
	my_id = None
	if g_user != None:
		my_id = HELPER_DB.getUserIDFromOktaID(g_user.id)
	match_data=HELPER_DB.getMatchFromID(match_id,my_id)
	#match_data=
	#TIME,TIMELEFT,MODE,DISCONNECT,REGION,SCORE1,SCORE2
	#username1,teamname1,NK1,MMR1,RESULT1,deck1
	#username2,teamname2,NK2,MMR2,RESULT2,deck2
	if len(match_data)!=3: return dcc.Markdown(HELPER.tr('''
			Oops, this match could not displayed.
		''',lindex))
	TIME,TIMELEFT,MODE,DISCONNECT,REGION,SCORE1,SCORE2=match_data[0]
	username1,teamname1,NK1,MMR1,RESULT1,deck1=match_data[1]
	username2,teamname2,NK2,MMR2,RESULT2,deck2=match_data[2]
	html_list=[]
	TIME = TIME - gmtOffset*60
	start_pretty=time.strftime('%m-%d %H:%M', time.gmtime(TIME))
	time_str = HELPER.tr('Time',lindex)
	mode_str = HELPER.tr('Mode',lindex)
	remainingtime_str = HELPER.tr('Remaining Time',lindex)
	region_str = HELPER.tr('Region',lindex)
	opponent_disconnected_str = HELPER.tr('Opponent Disconnected',lindex)
	score_str = HELPER.tr('Score',lindex)
	name_str = HELPER.tr('Name',lindex)
	team_str = HELPER.tr('Team',lindex)
	nk_str = HELPER.tr('NK',lindex)
	mmr_str = HELPER.tr('MMR',lindex)
	actual_mode_str = HELPER.tr(MODE,lindex)
	html_list.append(dcc.Markdown(f'''
		{time_str}: {start_pretty}\n
		{mode_str}: {actual_mode_str}\n
		{remainingtime_str}: {TIMELEFT}\n
		{region_str}: {REGION}\n
		{opponent_disconnected_str}: {DISCONNECT}\n
		{score_str}: {SCORE1}:{SCORE2}\n
	'''))
	for player_data in match_data[1:]:
		username,teamname,NK,MMR,RESULT,deck=player_data
		CARD_NAMES1=[]
		CARD_NAMES2=[]
		if len(deck) != 12: continue
		index = 0
		for key in deck.keys():
			card_name = HELPER_DB.getCardName(key)
			if index % 2 == 0:
				CARD_NAMES1.append([card_name,deck[key]])
			else:
				CARD_NAMES2.append([card_name,deck[key]])
			index+=1
		RESULT = HELPER.tr(RESULT,lindex)
		html_list.append(html.H3(f"{name_str}: {username}, {team_str}: {teamname}, {nk_str}: {NK}, {mmr_str}: {MMR}, {RESULT}"))
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(f"{HELPER.tr(x[0],lindex)}, {x[1]}", style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES1)],
				#style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x[0]],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES1)],
				style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(html.Div(f"{HELPER.tr(x[0],lindex)}, {x[1]}", style={'display': 'inline-block', 'width': "16%"}) for x in CARD_NAMES2)],
				#style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Div(children=[
			html.Div(children=[*(
				html.Img(src=DATABASE.IMAGE_MAP[x[0]],
					style={
						'border': '0',
						'alt': "",
						'width': "16%"
					}
				) for x in CARD_NAMES2)],
				style={'display': 'inline-block'}
			)
		]))
		html_list.append(html.Br())
	return html_list

def generate_deckbuilder_table(theme,type,cost,rarity,lang_index):
	#0th - Autocomplete Checkbox (default on)
	#1st Layer - Themes
	#2nd Layer - Cards
	#3rd Layer - Decks - autofilled out based on an algorithm.
	#Note: `disabled=True` after 12 cards have been selected?
	#Build Deck Button at the top
	#Display "Your Deck"
	#Display "Opponent's Deck"
	# For Each Deck Select Theme(s), default ALL
	# Checkbox for multi-theme (ignore/grey-out the themes)
	# Each Deck has a dropdown with all cards (except the card already in the deck)
	# Display the image of the selected card
	
	theme_options = []
	for theme in ['adv','sci','mys','fan','sup']:
		theme_options.append({'label': HELPER.tr(theme,lang_index), 'value': theme})

	html_list=[]
	your_themes_str = HELPER.tr('Your Themes',lang_index)
	opp_themes_str = HELPER.tr("Opponent's Themes",lang_index)
	html_list.append(dcc.Checklist(
		id = 'deckbuilder-autocomplete',
		options=[{'label': 'Auto-Complete', 'value': True}],
		value=[]
	))
	html_list.append(html.H3(your_themes_str))
	html_list.append(
		dcc.Dropdown(
			id = 'deckbuilder1-theme-dropdown',
			options = theme_options,
			value = [],
			placeholder = HELPER.tr("Select two themes, or not. I'm not your boss."),
			multi=True,
			className='w3-white'
		)
	)
	html_list.append(html.Div(id='deckbuilder1-content'))
	html_list.append(html.Br())
	html_list.append(html.Br())
	html_list.append(html.H3(opp_themes_str))
	html_list.append(
		dcc.Dropdown(
			id = 'deckbuilder2-theme-dropdown',
			options = theme_options,
			value = [],
			placeholder = HELPER.tr('Select two themes'),
			multi=True,
			className='w3-white'
		)
	)
	html_list.append(html.Div(id='deckbuilder2-content'))
	return html_list

def generate_compare_table(lang_index):
	#Select 1 or more cards to compare.
	#Each Card has it's own table.
	#inline-block for each table.
	#card art if it exists.
	
	your_cards_str = HELPER.tr('Select Cards',lang_index)
	my_card_options = []
	for name,energy,theme,key in sortCollectionWithKey_all():
		my_card_options.append({'label': HELPER.tr(name,lang_index), 'value': key})
			
	html_list = []
	html_list.append(html.H3(your_cards_str))
	html_list.append(
		dcc.Dropdown(
			id = 'compare-cards-dropdown',
			options = my_card_options,
			value = [],
			placeholder = HELPER.tr('Select one or more cards',lang_index),
			multi=True,
			className='w3-white'
		)
	)
	html_list.append(html.Div(id='compare-content'))
	return html_list

def get_specific_challenge(chal_id,gmtOffset,lindex):
	name = HELPER_DB.getChallengeName(chal_id)
	if name == None:
		return dcc.Markdown(HELPER.tr('''
			Oops, this challenge doesn't exist.
		''',lindex))
	html_list=[]
	name = HELPER.tr(name,lindex)
	html_list.append(html.H3(name))
	html_list.extend(generate_chal_cards_table(chal_id,gmtOffset,lindex))
	html_list.extend(generate_chal_decks_content(chal_id,lindex))
	return html_list

def generate_specific_teamwars_table(eventid,league,gmtOffset,lang_index):
	name = HELPER_DB.getEventName(eventid)
	if name == None:
		return dcc.Markdown(HELPER.tr('''
			Oops, this teamwars doesn't exist.
		''',lang_index))
	html_list=[]
	html_list.append(html.H3(name))
	html_list.extend(generate_teamwars_cards_table(eventid,league,gmtOffset,lang_index))
	return html_list
	
def generate_specific_twmeta_table(eventid,league,gmtOffset,lang_index):
	name = HELPER_DB.getEventName(eventid)
	if name == None:
		return dcc.Markdown(HELPER.tr('''
			Oops, this teamwars doesn't exist.
		''',lang_index))
	html_list=[]
	html_list.append(html.H3(name))
	html_list.extend(generate_twmeta_cards_table(eventid,league,gmtOffset,lang_index))
	return html_list

def get_specific_team(team_id, full_search, g_user=None, lindex=0):
	#Not Valid Team?
	if not HELPER_DB.isValidTeamID(team_id):
		return dcc.Markdown(HELPER.tr('''
			Oops, this team doesn't exist.
		''',lindex))
	global tab_styles,tab_style,tab_selected_style
	result=getSpecificTeam(team_id)
	NAME=result[0]
	RANK=result[1]
	TROPHIES=result[2]
	MEMBERS=result[3]
	LEAGUE="Unknown"
	if type(TROPHIES) != int:
		TROPHIES = -1
	elif TROPHIES > 3500:
		LEAGUE='Gold'
	elif TROPHIES > 1500:
		LEAGUE='Silver'
	elif TROPHIES > 500:
		LEAGUE='Bronze'
	else:
		LEAGUE='Wooden'
	LEAGUE = HELPER.tr(LEAGUE,lindex)
	NKLEVEL=result[4]
	COUNTRY=result[5]
	STATUS=result[6]
	STATUS = HELPER.tr(STATUS,lindex)
	DESC=result[7]
	rank_str = HELPER.tr('Rank',lindex)
	score_str = HELPER.tr('Score',lindex)
	members_str = HELPER.tr('Members',lindex)
	league_str = HELPER.tr('League',lindex)
	min_nk_level_str = HELPER.tr('Min New Kid Level',lindex)
	country_str = HELPER.tr('Country',lindex)
	status_str = HELPER.tr('Status',lindex)
	description_str = HELPER.tr('Description',lindex)
	tab_val='members'
	if 't1' in full_search: tab_val=full_search['t1']
	return html.Div(children=[
			html.H1(NAME), #Name: {NAME}\n
			dcc.Markdown(f'''
				{rank_str}: {RANK}\n
				{score_str}: {TROPHIES}\n
				{members_str}: {MEMBERS}\n
				{league_str}: {LEAGUE}\n
				{min_nk_level_str}: {NKLEVEL}\n
				{country_str}: {COUNTRY}\n
				{status_str}: {STATUS}\n
				{description_str}: {DESC}\n
			'''),
			html.H3(HELPER.tr('Team Details',lindex)),
			dcc.Tabs(
				id="specific-team-tabs",
				value=tab_val,
				children=[
					dcc.Tab(label=HELPER.tr('Members',lindex), value='members', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Team Wars',lindex), value='team-wars', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Team Events',lindex), value='team-events', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Requests',lindex), value='requests', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Applications',lindex), value='applications', style=tab_style, selected_style=tab_selected_style),
				],persistence=True,
				mobile_breakpoint=0,
				style=tab_styles
			),
			html.Div(id='specific-team-tabs-content')
		],
		className="w3-container"
	)

def get_specific_teamwars(eventid,lindex=0):
	global tab_styles,tab_style,tab_selected_style
	return html.Div(children=[
			html.H3(HELPER.tr('Team War Leagues',lindex)),
			ARTICLES.TeamwarsDescription(lindex),
			dcc.Tabs(
				id="specific-meta-tw-tabs",
				value='summary',
				children=[
					dcc.Tab(label=HELPER.tr('All',lindex), value='summary', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Gold',lindex), value='gold', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Silver',lindex), value='silver', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Bronze',lindex), value='bronze', style=tab_style, selected_style=tab_selected_style),
				],persistence=True,
				mobile_breakpoint=0,
				#className="w3-black"
				style=tab_styles
			),
			html.Div(id='specific-teamwars-content')
		],
		className="w3-container"
	)

def get_specific_twmeta(eventid,lindex=0):
	global tab_styles,tab_style,tab_selected_style
	return html.Div(children=[
			html.H3(HELPER.tr('Team War Leagues',lindex)),
			ARTICLES.TeamwarsDescription(lindex),
			dcc.Tabs(
				id="specific-meta-tw-tabs",
				value='summary',
				children=[
					dcc.Tab(label=HELPER.tr('All',lindex), value='summary', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Gold',lindex), value='gold', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Silver',lindex), value='silver', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Bronze',lindex), value='bronze', style=tab_style, selected_style=tab_selected_style),
				],persistence=True,
				mobile_breakpoint=0,
				#className="w3-black"
				style=tab_styles
			),
			html.Div(id='specific-twmeta-content')
		],
		className="w3-container"
	)
	
def get_specific_card(card_id,lindex=0):
	NAME, result = HELPER_DB.getCardDataAll(int(card_id))
	if result == None:
		return dcc.Markdown('''
			Oops, this card doesn't exist.
		''')
	#NAME = result[0]
	DISPLAY_NAME=NAME
	#DISPLAY_NAME=HELPER.tr(NAME,lindex)
	#COST=HELPER.tr(result[1],lindex)
	#TYPE=HELPER.tr(result[2],lindex)
	#THEME=HELPER.tr(result[3],lindex)
	#RARITY=HELPER.tr(result[4],lindex)
	#name_str=HELPER.tr('Name',lindex)
	#cost_str=HELPER.tr('Cost',lindex)
	#type_str=HELPER.tr('Type',lindex)
	#theme_str=HELPER.tr('Theme',lindex)
	#rarity_str=HELPER.tr('Rarity',lindex)
	card_history_str=HELPER.tr('Card History',lindex)
	percent_str=HELPER.tr('Percent',lindex)
	card_data=HELPER_DB.generate_card_history(int(card_id))
	image_source = ''
	if NAME in DATABASE.IMAGE_MAP: image_source = DATABASE.IMAGE_MAP[NAME]
	global tab_styles,tab_style,tab_selected_style
	return html.Div(children=[
			html.Div(children=[
				dcc.Markdown(result)],
				style={'display': 'inline-block'}
			),
			html.Div(children=[
				html.Img(src=f"{image_source}",
					style={
						'border': '0',
						'alt': f"{NAME}",
						'margin-left': '25%',
						'width': "50%",
					}
				)],
				style={'display': 'inline-block'}
			),
			dcc.Graph(
				figure=dict(
					data=card_data,
					layout=dict(
						title=f'{card_history_str} - {DISPLAY_NAME} - {percent_str}',
						showlegend=True,
						legend=dict(
							x=0,
							y=1.0
						),
						margin=dict(l=40, r=0, t=40, b=30),
						plot_bgcolor='rgb(30,30,30)',
						paper_bgcolor='rgb(0,0,0)',
						font = {
							'family': 'Segoe UI', 
							'color': "#f9f9f9"
						},
					)
				),
				style={'height': 300},
			),
			dcc.Tabs(
				id="specific-card-tabs",
				value='simple',
				children=[
					dcc.Tab(label=HELPER.tr('Simple',lindex), value='simple', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Detailed',lindex), value='detailed', style=tab_style, selected_style=tab_selected_style)
				],persistence=True,
				mobile_breakpoint=0,
				#className="w3-black"
				style=tab_styles
			),
			html.Div(id='specific-card-tabs-content')
		],
		className="w3-container"
	)
	
def get_all_brackets(lindex=0):
	global tab_styles,tab_style,tab_selected_style
	return html.Div(children=[
			html.H3(HELPER.tr('All Live Brackets',lindex)),
			ARTICLES.BracketsDescription(lindex),
			dcc.Tabs(
				id="specific-bracket-tabs",
				value='gold',
				children=[
					dcc.Tab(label=HELPER.tr('Gold',lindex), value='gold', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Silver',lindex), value='silver', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Bronze',lindex), value='bronze', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Wood',lindex), value='wood', style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(label=HELPER.tr('Summary',lindex), value='summary', style=tab_style, selected_style=tab_selected_style),
				],persistence=True,
				mobile_breakpoint=0,
				#className="w3-black"
				style=tab_styles
			),
			html.Div(id='specific-bracket-tabs-content')
		],
		className="w3-container"
	)
	
def get_all_events(gmtOffset,lindex=0):
	return html.Div(children=[
			generate_events_table(gmtOffset,lindex)
		],
		className="w3-container"
	)
	
def get_specific_event(gmtOffset,event_id,lindex=0):
	return html.Div(children=[
			generate_specific_events_table(gmtOffset,event_id,lindex)
		],
		className="w3-container"
	)
	
def get_card_builder(lindex):
	return html.Div(children=[
			generate_card_builder(lindex)
		],
		className="w3-container"
	)
	
'''
html.Div(children=HOME_THEMES(lindex),
	#className='giveboxplease'
),
html.Div(children=HOME_CARDS_CHAOS(lindex),
	#className='giveboxplease'
),
html.Div(children=HOME_DONATE(lindex),
	#TO-DO HALF BOX
	#className='giveboxplease'
),
html.Div(children=HOME_GETTING_STARTED(lindex),
	#TO-DO HALF BOX
	#className='giveboxplease'
),
html.Div(children=HOME_DECK_TRACKER(lindex),
	#TO-DO HALF BOX
	#className='giveboxplease'
),
html.Div(children=HOME_MASTER_META(lindex),
	#TO-DO HALF BOX
	#className='giveboxplease'
),
#html.Div(children=HOME_THEME_MATCHUPS(lindex),
#	#TO-DO HALF BOX
#	#className='giveboxplease'
#),
html.Div(children=HOME_LIVE_CARDS(lindex),
	#className='giveboxplease'
),
'''
def new_home_page(lindex=0):
	BOX_X=325
	BOX_Y=400
	return html.Div(children=[
		html.Div(children=[
			html.H1(HELPER.tr("UNLEASH YOUR POTENTIAL",lindex),
				style={'color':'black','font-size':'x-large','font-weight': 'bold','-webkit-text-stroke': '1px white','-webkit-text-fill-color': 'black'}),   
			html.H1(HELPER.tr("FIND THE BEST DECK FOR YOUR RANK",lindex),
				style={'color':'black','font-size':'x-large','font-weight': 'bold','-webkit-text-stroke': '1px white','-webkit-text-fill-color': 'black'}),
			],
			style = {
				'background-image': "url('https://i.imgur.com/FE9cWZm.png')",
				'background-repeat': 'no-repeat',
				'background-attachment': 'scroll',
				'background-position': 'right top',
				'background-size': 'auto 180px',
				'height':'231px'
			}
		),
		#Build out a grid summarizing all the features of the website
		html.Div([
			html.Div(children=generate_cards_table(lang_index=lindex,limit=5),
				style = {'display':'inline-block',
					'max-width': f'{BOX_X}px','max-height': f'{BOX_Y}px',
					'min-width': f'{BOX_X}px','min-height': f'{BOX_Y}px','border': '3px solid #73AD21','vertical-align': 'bottom'},
			),
			html.Div(id='home-live-matches',children=html.A(HELPER.tr("Live Matches",lindex), href='/match', style={'font-size':'x-large', 'font-weight': 'bold'}),
				style = {'display':'inline-block',
					'max-width': f'{BOX_X}px','max-height': f'{BOX_Y}px',
					'min-width': f'{BOX_X}px','min-height': f'{BOX_Y}px','border': '3px solid #73AD21','vertical-align': 'bottom','transition': '1.5s ease'}
			),
			html.Div(children=get_theme_matchups(lindex),
				style = {'display':'inline-block',
					'max-width': f'{BOX_X}px','max-height': f'{BOX_Y}px',
					'min-width': f'{BOX_X}px','min-height': f'{BOX_Y}px','border': '3px solid #73AD21','vertical-align': 'bottom'},
			),
			html.Div(children=get_top_gold_bracket(lindex),
				style = {'display':'inline-block',
					'max-width': f'{BOX_X}px','max-height': f'{BOX_Y}px',
					'min-width': f'{BOX_X}px','min-height': f'{BOX_Y}px','border': '3px solid #73AD21','vertical-align': 'bottom'},
			),
		],className='w3-container'),
		html.Div(id='home-best-deck',children=html.A(HELPER.tr("The Best Deck",lindex), href='/decks', style={'font-size':'large', 'font-weight': 'bold'}),
			style = {'border': '3px solid #73AD21','vertical-align': 'bottom','transition': '1.5s ease'}
		),
		dcc.Interval(
			id='home-interval',
			interval=10*1000, # in milliseconds
			n_intervals=0
		),
		dcc.Interval(
			id='home-interval-two',
			interval=30*1000, # in milliseconds
			n_intervals=0
		)
		],
		className="w3-container"
	)
	
def get_theme_matchups(lang_index):
	cols = ['You']
	double_cols = [['','You']]
	theme_matchups,cols=getThemeMatchups(cols,lang_index)
	for i in cols:
		if i == 'You': continue
		double_cols.append(['Opponent',i])
	columns_list=[]
	for i in double_cols:
		first,second = i
		first = HELPER.tr(first,lang_index)
		second = HELPER.tr(second,lang_index)
		modified_i = [first,second]
		columns_list.append({"name": modified_i, "id": i[1]})
	df = pandas.DataFrame(OrderedDict([
		(i, theme_matchups[i]) for i in cols
	]))
	return html.Div(children=[
	html.H2(HELPER.tr("Theme Matchups",lang_index)),
	html.H5(HELPER.tr("Find the counter! Discover the themes that will beat your opponent.",lang_index)),
	dt.DataTable(
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_as_list_view=True,
		style_header={'backgroundColor': 'rgb(30, 30, 30)'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			#'padding': '10px',
			'width': 'auto',
			'textAlign': 'center',
		},
		#Make >50% green, and <50% red
		style_data_conditional=[
			*({
				'if': {
					'column_id':elem['id'],
					'filter_query': '{%s} > 50' % elem['id']
				},
				'background-color': 'green',
			} for elem in columns_list),
			*({
				'if': {
					'column_id':elem['id'],
					'filter_query': '{%s} < 50' % elem['id']
				},
				'background-color': 'red',
			} for elem in columns_list)
		],
		sort_action='native',
		editable=False,
		row_deletable=False,
		merge_duplicate_headers=True,
	)])
	
def get_top_gold_bracket(lang_index):
	cols = ['id', 'Rank', 'Team Name', 'Score', 'Runs', 'Average', 'Members', 'Projected', 'Maximum']
	teamwar_bracket_report, updated=getAllTeamwarBracketReport(cols, 'gold', limit=5)
	df = pandas.DataFrame(OrderedDict([
		(i, teamwar_bracket_report[i]) for i in cols
	]))
	columns_list=[]
	for i in cols:
		if i == 'id': columns_list.append({'id': i, 'name': HELPER.tr(i,lang_index), 'presentation': 'markdown'})
		else: columns_list.append({'id': i, 'name': HELPER.tr(i,lang_index)} )
	return [html.A(HELPER.tr('Team Wars Brackets',lang_index), href='/brackets',style={'font-size':'x-large', 'font-weight': 'bold',}),
	html.Br(),
	html.Br(),
	dt.DataTable(
		data=df.to_dict('records'),
		columns=columns_list,
		css = [ {"selector": ".Select-value-label", "rule": 'color: gold;'},
			{"selector": "input:not([type=radio]):not([type=checkbox])", "rule": 'color: gold;'}],
		style_table={'overflowX': 'scroll'},
		style_header={'backgroundColor': 'rgb(30, 30, 30)'},
		style_cell={
			'backgroundColor': 'rgb(50, 50, 50)',
			'color': 'white',
			'padding': '0px',
			'width': 'auto',
			'textAlign': 'center',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgb(80, 80, 80)'
			}
		],
		editable=False,
		row_deletable=False,
	)]
	
class SPPDSIM():

	def cards_layout(card_id = None,lindex=0):
		if card_id == None:
			return [
				HELPER.getHeader(g.user,lang_index=lindex),
				HELPER.getMainSideBar(lindex),
				*HELPER.buildSidebarCustom('cards',ARTICLES.CardsDescription(lindex),lindex)
			]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			get_specific_card(card_id,lindex)
		]

	def allcards_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('allcards',ARTICLES.AllCardsDescription(lindex),lindex)
		]

	def compare_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			ARTICLES.CompareCardsDescription(lindex),
			*generate_compare_table(lindex)
		]

	def cardstats_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('cardstats',ARTICLES.CardstatsDescription(lindex),lindex)
		]

	def deckbuilder_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('deckbuilder',ARTICLES.DeckbuilderDescription(lindex),lindex)
		]
	
	def decks_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('decks',ARTICLES.DecksDescription(lindex),lindex)
		]

	def themes_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('themes',ARTICLES.ThemesDescription(lindex),lindex)
		]
	
	def collections_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('mycards',ARTICLES.CollectionsDescription(lindex),lindex)
		]
	
	def mymatches_layout(gmtOffset,lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('mymatches',ARTICLES.MyMatchesDescription(lindex),lindex)
		]
		
	def player_layout(user_id=None,lindex=0):
		if user_id == None: return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('player',ARTICLES.PlayersDescription(lindex),lindex)
		]
		if not HELPER_DB.isValidUserID(user_id):
			return [
				HELPER.getHeader(g.user,lang_index=lindex),
				HELPER.getMainSideBar(lindex),
				html.H1(HELPER.tr("Can't display this page.",lindex)),
				html.H1(HELPER.tr("Maybe the player set it to private.",lindex))
			]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*generate_specific_player(user_id,lang_index=lindex)
		]
	
	def teams_layout(team_id=None,full_search={},lindex=0):
		if team_id == None: return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('teams',ARTICLES.TeamsDescription(lindex),lindex)
		]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			get_specific_team(team_id, full_search, g.user, lindex)
		]
	
	def teamwars_layout(eventid = None,lindex=0):
		if eventid == None: return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('teamwars',ARTICLES.TeamwarsDescription(lindex),lindex)
		]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			get_specific_teamwars(eventid,lindex)
		]
	
	def twmeta_layout(eventid = None,lindex=0):
		if eventid == None: return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('twmeta',ARTICLES.TeamwarsDescription(lindex),lindex)
		]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			get_specific_twmeta(eventid,lindex)
		]
		
	def match_layout(gmtOffset,match_id=None,lindex=0):
		if match_id == None: return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('match',ARTICLES.LiveMatchDescription(lindex),lindex)
		]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*get_specific_match(match_id,gmtOffset,g.user,lindex)
		]
	
	def challenge_layout(gmtOffset,chal_id=None,lindex=0):
		if chal_id == None: return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*HELPER.buildSidebarCustom('challenge',ARTICLES.ChallengeDescription(lindex),lindex)
		]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*get_specific_challenge(chal_id,gmtOffset,lindex)
		]
		
	def brackets_layout(gmtOffset=None,bracket_id=None,email=None,lindex=0):
		if bracket_id == None:
			return [
				HELPER.getHeader(g.user,lang_index=lindex),
				HELPER.getMainSideBar(lindex),
				get_all_brackets(lindex)
			]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*generate_specific_bracket(gmtOffset,bracket_id,email)
		]
		
	def events_layout(gmtOffset=0,event_id=None,lindex=0):
		if event_id == None:
			return [
				HELPER.getHeader(g.user,lang_index=lindex),
				HELPER.getMainSideBar(lindex),
				get_all_events(gmtOffset,lindex)
			]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			get_specific_event(gmtOffset,event_id,lindex)
		]
		
	def articles_layout(article_id=None,lindex=0):
		if article_id == None: return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			*ARTICLES.getArticlesList(lindex)
			]
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			ARTICLES.getArticleByNumber(article_id,lindex)
		]
		
	def about_page(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			ARTICLES.getArticleByNumber(0,lindex)
		]
		
	def teammanagercloud_page(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			HELPER.getTMCContent(lindex)
		]
		
	def calc_page(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			HELPER.getCalcContent(lindex)
		]
		
	def home_page(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			new_home_page(lindex)
		]
		
	def downloads_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			html.Br(),
			ARTICLES.Downloads(lindex)
		]

	def donate_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			html.Br(),
			ARTICLES.DonateDescription(lindex),
			HELPER.donate_button()
		]

	def card_builder_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,lang_index=lindex),
			HELPER.getMainSideBar(lindex),
			html.Br(),
			get_card_builder(lindex)
		]
		
	def settings_layout(lindex=0):
		return [
			HELPER.getHeader(g.user,True,lindex), #is_settings_page
			HELPER.getMainSideBar(lindex),
			HELPER.getSettingsContent(g.user,lindex)
		]
		
	def shutdown():
		return html.Div(id='shutdown', children=["Shutdown Server"])

	def main(self):
		app.layout = html.Div([
			dcc.Store(id="hidden-time-output",data=0),
			dcc.Store(id="hidden-time-input", data=0),
			dcc.Store(id="hidden-language-output",storage_type='local',data=0),
			#dcc.Store(id="hidden-language-input", data=0),
			dcc.Location(id='url', refresh=True),
			html.Div(id='page-content', className="w3-black"),
			html.Footer(id='footer-content')
			#html.Footer("This content is in no way approved, endorsed, sponsored, or connected to South Park Digital Studios, Ubisoft, RedLynx, or associated/affiliated entities, nor are these entities responsible for this content.", className="w3-black")
		], className="w3-black")
		
		#Dash only
		#app.run_server(port=8000,host='0.0.0.0',debug=False)
		#Flask -> Dash
		#server.run(port=8000,host='0.0.0.0',debug=False)
		#Waitress -> Flask -> Dash
		#serve(server, host='0.0.0.0', port=8000, threads=6)
		
		#CherryPy -> Flask -> Dash
		# Mount the application
		global server
		cherrypy.tree.graft(server, "/")

		# Unsubscribe the default server
		cherrypy.server.unsubscribe()
		
		# Instantiate a new server object
		cserver = cherrypy._cpserver.Server()

		# Configure the server object
		cserver.socket_host = "0.0.0.0"
		cserver.socket_port = 443
		cserver.thread_pool = 100
		cherrypy.config.update({'engine.autoreload.on': False,
							'tools.sessions.timeout': 10,
							'log.access_file': './access.log',
							'log.error_file': './error.log'})

		# For SSL Support
		# server.ssl_module            = 'pyopenssl'
		cserver.ssl_certificate       = 'domain.cert.pem'
		cserver.ssl_private_key       = 'private.key.pem'
		# server.ssl_certificate_chain = 'ssl/bundle.crt'

		# Subscribe this server
		cserver.subscribe()
		
		# Example for a 2nd server (same steps as above):
		# Remember to use a different port
		server2             = cherrypy._cpserver.Server()

		server2.socket_host = "0.0.0.0"
		server2.socket_port = 8000
		server2.thread_pool = 1
		server2.subscribe()

		# Start the server engine (Option 1 *and* 2)
		cherrypy.engine.start()
		#cherrypy.engine.block()
		
		#After updating libraries, expect plenty of `dash.exceptions.DependencyException`
		#	due to caching, and people not refreshing their page.

if __name__ == '__main__':
	sppdsim=SPPDSIM()
	sppdsim.main()