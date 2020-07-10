#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import requests

from pyamf.remoting import STATUS_OK

import time
import socket
import threading
import json
import select
from html.parser import HTMLParser

from .data.item_interaction import ItemInteraction
from .data.item_properties import ItemProperties
from .data.ctxt_server import CtxtServer
from .data.ctxt_room import CtxtRoom
from .data.env import EnvUser, EnvItem, EnvMisc
from .data.transfer import TrRoomJoin, TrRoomLeave, TrRoomReject
from .data.chat import ChatUsr, ChatSrv
from .data.action import ActionUpdateWob, ActionThrow
from .data.list_cmd import MayVote
from .data.interaction import InteractionData
from .data.shop_item import ShopItem
from .net.amf_api import AmfAPI
from .animation import AnimationManager
from .animation.movement import MovementWayPoint
from .net.utf_message import UtfMessage
from .iso import Status
from .iso.player import Player
from .iso.item import IsoItem
from .iso.wob_registry import WOBRegistry
from .media.resource_manager import RESOURCE_MANAGER
from .media.level import Level

BrowserInfo = {
	'browser': 'Chrome',
	'version': 82,
	'OS': 'Windows'
}

Capabilities = {
	'os': 'Windows 10',
	'version': 'WIN 32,0,0,344'
}

class TargetPicker:

	WOBID_INV = 1
	WOBID_ROOM = 2
	UVZ_FLOORED = 4
	UVZ = 8
	
class Event:
	
	PING = 0
	LOGOUT = 1
	LOGIN = 2
	CTXT_SERVER = 3
	CTXT_ROOM = 4
	ENV_USER = 5
	ENV_EXIT = 6
	ENV_ITEM = 7
	ENV_STAT = 8
	ENV_MISC = 9
	ENV_BRIGHTNESS = 10
	ENV_REMOVE_ITEMS = 11
	ENV_ROOM_TOPIC = 12
	ENV_WOB_PROPERTIES = 13
	TR_ROOM_JOIN = 14
	TR_ROOM_LEAVE = 15
	TR_ROOM_REJECT = 16
	CHAT_USR = 17
	CHAT_SRV = 18
	ACTION_SHOW_METROMAP = 19
	ACTION_ROOM_HOP = 20
	ACTION_SPGAME = 21
	ACTION_UPDATE_WOB = 22
	ACTION_OPEN_LOCKER = 23
	ACTION_OPEN_SHOP = 24
	ACTION_OPEN_APARTMENT_LIST = 25
	ACTION_THROW = 26
	NOTIFY_ONL_STAT = 27
	NOTIFY_CREATE_ITEM = 28
	NOTIFY_INVENTORY = 29
	NOTIFY_COINS_OR_BILLS = 30
	NOTIFY_STREAM = 31
	NOTIFY_MAIL = 32
	NOTIFY_ITEMUPDATE = 33
	NOTIFY_STICKIES = 34
	NOTIFY_BADGE = 35
	NOTIFY_LEVEL = 36
	NOTIFY_ITEM_INBOX = 37
	NOTIFY_MODEL_UPDATE = 38
	DATA_GENERAL = 39
	COMMAND_REFRESH_IGNORES = 40
	SET_HAND_HELD = 41
	CLEAR_HAND_HELD = 42
	OPEN_BUY_ITEM_VIEW = 43
	SHOW_TIMER_BAR = 44
	SHOW_ACTION_FEEDBACK = 45
	SRV_OFFER_HINT = 46
	SRV_SHOW_HINT = 47
	CLOSE_ROOM_HOP_MENU = 48
	OPEN_LIST_RECIPES_BY_INGREDIENT_VIEW = 49
	OPEN_CRAFT_RECIPE_VIEW = 50
	COM_MAY_VOTE = 51
	NOTIFY_CREDIT_ACCOUNT = 52
	OPEN_QUEST_VIEW = 53
	OPEN_QUEST_COMPLETED_VIEW = 54
	UPDATE_ROOMITEM_MENU = 55

class Freggers:
	
	VERSION = '20190130-160700phi'
	BROWSER = BrowserInfo['browser'] + ' ' + str(BrowserInfo['version'])
	
	GENDER_MALE = 'male'
	GENDER_FEMALE = 'female'

	SEND_LIVE_STATS = False
	LIVE_STATS = False
	STAT_UPDATE_INTERVAL = 60
	
	TOUCH_INTERVAL = 300
	AUTO_RECONNECT_TIME = 10
	LOOP_INTERVAL = 0.02
	
	PING = 256
	COM_LOGOUT = 0
	COM_LOGIN = 1
	COM_CONTEXT = 160
	COM_ENV = 10
	COM_TRANSFER = 3
	COM_MOVE = 4
	USER_COMMAND_WRAPPER = 5
	COM_CHAT = 16
	COM_MAND = 17
	COM_ACTION = 18
	COM_NOTIFY = 19
	COM_DATA = 208
	COM_MAY_VOTE = 106
	COM_VOTE = 105
	SET_HAND_HELD = 80
	CLEAR_HAND_HELD = 81
	USE_HAND_HELD_WITH = 82
	REQUEST_CLEAR_HAND_HELD = 83
	OPEN_BUY_ITEM_VIEW = 84
	SHOW_TIMER_BAR = 85
	SHOW_ACTION_FEEDBACK = 86
	SRV_OFFER_HINT = 87
	SRV_SHOW_HINT = 88
	REQUEST_HINT = 89
	CLOSE_ROOM_HOP_MENU = 96
	OPEN_LIST_RECIPES_BY_INGREDIENT_VIEW = 99
	OPEN_CRAFT_RECIPE_VIEW = 104
	NOTIFY_CREDIT_ACCOUNT = 109
	OPEN_QUEST_VIEW = 110
	OPEN_QUEST_COMPLETED_VIEW = 111
	UPDATE_ROOMITEM_MENU = 112
	CTXT_ROOM = 1
	CTXT_SERVER = 15
	ENV_USER = 0
	ENV_EXIT = 1
	ENV_ITEM = 2
	ENV_MISC = 3
	ENV_BRIGHTNESS = 4
	ENV_REMOVE_ITEMS = 5
	ENV_ROOM_TOPIC = 6
	ENV_WOB_PROPERTIES = 7
	ENV_STAT = 15
	TR_ROOM_JOIN = 0
	TR_ROOM_LEAVE = 1
	TR_ROOM_REJECT = 2
	CHAT_USR = 0
	CHAT_SRV = 15
	MOVE_DIR = 0
	MOVE_WALKTO = 1
	MOVE_AUTOWALK = 2
	MOVE_AUTOWALK_EXACT = 3
	MOVE_POSUPD = 15
	MAND_USER = 0
	MAND_REFRESHIGNORES = 16
	MAND_ADMIN = 15
	ACTION_INTERACT = 3
	ACTION_SELDEFMENU = 2
	ACTION_SHOW_METROMAP = 10
	ACTION_ROOM_HOP = 11
	ACTION_OPEN_LOCKER = 13
	ACTION_OPEN_SHOP = 14
	ACTION_SPGAME = 15
	ACTION_THROW = 35
	ACTION_UPDATE_WOB = 48
	ACTION_LIFT_OBJ = 64
	ACTION_PLACE_OBJ = 65
	ACTION_OPEN_APARTMENT_LIST = 174
	COMPOSING_IDLE = 0
	COMPOSING_WRITING = 1
	DATA_GENERAL = 0
	ANIM_PLAYER = 0
	ANIM_OBJECT = 1
	NOTIFY_ONL_STAT = 0
	NOTIFY_STREAM = 1
	NOTIFY_MAIL = 2
	NOTIFY_INVENTORY = 3
	NOTIFY_COINS_OR_BILLS = 4
	NOTIFY_ITEMUPDATE = 5
	NOTIFY_STICKIES = 6
	NOTIFY_BADGE = 7
	NOTIFY_LEVEL = 8
	NOTIFY_CREATE_ITEM = 9
	NOTIFY_ITEM_INBOX = 10
	NOTIFY_MODEL_UPDATE = 11
	REASON_NORMAL = 0
	REASON_KICKED = 1
	REASON_THROWN_OUT_BY_COPY = 2
	ANIM_KEYVAL_PLAY = 1
	ANIM_KEYVAL_MODE = 2
	ANIM_KEYVAL_MILLIS = 3
	ANIM_KEY_PLAY = "play"
	ANIM_KEY_MODE = "mode"
	ANIM_KEY_MILLIS = "millis"
	COMPONENT_INIT = 0
	COMPONENT_MCALL = 1
	COMPONENT_TYPE_ROOM = 0
	COMPONENT_TYPE_OBJ = 1
	COMPONENT_TYPE_OVRL = 2
	
	INBOX_ACTION_ACCEPT = 'accept'
	INBOX_ACTION_DECLINE = 'decline'
	
	def __init__(self, localeItems, log_prefix = '[Freggers]', is_debug = False):
		self.localeItems = localeItems
		self.is_debug = is_debug
		self.log_prefix = log_prefix
		self._session = requests.Session()
		self._session.cookies.set_cookie(requests.cookies.create_cookie(name = 'cookie_enabled_check', value = 'enabled', domain = localeItems.DOMAIN, path = '/'))
		self.__connected = False
		self.__list_buffers = {}
		self.__in_msg = UtfMessage()
		self.__room_context_id = 0
		self.__last_client_send = 0
		self.__expect_disconnect = False
		self.__client_event_callbacks = {}
		self.__e_movement_finished = threading.Event()
		self.__e_exits_loaded = threading.Event()
		self.__event_listeners = {
			Event.PING: threading.Event(),
			Event.LOGOUT: threading.Event(),
			Event.LOGIN: threading.Event(),
			Event.CTXT_SERVER: threading.Event(),
			Event.CTXT_ROOM: threading.Event(),
			Event.ENV_USER: threading.Event(),
			Event.ENV_EXIT: threading.Event(),
			Event.ENV_ITEM: threading.Event(),
			Event.ENV_STAT: threading.Event(),
			Event.ENV_MISC: threading.Event(),
			Event.ENV_BRIGHTNESS: threading.Event(),
			Event.ENV_REMOVE_ITEMS: threading.Event(),
			Event.ENV_ROOM_TOPIC: threading.Event(),
			Event.ENV_WOB_PROPERTIES: threading.Event(),
			Event.TR_ROOM_JOIN: threading.Event(),
			Event.TR_ROOM_LEAVE: threading.Event(),
			Event.TR_ROOM_REJECT: threading.Event(),
			Event.CHAT_USR: threading.Event(),
			Event.CHAT_SRV: threading.Event(),
			Event.ACTION_SHOW_METROMAP: threading.Event(),
			Event.ACTION_ROOM_HOP: threading.Event(),
			Event.ACTION_SPGAME: threading.Event(),
			Event.ACTION_UPDATE_WOB: threading.Event(),
			Event.ACTION_OPEN_LOCKER: threading.Event(),
			Event.ACTION_OPEN_SHOP: threading.Event(),
			Event.ACTION_OPEN_APARTMENT_LIST: threading.Event(),
			Event.ACTION_THROW: threading.Event(),
			Event.NOTIFY_ONL_STAT: threading.Event(),
			Event.NOTIFY_CREATE_ITEM: threading.Event(),
			Event.NOTIFY_INVENTORY: threading.Event(),
			Event.NOTIFY_COINS_OR_BILLS: threading.Event(),
			Event.NOTIFY_STREAM: threading.Event(),
			Event.NOTIFY_MAIL: threading.Event(),
			Event.NOTIFY_ITEMUPDATE: threading.Event(),
			Event.NOTIFY_STICKIES: threading.Event(),
			Event.NOTIFY_BADGE: threading.Event(),
			Event.NOTIFY_LEVEL: threading.Event(),
			Event.NOTIFY_ITEM_INBOX: threading.Event(),
			Event.NOTIFY_MODEL_UPDATE: threading.Event(),
			Event.DATA_GENERAL: threading.Event(),
			Event.COMMAND_REFRESH_IGNORES: threading.Event(),
			Event.SET_HAND_HELD: threading.Event(),
			Event.CLEAR_HAND_HELD: threading.Event(),
			Event.OPEN_BUY_ITEM_VIEW: threading.Event(),
			Event.SHOW_TIMER_BAR: threading.Event(),
			Event.SHOW_ACTION_FEEDBACK: threading.Event(),
			Event.SRV_OFFER_HINT: threading.Event(),
			Event.SRV_SHOW_HINT: threading.Event(),
			Event.CLOSE_ROOM_HOP_MENU: threading.Event(),
			Event.OPEN_LIST_RECIPES_BY_INGREDIENT_VIEW: threading.Event(),
			Event.OPEN_CRAFT_RECIPE_VIEW: threading.Event(),
			Event.COM_MAY_VOTE: threading.Event(),
			Event.NOTIFY_CREDIT_ACCOUNT: threading.Event(),
			Event.OPEN_QUEST_VIEW: threading.Event(),
			Event.OPEN_QUEST_COMPLETED_VIEW: threading.Event(),
			Event.UPDATE_ROOMITEM_MENU: threading.Event()
		}
		self.wob_registry = WOBRegistry()
		self.animation_manager = AnimationManager()
		self.exits = []
		self.room = None
		self.player = None
		self.hand_held = None
		self.log('Freggers Client initialized.')
	
	class ModelData:

		def __init__(self, hairColor, bodyColor, eyeColor, gender):
			self.hairColor = hairColor

	def log(self, *args):
		print('[i]', self.log_prefix, *args)
	
	def debug(self, *args):
		if self.is_debug:
			print('[d]', self.log_prefix, *args)
	
	def register_callback(self, event, callback):
		callbacks = self.__client_event_callbacks.get(event)
		if callbacks == None:
			callbacks = []
			self.__client_event_callbacks[event] = callbacks
		callbacks.append(callback)
	
	def unregister_callback(self, event, callback):
		callbacks = self.__client_event_callbacks.get(event)
		if callbacks != None:
			try:
				callbacks.remove(callback)
				return True
			except ValueError:
				return False
		return False
	
	def is_logged_in(self):
		for cookie in self._session.cookies:
			if cookie.name == 'session1':
				return True
		return False
	
	def init_session(self, username, password):
		req1 = self._session.post(self.localeItems.URL + '/ajax_login', data = {
			'login': username,
			'pass': password
		})
		if req1.status_code == 200:
			req2 = self._session.get(self.localeItems.URL + '/home?popup=no&skip_confirm_warning=1;skip_nomail_notice=1')
			if req2.status_code == 200:
				html = req2.text
				
				params = {}
				
				index = 0
				lim = html.find('RoomDisplay.swf')
				while True:
					start = html.find('flashvars.', index, lim)
					if start == -1:
						break
					start += 10
					end = html.find('=', start)
					key = html[start:end]
					start = html.find('"', end)
					start += 1
					end = html.find('"', start)
					value = html[start:end]
					params[key] = value.replace('\\', '')
					index = end + 1
				
				self.params = params
				
				userid_start = html.find('"', html.find(',', html.find('SponsorPay.init('))) + 1
				userid_end = html.find('"', userid_start)
				
				if userid_start != 0:
					self.user_id = html[userid_start:userid_end]
					self.log('User ID:', self.user_id)
		
		return self.is_logged_in()
	
	def __ajax_request_bag(self, url, container_id):
		resp = self._session.get(url)
		if resp.status_code == 200:
			resp_txt = resp.text
			if resp_txt.find('--JSON--') != -1:
				obj = json.loads(resp_txt[8:])
				data = obj['data'][container_id]
				parser = Freggers.InventoryParser()
				parser.feed(data)
				result = parser.get_result()
				return result
			else:
				self.log('Could not request inventory:', resp_txt)
	
	def ajax_request_inventory(self):
		return self.__ajax_request_bag(self.localeItems.URL + '/sidebar/inventory/ajax_render_bag?user_id=' + self.user_id, '#iv-bags')
	
	def ajax_request_locker(self):
		return self.__ajax_request_bag(self.localeItems.URL + '/sidebar/locker/ajax_render_locker', '#iv-locker')
	
	def ajax_request_item_queue(self):
		resp = self._session.get(self.localeItems.URL + '/sidebar/inventory/ajax_render_inbox_items?user_id=' + self.user_id)
		if resp.status_code == 200:
			resp_txt = resp.text
			if resp_txt.find('--JSON--') != -1:
				obj = json.loads(resp_txt[8:])
				data = obj['data']['#iv-gifts']
				parser = Freggers.InventoryQueueParser()
				parser.feed(data)
				result = parser.get_result()
				return result
			else:
				self.log('Could not request inventory:', resp_txt)
	
	def ajax_inbox_action(self, item_id, action):
		resp = self._session.post(self.localeItems.URL + '/sidebar/inventory/ajax_inbox_action', {
			'item_id': item_id,
			'action': action,
			'session_id': self.params['sessionid']
		})
		return resp.status_code == 200
	
	def ajax_item_edit(self, item_id, cmd):
		resp = self._session.post(self.localeItems.URL + '/sidebar/inventory/ajax_edit_item', {
			'id': item_id,
			'cmd': cmd,
			'session_id': self.params['sessionid']
		})
		return resp.status_code == 200
	
	def ajax_item_interact(self, item_id, interaction):
		resp = self._session.post(self.localeItems.URL + '/sidebar/inventory/ajax_item_interact', {
			'id': item_id,
			'interaction': interaction,
			'session_id': self.params['sessionid']
		})
		return resp.status_code == 200
	
	#hairdye_slot: 1, 2, 3
	def ajax_use_hairdye(self, item_id, hairdye_slot):
		return self.ajax_item_interact(item_id, 'HAIRDYE' + str(hairdye_slot))
	
	def ajax_delete_item(self, item_id):
		return self.ajax_item_edit(item_id, 'delete')
	
	def ajax_deposit_item(self, item_id):
		return self.ajax_item_edit(item_id, 'deposit')
	
	def ajax_withdraw_item(self, item_id):
		return self.ajax_item_edit(item_id, 'withdraw')
	
	def ajax_buy_item(self, relation_id, price):
		resp = self._session.post(self.localeItems.URL + '/sidebar/shop/ajax_buy_item', {
			'relation_id': relation_id,
			'coins': price,
			'session_id': self.params['sessionid']
		})
		return resp.status_code == 200
	
	def ajax_item_menu(self, item_id, reason):
		resp = self._session.get(self.localeItems.URL + '/sidebar/inventory/ajax_item_menu?item_id=' + item_id + '&reason=' + reason)
		if resp.status_code == 200:
			resp_txt = resp.text.strip()
			if resp_txt.startswith('--JSON--'):
				return json.loads(resp_txt[8:])
	
	def item_menu_cbdata(self, item_menu):
		if 'callback' in item_menu:
			return json.loads(item_menu['callback'][1:-1])
		return None
	
	def item_menu_interactions(self, item_menu):
		if 'data' in item_menu:
			return json.loads(item_menu['data'])
		return None
	
	def ajax_item_usewith(self, item_id, target):
		resp = self._session.post(self.localeItems.URL + '/sidebar/inventory/ajax_item_usewith', {
			'item_id_a': item_id,
			'target': target,
			'room_context': self.room.room_context_label,
			'session_id': self.params['sessionid']
		})
		return resp.status_code == 200
	

	#Firstname max length: 100
	#City max length: 50
	#Homepage max length: 255
	#Homepage/Email visibility values: all, loggedin, friends, nobody
	#Messages from values: all, friends
	def ajax_edit_profile(self, first_name, birth_day, birth_month, birth_year, country, city, homepage, homepage_visibility, email_visibility, allow_messages_from):
		resp = self._session.post(self.localeItems.URL + '/sidebar/profile/ajax_edit_form', {
			'_brix_detect_charset': '€ ´ ü',
			'session_id': self.params['sessionid'],
			'progress': 1,
			'firstname': first_name,
			'birth-day': birth_day,
			'birth-month': birth_month,
			'birth-year': birth_year,
			'country': country,
			'city': city,
			'homepage': homepage,
			'visib_homepage': homepage_visibility,
			'visib_email': email_visibility,
			'allow_message_from': allow_messages_from
		})
		return resp.status_code == 200

	def request_apartment_list(self, room_label):
		resp = self._session.get(self.localeItems.URL + '/sidebar/apartment/index?room_context_label=' + room_label)
		if resp.status_code == 200:
			resp_txt = resp.text
			me_id = self.user_id
			user_ids = []
			i = resp_txt.find('plattenbau.eigenheim#@#')
			while i != -1:
				i += len('plattenbau.eigenheim#@#')
				end = resp_txt.find('"', i)
				owner_id = resp_txt[i:end]
				i = end + 1
				if owner_id != me_id:
					user_ids.append(owner_id)
				i = resp_txt.find('plattenbau.eigenheim#@#', i)
			return user_ids
	
	class InventoryParser(HTMLParser):
		
		def __init__(self):
			self.__result = []
			self.__level = 0
			self.__item = None
			self.__expect_item_count = False
			self.__expect_item_desc = False
			super(Freggers.InventoryParser, self).__init__()
		
		def handle_starttag(self, tag, attrs):
			if tag == 'div':
				self.__level += 1
				for attr_name, attr_value in attrs:
					if attr_name == 'id' and attr_value.startswith('iv-item-'):
						self.__item = {
							'id': attr_value[8:],
							'count': 1
						}
						break
					elif self.__item != None and attr_name == 'class':
						if attr_value == 'iv-item-count':
							self.__expect_item_count = True
							break
						elif attr_value == 'iv-item-desc':
							self.__expect_item_desc = True
							break
					elif attr_name == 'class':
						if 'iv-slot-empty' in attr_value:
							self.__result.append(None)
			elif tag == 'img':
				if self.__item != None:
					for attr_name, attr_value in attrs:
						if attr_name == 'src':
							self.__item['imgurl'] = attr_value
							break
		
		def handle_data(self, data):
			if self.__expect_item_count:
				self.__item['count'] = int(data)
				self.__expect_item_count = False
			elif self.__expect_item_desc:
				self.__item['description'] = data
				self.__expect_item_desc = False
		
		def handle_endtag(self, tag):
			if tag == 'div':
				if self.__level == 3 and self.__item != None:
					self.__result.append(self.__item)
					self.__item = None
				self.__level -= 1
		
		def get_result(self):
			return self.__result
			
	class InventoryQueueParser(HTMLParser):
		
		def __init__(self):
			self.__result = []
			self.__item = None
			super(Freggers.InventoryQueueParser, self).__init__()
		
		def handle_starttag(self, tag, attrs):
			if tag == 'div':
				for attr_name, attr_value in attrs:
					if attr_name == 'id' and attr_value.startswith('iv-item-'):
						self.__item = {
							'id': attr_value[8:]
						}
						break
			elif tag == 'img':
				if self.__item != None:
					for attr_name, attr_value in attrs:
						if attr_name == 'src':
							self.__item['imgurl'] = attr_value
						elif attr_name == 'title':
							self.__item['description'] = attr_value
					self.__result.append(self.__item)
					self.__item = None
		
		def get_result(self):
			return self.__result
	
	def boot(self):
		self.amf_api = AmfAPI(self.params["amfgw"], session = self._session)
		self.__host = self.params["host"]
		self.__port = int(self.params["port"])
		
		live_stats = int(self.params["livestats"])
		if live_stats > 0 and Freggers.SEND_LIVE_STATS:
			Freggers.LIVE_STATS = True
			Freggers.STAT_UPDATE_INTERVAL = live_stats
		
		self.log('Freggers Client booted up')
		
		self.post_init()
	
	def post_init(self):
		self._logged_in_at = self._stats_sent_at = time.time()
		self.connect_client()
		
		threading.Thread(target = self.__handle_data).start()
		threading.Thread(target = self.__main_loop).start()
		
		RESOURCE_MANAGER.configure(self.params)
		
		if self.params["hasofferitems"] != None:
			self.log('Requesting daily offer item...')
			self.daily_offer = self.get_daily_offer()
		
		self.log('Freggers Client post-initialized')
	
	def connect_client(self):
		if self.__connected:
			self.disconnect()
		self.connect()
	
	def connect(self):
		if not self.__connected:
			self.__sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
			self.__sock.settimeout(310)
			self.__sock.connect((self.__host, self.__port))
			self.__connected = True
			self.__last_client_send = time.time()
			
			self.send_login()
			self.__remote_log('OK', 'CONNECTION', 'Connection established to {}:{} at handleConnect'.format(self.__host, self.__port))
	
	def disconnect(self):
		self.__close_socket()
		self.__in_msg.reset(True)
	
	def reconnect(self):
		self.disconnect()
		self.connect()
	
	def __close_socket(self):
		self.__remote_log('INFO', 'CONNECTION', 'Connection Closed at handleClose (null)') #param1:Event
		self.set_room_context_id(0)
		if self.__sock == None or not self.__connected:
			return
		self.__connected = False
		self.__sock.close()
		self.__sock = None
	
	def wait_for(self, event):
		self.__event_listeners[event].wait()
	
	def __fire_event(self, event, *args):
		e = self.__event_listeners[event]
		e.set()
		e.clear()
		callbacks = self.__client_event_callbacks.get(event)
		if callbacks != None:
			for cb in callbacks:
				try:
					cb(*args)
				except Exception as e:
					print(e)
	
	def __main_loop(self):
		next_main_loop = 0
		next_stat_send = 0
		
		sprites_len = 30
		
		last_frame = -1
		stat_frames = 0
		total_frames = 0
		total_objects = 0
		frame_dur_sum = 0
		frames = 0
		
		self.animation_manager.start(time.time())
		
		self.log('Freggers Client main loop started.')
		while True:
			if self.__connected:
				now = time.time()
				
				self.animation_manager.update(now)
				
				if last_frame > -1:
					frame_dur_sum += now - last_frame
					frames += 1
				
				if frames >= 30:
					dur_per_frame = round(1000 / (frame_dur_sum / frames * 1000))
					total_frames += dur_per_frame
					total_objects += sprites_len
					stat_frames += 1
					if Freggers.LIVE_STATS and next_stat_send <= now:
						next_stat_send = now + Freggers.STAT_UPDATE_INTERVAL
						self.log('Sending live stats...')
						self.amf_api.call(AmfAPI.SEND_STATS, args = [Freggers.VERSION, 
																	 int(now - self._logged_in_at + 0.5), 
																	 int(total_frames / stat_frames + 0.5), 
																	 int(total_objects / stat_frames + 0.5), 
																	 Capabilities['os'], 
																	 Capabilities['version'], 
																	 Freggers.BROWSER, 
																	 800, 
																	 500])
						
						stat_frames = total_frames = total_objects = 0
					frames = frame_dur_sum = 0
					
				if next_main_loop <= now:
					next_main_loop = now + Freggers.LOOP_INTERVAL
					
					self.__update()
				
				last_frame = now
				time.sleep(0.05)
			else:
				time.sleep(0.25)
	
	def __update(self):
		if time.time() - self.__last_client_send >= Freggers.TOUCH_INTERVAL:
			self.send_touch()
	
	def set_room_context_id(self, val):
		self.__room_context_id = val
	
	def is_connected(self):
		return self.__connected
	
	def __send_raw(self, utfmsg):
		sent_bytes = utfmsg.send(self.__sock)
		if sent_bytes > 0:
			self.__last_client_send = time.time()
		self.debug('Sent RAW message ({} bytes):'.format(sent_bytes))
		self.debug(utfmsg.dump(name = 'O'))
		return sent_bytes
	
	def __send(self, utfmsg):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.USER_COMMAND_WRAPPER, self.__room_context_id])
		msg.add_message_arg(utfmsg)
		return self.__send_raw(msg)
		
	def send_room_loaded(self, room_gui, wob_id):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_CONTEXT, Freggers.CTXT_ROOM])
		msg.add_string_arg(room_gui)
		msg.add_int_arg(wob_id)
		return self.__send(msg)
	
	def send_login(self):
		msg = UtfMessage()
		msg.add_int_arg(Freggers.COM_LOGIN)
		msg.add_string_arg(self.params["username"])
		msg.add_string_arg(self.params["sessionid"])
		return self.__send_raw(msg)
	
	def send_touch(self):
		return self.__send_raw(UtfMessage())
	
	def send_ping(self):
		msg = UtfMessage()
		msg.add_int_arg(Freggers.PING)
		msg.add_int_arg(10)
		return self.__send_raw(msg)
	
	#0: default
	#1: /me
	#2: /think
	#3: /shout
	#4: /w
	def send_chat(self, txt_msg, context = 0):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_CHAT, Freggers.CHAT_USR, 0])
		msg.add_string_arg(txt_msg)
		msg.add_int_arg(context)
		return self.__send(msg)
	
	#key: Freggers.STAT_KEY_IDLE -> status : int
	#key: Freggers.STAT_KEY_COMPOSING -> status : int
	#key: Freggers.STAT_KEY_AWAY -> status : string
	def send_set_status(self, key, status = None):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_ENV, Freggers.ENV_STAT, 1])
		msg.add_int_arg(key)
		if status != None:
			if key == Status.COMPOSING or key == Status.IDLE:
				msg.add_int_arg(status)
			else:
				msg.add_string_arg(status)
		return self.__send(msg)
	
	def send_delete_status(self, key):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_ENV, Freggers.ENV_STAT, 0])
		msg.add_int_arg(key)
		return self.__send(msg)
		
	def send_direction(self, dir):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_MOVE, Freggers.MOVE_DIR])
		msg.add_int_arg(dir)
		return self.__send(msg)
	
	#str is never used in the original code
	def send_move_on_ground_to(self, x, y, z, str = None):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_MOVE, Freggers.MOVE_WALKTO])
		msg.add_int_list_arg([x, y, z])
		if str != None:
			msg.add_string_arg(str)
		self.__e_movement_finished.clear()
		return self.__send(msg)
	
	def wait_movement_finished(self):
		self.__e_movement_finished.wait()

	def wait_exits_loaded(self):
		self.__e_exits_loaded.wait()

	#b1 unknown
	def send_auto_walk_to(self, room_gui, b1 = True, exact = False):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_MOVE, Freggers.MOVE_AUTOWALK_EXACT if exact else Freggers.MOVE_AUTOWALK])
		msg.add_string_arg(room_gui)
		msg.add_boolean_arg(b1)
		return self.__send(msg)
	
	def send_item_interaction(self, wob_id, interaction, position = None):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_ACTION, Freggers.ACTION_INTERACT])
		msg.add_int_arg(wob_id)
		msg.add_string_arg(interaction)
		if position != None and len(position) == 3:
			msg.add_int_list_arg(position)
		self.__send(msg)
	
	def send_show_metroplan(self):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_ACTION, Freggers.ACTION_SHOW_METROMAP])
		return self.__send(msg)
	
	def send_user_command(self, command):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_MAND, Freggers.MAND_USER])
		msg.add_string_arg(command)
		return self.__send(msg)
	
	#"warn","kick","skick"
	def send_admin_command(self, command):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_MAND, Freggers.MAND_ADMIN])
		msg.add_string_arg(command)
		return self.__send(msg)
	
	def send_use_handheld_with(self, wob_id):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.USE_HAND_HELD_WITH])
		msg.add_int_arg(wob_id)
		return self.__send(msg)
	
	def send_clear_handheld(self):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.REQUEST_CLEAR_HAND_HELD])
		return self.__send(msg)
	
	def send_pickup_object(self, wob_id):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_ACTION, Freggers.ACTION_LIFT_OBJ])
		msg.add_int_list_arg([wob_id])
		return self.__send(msg)
	
	def send_place_object(self, x, y, z, direction):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_ACTION, Freggers.ACTION_PLACE_OBJ])
		msg.add_int_list_arg([x, y, z, direction])
		return self.__send(msg)
	
	def send_room_hop_command(self, exit_label):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_ACTION, Freggers.ACTION_ROOM_HOP])
		msg.add_string_arg(exit_label)
		return self.__send(msg)
	
	def send_request_hint(self):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.REQUEST_HINT])
		return self.__send(msg)
	
	def send_vote(self):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_VOTE])
		return self.__send(msg)
	
	def send_logout(self):
		msg = UtfMessage()
		msg.add_int_list_arg([Freggers.COM_LOGOUT])
		return self.__send(msg)
	
	def logout(self, reason = 0):
		def cb(data):
			self.log('Disconnecting...')
			self.disconnect()
			self.log('Disconnected.')
			self.log('Logging out... ({})'.format(data))
			self._session.get(self.localeItems.URL + '/logout?r=' + str(reason) + ';session_id=' + self.params["sessionid"])
			self.log('Logged out.')
		if reason == 2:
			self.__remote_log('ERROR', 'COOKIEJAR', 'User already logged in on system.', cb)
		else:
			cb(reason)
	
	def craft_item(self, recipe_id, fee, buy):
		form_data = {
			'_brix_detect_charset': '€ ´ ü',
			'session_id': self.params['sessionid'],
			'recipe_id': recipe_id,
			'buy': buy
		}
		if fee != None:
			form_data['fee'] = fee
		return self._session.post(self.localeItems.URL + '/sidebar/crafting/craft_recipe', form_data).status_code == 200
	
	def unlock_crafting_category(self, category_id):
		return self._session.post(self.localeItems.URL + '/sidebar/crafting/category', {
			'_brix_detect_charset': '€ ´ ü',
			'session_id': self.params['sessionid'],
			'category_id': category_id,
			'unlock_category': 1
		}).status_code == 200
	
	def __process_list_cmd(self, utfmsg, clazz):
		index = utfmsg.get_int_list_arg(0)[1]
		list_cmd = self.__list_buffers.get(index)
		if list_cmd == None:
			list_cmd = clazz()
			self.__list_buffers[index] = list_cmd
		list_cmd.feed(utfmsg)
		if list_cmd.is_complete():
			del self.__list_buffers[index]
			return list_cmd
		self.__list_buffers[index] = list_cmd
		return None
	
	@staticmethod
	def __get_exit_data(utfmsg):
		if utfmsg == None:
			return None
		array = utfmsg.get_int_list_arg(1)
		result = {
			'polygon': utfmsg.get_int_list_arg(0),
			'z': array[0],
			'dir': array[1],
			'wobid': array[2]
		}
		if utfmsg.get_arg_count() > 2:
			result['gui'] = utfmsg.get_string_arg(2)
		return result
	
	def __process_exit_list(self):
		result = {}
		exits = []
		exit_list = self.__list_buffers.get(Freggers.ENV_EXIT)
		if list != None:
			entry_msg = None
			for x in range(len(exit_list)):
				entry_msg = exit_list[x]
				for y in range(2, entry_msg.get_arg_count(), 1):
					exits.append(Freggers.__get_exit_data(entry_msg.get_message_arg(y)))
			result['room'] = entry_msg.get_string_arg(1)
		del self.__list_buffers[Freggers.ENV_EXIT]
		result['exits'] = exits
		self.exits.extend(exits)
		return result
	
	def __handle_env_msg(self, utfmsg):
		array = utfmsg.get_int_list_arg(0)
		if array[1] not in self.__list_buffers:
			self.__list_buffers[array[1]] = []
		self.__list_buffers[array[1]].append(utfmsg.clone())
		return array[2] == 2 or array[2] == 3
	
	@staticmethod
	def __parse_hop_exit_data(utfmsg):
		if utfmsg == None:
			return None
		array = utfmsg.get_int_list_arg(1)
		return {
			'polygon': utfmsg.get_int_list_arg(0),
			'z': array[0],
			'dir': array[1],
			'label': array[2]
		}
	
	def __handle_wob_property_change(self, wob, properties, old_properties):
		pass
	
	def __handle_movement_done(self, animation):
		self.__e_movement_finished.set()

	def __update_wob_data(self, data, force, delay):
		wob = self.wob_registry.get_object_by_wobid(data.wob_id)
		if wob == None:
			return
		if hasattr(data, 'position'):
			pos = data.position
			wob.iso_obj.set_position(pos.u, pos.v, pos.z)
			wob.iso_obj.set_direction(pos.direction)
		elif hasattr(data, 'path') and data.path != None:
			path = data.path
			if path.age() < path.duration:
				pos = path.start
				wob.iso_obj.set_position(pos.u, pos.v, pos.z)
				anim = self.animation_manager.moveground(wob.iso_obj, MovementWayPoint.get_movement_waypoints(path), path.duration, path.age(), self.level, wob)
				if anim != None:
					anim.on_complete = self.__handle_movement_done
			else:
				waypoint_pos = path.waypoints[-1].position
				wob.iso_obj.set_position(waypoint_pos.u, waypoint_pos.v, waypoint_pos.z)
		elif force:
			if self.animation_manager.has_animation(wob.iso_obj):
				self.animation_manager.clear_animation(wob.iso_obj)
				self.__e_movement_finished.set()
			else:
				wob.iso_obj.set_position(0, 0, 0)
	
	def __init_wob_states(self, wob, states):
		if wob == None or states == None:
			return
		wob.clear_states()
		for state_id, state_value in states.items():
			self.__update_wob_state(wob, state_id, state_value, True)
		
	def __update_wob_state(self, wob, state_id, value, enabled):
		if wob == None:
			return
		wob.set_state(state_id, enabled, value)
	
	def __cleanup_iso_object_container(self, iso_object_container):
		pass
	
	def __remove_exits(self):
		self.exits.clear()
	
	def __remove_items(self):
		for iso_item in list(self.wob_registry.iso_items):
			self.__cleanup_iso_object_container(iso_item)
			self.wob_registry.remove(iso_item)
	
	def __remove_player(self, wob_id):
		player = self.wob_registry.get_object_by_wobid(wob_id)
		if player == None:
			return
		self.wob_registry.remove(player)
		if player == self.player:
			self.player = None
		self.__cleanup_iso_object_container(player)
	
	class Property:
		def __init__(self, key, value):
			self.key = key
			self.value = value
		
		def __str__(self):
			return 'Property[key={}, value={}]'.format(self.key, self.value)
		
		def __repr__(self):
			return self.__str__()
	
	@staticmethod
	def create_property(key, value):
		return Freggers.Property(key, value)
	
	@staticmethod
	def create_property_list(map):
		list = []
		for key, value in map.items():
			property = Freggers.create_property(key, value)
			if property != None:
				list.append(property)
		return list
	
	def __add_examine_interaction(self, iso_item):
		interaction = ItemInteraction('DETAILS', '', ItemInteraction.TYPE_SECONDARY)
		iso_item.interactions.append(interaction)
	
	def __handle_data(self):
		self.log('Freggers flash message handler started. Waiting for messages...')
		while True:
			if self.__connected:
				socks_r, _, _ = select.select([self.__sock], [], [])
				if len(socks_r) > 0:
					sock = socks_r[0]
					in_msg = self.__in_msg
					if in_msg.read(sock):
						self.__in_msg = UtfMessage()
						self.__handle_msg(in_msg)
			else:
				time.sleep(0.25)
	
	def __handle_msg(self, msg):
		if self.is_debug:
			self.debug(msg.dump('RECV'))
		if msg.is_prepared() and msg.get_arg_count() > 0:
			com = msg.get_int_list_arg(0)
			if com == None:
				return
			cmd = com[0]
			subcmd = com[1] if len(com) > 1 else None
			if cmd == Freggers.PING:
				self.debug('Com: PING')
				ttl = msg.get_int_arg(1)
				if ttl > 0:
					resp_msg = UtfMessage()
					resp_msg.add_int_arg(Freggers.PING)
					resp_msg.add_int_arg(ttl - 1)
					self.__send_raw(resp_msg)
				self.__fire_event(Event.PING, ttl)
			elif cmd == Freggers.COM_LOGOUT:
				self.debug('Com: COM_LOGOUT')
				self.__expect_disconnect = True
				self.logout(reason = msg.get_int_arg(1))
				self.__fire_event(Event.LOGOUT)
			elif cmd == Freggers.COM_LOGIN:
				self.debug('Com: COM_LOGIN')
				result = msg.get_int_arg(1)
				if result == 0:
					subcmd = result
				self.debug('wobid:',msg.get_int_arg(2))
				self.__fire_event(Event.LOGIN)
			elif cmd == Freggers.COM_CONTEXT:
				if subcmd == Freggers.CTXT_SERVER:
					self.debug('Com: CTXT_SERVER')
					ctxt_svr = CtxtServer(msg)
					self.set_room_context_id(0)
					self.__expect_disconnect = True
					
					self.__host = ctxt_svr.host
					self.__port = ctxt_svr.port
					
					self.connect_client()
					self.__fire_event(Event.CTXT_SERVER)
				elif subcmd == Freggers.CTXT_ROOM:
					self.debug('Com: CTXT_ROOM')
					self.__e_exits_loaded.clear()
					ctxt_room = CtxtRoom(msg)
					
					self.area_name = ctxt_room.room_context_label.split('.',1)[0]
					
					self.room = ctxt_room
					self.set_room_context_id(ctxt_room.wob_id)
					
					self.debug('Loading room {}...'.format(ctxt_room.room_gui))
					
					
					self.level = Level(self.area_name, ctxt_room.gui())
					RESOURCE_MANAGER.request_level(self, self.level, None, False, True)
					
					self.log(ctxt_room.gui(), ctxt_room.wob_id)
					self.send_room_loaded(ctxt_room.gui(), ctxt_room.wob_id)
					
					self.log('Loaded room {}.'.format(ctxt_room.room_gui))
					
					self.__fire_event(Event.CTXT_ROOM, ctxt_room)
			elif cmd == Freggers.COM_ENV:
				if subcmd == Freggers.ENV_USER:
					self.debug('Com: ENV_USER')
					data = self.__process_list_cmd(msg, EnvUser)
					if data != None:
						for player_data in data.get_data():
							player = Player.create_from_data(player_data)
							player.properties_cb = self.__handle_wob_property_change
							if player.name == self.params['username']:
								self.player = player
							self.wob_registry.add(player)
							self.__update_wob_data(player_data, True, 0)
							self.__init_wob_states(player, player_data.status)
						self.__fire_event(Event.ENV_USER, data)
				elif subcmd == Freggers.ENV_EXIT:
					self.debug('Com: ENV_EXIT')
					self.exits.clear()
					if self.__handle_env_msg(msg):
						data = self.__process_exit_list()
						self.__e_exits_loaded.set()
						self.__fire_event(Event.ENV_EXIT, data)
				elif subcmd == Freggers.ENV_ITEM:
					self.debug('Com: ENV_ITEM')
					data = self.__process_list_cmd(msg, EnvItem)
					if data != None:
						if not data.add:
							self.__remove_items()
						list = data.get_data()
						if list != None and len(list) > 0:
							for item_data in list:
								item = self.wob_registry.get_object_by_wobid(item_data.wob_id)
								if item == None:
									item = IsoItem.create_from_data(item_data)
									self.__add_examine_interaction(item)
									item.properties_cb = self.__handle_wob_property_change
									item.num_stickies = 0
									self.wob_registry.add(item)
									self.__update_wob_data(item_data, True, 0)
									self.__init_wob_states(item, item_data.status)
						self.debug('Items:')
						for i, item in enumerate(self.wob_registry.iso_items):
							self.debug('{}: name={} wobid={} gui={} primaryInteraction={} interactions={}'.format(i, item.name, item.wob_id, item.gui, item.get_primary_interaction(), item.interactions))
						self.__fire_event(Event.ENV_ITEM, data)
				elif subcmd == Freggers.ENV_STAT:
					self.debug('Com: ENV_STAT')
					info = msg.get_int_list_arg(1)
					data = {
						'wobid': info[0],
						'userid': info[1],
						'rights': info[2],
						'set': com[2],
						'status': msg.get_int_arg(2)
					}
					if msg.get_arg_count() == 4:
						status = data['status']
						if status == Status.AWAY:
							data['value'] = msg.get_string_arg(3)
						elif status == Status.CARRYING:
							carry_msg = msg.get_message_arg(3)
							if carry_msg == None:
								data['value'] = None
							else:
								data['value'] = {
									'wobid': carry_msg.get_int_arg(0),
									'gui': carry_msg.get_string_arg(1),
									'dir': carry_msg.get_int_arg(2)
								}
						else:
							data['value'] = msg.get_int_arg(3)
					
					wob = self.wob_registry.get_object_by_wobid(data['wobid'])
					if wob != None:
						self.__update_wob_state(wob, data['status'], data['value'], data['set'] == 1)
						self.__fire_event(Event.ENV_STAT, data)
				elif subcmd == Freggers.ENV_MISC:
					self.debug('Com: ENV_MISC')
					data = EnvMisc(msg)
					self.__fire_event(Event.ENV_MISC, data)
				elif subcmd == Freggers.ENV_BRIGHTNESS:
					self.debug('Com: ENV_BRIGHTNESS')
					data = {
						'brightness': msg.get_int_arg(1)
					}
					self.room.brightness = data['brightness']
					self.__fire_event(Event.ENV_BRIGHTNESS, data)
				elif subcmd == Freggers.ENV_REMOVE_ITEMS:
					self.debug('Com: ENV_REMOVE_ITEMS')
					data = {
						'removeall': len(com) >= 4 and com[3] == 1
					}
					if not data['removeall']:
						data['wobids'] = msg.get_int_list_arg(1)
					
					if data['removeall']:
						self.__remove_items()
					else:
						wob_ids = data['wobids']
						for wob_id in wob_ids:
							wob = self.wob_registry.get_object_by_wobid(wob_id)
							if wob != None:
								self.wob_registry.remove(wob)
								self.__cleanup_iso_object_container(wob)
					self.__fire_event(Event.ENV_REMOVE_ITEMS, data)
				elif subcmd == Freggers.ENV_ROOM_TOPIC:
					self.debug('Com: ENV_ROOM_TOPIC')
					data = {
						'topic': msg.get_string_arg(1)
					}
					self.room.topic = data['topic']
					self.__fire_event(Event.ENV_ROOM_TOPIC, data)
				elif subcmd == Freggers.ENV_WOB_PROPERTIES:
					self.debug('Com: ENV_WOB_PROPERTIES')
					data = {
						'wob_id': msg.get_int_arg(1)
					}
					prop_map = {}
					for prop in range(2, msg.get_arg_count(), 1):
						prop_msg = msg.get_message_arg(prop)
						prop_map[prop_msg.get_string_arg(0)] = prop_msg.get_string_arg(1)
					data['prop_map'] = prop_map
					
					wob = self.wob_registry.get_object_by_wobid(data['wob_id'])
					if wob != None:
						wob.set_properties(Freggers.create_property_list(data['prop_map']))
						self.__fire_event(Event.ENV_WOB_PROPERTIES, data)
			elif cmd == Freggers.COM_TRANSFER:
				if subcmd == Freggers.TR_ROOM_JOIN:
					self.debug('Com: TR_ROOM_JOIN')
					data = TrRoomJoin(msg)
					
					player = self.wob_registry.get_object_by_wobid(data.data.wob_id)
					if player == None:
						player = Player.create_from_data(data.data)
						self.wob_registry.add(player)
					self.__update_wob_data(data.data, True, 0)
					self.__init_wob_states(player, data.data.status)
					self.__fire_event(Event.TR_ROOM_JOIN, data)
				elif subcmd == Freggers.TR_ROOM_LEAVE:
					self.debug('Com: TR_ROOM_LEAVE')
					data = TrRoomLeave(msg)
					
					player = self.wob_registry.get_object_by_wobid(data.wob_id)
					if player != None:
						self.__remove_player(data.wob_id)
					self.__fire_event(Event.TR_ROOM_LEAVE, data)
				elif subcmd == Freggers.TR_ROOM_REJECT:
					self.debug('Com: TR_ROOM_REJECT')
					data = TrRoomReject(msg)
					self.__fire_event(Event.TR_ROOM_REJECT, data)
			elif cmd == Freggers.COM_CHAT:
				if subcmd == Freggers.CHAT_USR:
					self.debug('Com: CHAT_USR')
					data = ChatUsr(msg)
					self.debug('CHAT_USR:',data.message,data.wob_id,data.type,data.mode,data.overheard)
					self.__fire_event(Event.CHAT_USR, data)
				elif subcmd == Freggers.CHAT_SRV:
					self.debug('Com: CHAT_SRV')
					data = ChatSrv(msg)
					self.debug('CHAT_SRV:',data.message)
					self.__fire_event(Event.CHAT_SRV, data)
			elif cmd == Freggers.COM_ACTION:
				if subcmd == Freggers.ACTION_SHOW_METROMAP:
					self.debug('Com: ACTION_SHOW_METROMAP')
					data = []
					nodes_msg = msg.get_message_arg(1)
					if nodes_msg == None:
						return
					for x in range(nodes_msg.get_arg_count()):
						node = nodes_msg.get_message_arg(x)
						data.append({
							'label': node.get_string_arg(0),
							'name': node.get_string_arg(1),
							'enabled': node.get_int_arg(2) != 0,
							'usercount': node.get_int_arg(3),
							'context': node.get_string_arg(4)
						})
					self.__fire_event(Event.ACTION_SHOW_METROMAP, data)
				elif subcmd == Freggers.ACTION_ROOM_HOP:
					self.debug('Com: ACTION_ROOM_HOP')
					data = {
						'hop room label': msg.get_string_arg(1)
					}
					list = []
					for x in range(2, msg.get_arg_count(), 1):
						list.append(Freggers.__parse_hop_exit_data(msg.get_message_arg(x)))
					data['exits'] = list
					self.__fire_event(Event.ACTION_ROOM_HOP, data)
				elif subcmd == Freggers.ACTION_SPGAME:
					self.debug('Com: ACTION_SPGAME')
					data = {
						'label': msg.get_string_arg(1)
					}
					self.__fire_event(Event.ACTION_SPGAME, data)
				elif subcmd == Freggers.ACTION_UPDATE_WOB:
					self.debug('Com: ACTION_UPDATE_WOB')
					data = ActionUpdateWob(msg)
					
					self.__update_wob_data(data, False, 0)
					self.__fire_event(Event.ACTION_UPDATE_WOB, data)
				elif subcmd == Freggers.ACTION_OPEN_LOCKER:
					self.debug('Com: ACTION_OPEN_LOCKER')
					data = {
						'userid': msg.get_int_arg(1)
					}
					self.__fire_event(Event.ACTION_OPEN_LOCKER, data)
				elif subcmd == Freggers.ACTION_OPEN_SHOP:
					self.debug('Com: ACTION_OPEN_SHOP')
					data = {
						'shopid': msg.get_int_arg(1)
					}
					self.__fire_event(Event.ACTION_OPEN_SHOP, data)
				elif subcmd == Freggers.ACTION_OPEN_APARTMENT_LIST:
					self.debug('Com: ACTION_OPEN_APARTMENT_LIST')
					data = {
						'label': msg.get_string_arg(1)
					}
					self.__fire_event(Event.ACTION_OPEN_APARTMENT_LIST, data)
				elif subcmd == Freggers.ACTION_THROW:
					self.debug('Com: ACTION_THROW')
					data = ActionThrow(msg)
					self.__fire_event(Event.ACTION_THROW, data)
			elif cmd == Freggers.COM_NOTIFY:
				if subcmd == Freggers.NOTIFY_ONL_STAT:
					self.debug('Com: NOTIFY_ONL_STAT')
					array = msg.get_int_list_arg(1)
					data = {
						'userid': array[0],
						'status': array[1],
						'wobid': array[2],
						'username': msg.get_string_arg(2)
					}
					
					self.__fire_event(Event.NOTIFY_ONL_STAT, data)
				elif subcmd == Freggers.NOTIFY_CREATE_ITEM:
					self.debug('Com: NOTIFY_CREATE_ITEM')
					data = {
						'gui': msg.get_string_arg(1),
						'template_id': msg.get_int_arg(2),
						'dir': msg.get_int_arg(3)
					}
					
					self.__fire_event(Event.NOTIFY_CREATE_ITEM, data)
				elif subcmd == Freggers.NOTIFY_INVENTORY:
					self.debug('Com: NOTIFY_INVENTORY')
					data = {
						'item_container_id': msg.get_int_arg(1),
						'item_id': msg.get_int_arg(2),
						'type': msg.get_int_arg(3)
					}
					
					self.__fire_event(Event.NOTIFY_INVENTORY, data)
				elif subcmd == Freggers.NOTIFY_COINS_OR_BILLS:
					self.debug('Com: NOTIFY_COINS_OR_BILLS')
					array = msg.get_int_list_arg(1)
					data = {
						'coins_delta': array[0],
						'bills_delta': array[1],
						'show_message': msg.get_boolean_arg(2)
					}
					
					self.__fire_event(Event.NOTIFY_COINS_OR_BILLS, data)
				elif subcmd == Freggers.NOTIFY_STREAM:
					self.debug('Com: NOTIFY_STREAM')
					self.__fire_event(Event.NOTIFY_STREAM)
				elif subcmd == Freggers.NOTIFY_MAIL:
					self.debug('Com: NOTIFY_MAIL')
					data = {
						'userid': msg.get_int_arg(1),
						'sender': msg.get_string_arg(2),
						'body': msg.get_string_arg(3)
					}
					
					self.__fire_event(Event.NOTIFY_MAIL, data)
				elif subcmd == Freggers.NOTIFY_ITEMUPDATE:
					self.debug('Com: NOTIFY_ITEMUPDATE')
					data = {
						'wobid': msg.get_int_arg(1)
					}
					
					self.__fire_event(Event.NOTIFY_ITEMUPDATE, data)
				elif subcmd == Freggers.NOTIFY_STICKIES:
					self.debug('Com: NOTIFY_STICKIES')
					array = msg.get_int_list_arg(2)
					data = {
						'wobid': msg.get_int_arg(1),
						'delta': array[0],
						'total': array[1]
					}
					
					self.__fire_event(Event.NOTIFY_STICKIES, data)
				elif subcmd == Freggers.NOTIFY_BADGE:
					self.debug('Com: NOTIFY_BADGE')
					array = msg.get_int_list_arg(1)
					data = {
						'userid': array[0],
						'badgeid': array[1],
						'message': msg.get_string_arg(2),
						'stepComplete': msg.get_boolean_arg(3)
					}
					
					self.__fire_event(Event.NOTIFY_BADGE, data)
				elif subcmd == Freggers.NOTIFY_LEVEL:
					self.debug('Com: NOTIFY_LEVEL')
					array = msg.get_int_list_arg(1)
					data = {
						'level': array[0],
						'xp_total': array[1],
						'xp_current': array[2],
						'xp_cap': array[3],
						'xp_delta': array[4]
					}
					
					self.__fire_event(Event.NOTIFY_LEVEL, data)
				elif subcmd == Freggers.NOTIFY_ITEM_INBOX:
					self.debug('Com: NOTIFY_ITEM_INBOX')
					self.__fire_event(Event.NOTIFY_ITEM_INBOX)
				elif subcmd == Freggers.NOTIFY_MODEL_UPDATE:
					self.debug('Com: NOTIFY_MODEL_UPDATE')
					self.__fire_event(Event.NOTIFY_MODEL_UPDATE)
			elif cmd == Freggers.COM_DATA:
				if subcmd == Freggers.DATA_GENERAL:
					self.debug('Com: DATA_GENERAL')
					data = {
						'objid': msg.get_int_arg(1),
						'datamsg': msg.get_message_arg(2)
					}
					
					self.__fire_event(Event.DATA_GENERAL, data)
			elif cmd == Freggers.COM_MAND:
				if subcmd == Freggers.MAND_REFRESHIGNORES:
					self.debug('Com: COMMAND_REFRESH_IGNORES')
					array = msg.get_int_list_arg(1)
					data = {
						'userid': array[0],
						'action': array[1],
						'username': msg.get_string_arg(2)
					}
					
					self.__fire_event(Event.COMMAND_REFRESH_IGNORES, data)
			elif cmd == Freggers.SET_HAND_HELD:
				self.debug('Com: SET_HAND_HELD')
				data = {
					'gui': msg.get_string_arg(1),
					'count': msg.get_int_arg(2),
					'consumer_wobids': msg.get_int_list_arg(3)
				}
				
				self.hand_held = data
				self.__fire_event(Event.SET_HAND_HELD, data)
			elif cmd == Freggers.CLEAR_HAND_HELD:
				self.debug('Com: CLEAR_HAND_HELD')
				
				self.hand_held = None
				self.__fire_event(Event.CLEAR_HAND_HELD)
			elif cmd == Freggers.OPEN_BUY_ITEM_VIEW:
				self.debug('Com: OPEN_BUY_ITEM_VIEW')
				data = msg.get_int_arg(1)
				self.__fire_event(Event.OPEN_BUY_ITEM_VIEW, data)
			elif cmd == Freggers.SHOW_TIMER_BAR:
				self.debug('Com: SHOW_TIMER_BAR')
				data = msg.get_int_arg(1)
				self.__fire_event(Event.SHOW_TIMER_BAR, data)
			elif cmd == Freggers.SHOW_ACTION_FEEDBACK:
				self.debug('Com: SHOW_ACTION_FEEDBACK')
				data = msg.get_string_arg(1)
				self.__fire_event(Event.SHOW_ACTION_FEEDBACK, data)
			elif cmd == Freggers.SRV_OFFER_HINT:
				self.debug('Com: SRV_OFFER_HINT')
				data = msg.get_boolean_arg(1)
				self.__fire_event(Event.SRV_OFFER_HINT, data)
			elif cmd == Freggers.SRV_SHOW_HINT:
				self.debug('Com: SRV_SHOW_HINT')
				data = msg.get_string_arg(1)
				self.__fire_event(Event.SRV_SHOW_HINT, data)
			elif cmd == Freggers.CLOSE_ROOM_HOP_MENU:
				self.debug('Com: CLOSE_ROOM_HOP_MENU')
				self.__fire_event(Event.CLOSE_ROOM_HOP_MENU, None)
			elif cmd == Freggers.OPEN_LIST_RECIPES_BY_INGREDIENT_VIEW:
				self.debug('Com: OPEN_LIST_RECIPES_BY_INGREDIENT_VIEW')
				data = msg.get_int_arg(1)
				self.__fire_event(Event.OPEN_LIST_RECIPES_BY_INGREDIENT_VIEW, data)
			elif cmd == Freggers.OPEN_CRAFT_RECIPE_VIEW:
				self.debug('Com: OPEN_CRAFT_RECIPE_VIEW')
				data = {
					'recipe_id': msg.get_int_arg(1),
					'replace_item_id': msg.get_int_arg(2)
				}
				
				self.__fire_event(Event.OPEN_CRAFT_RECIPE_VIEW, data)
			elif cmd == Freggers.COM_MAY_VOTE:
				self.debug('Com: COM_MAY_VOTE')
				data = MayVote(msg)
				self.__fire_event(Event.COM_MAY_VOTE, data)
			elif cmd == Freggers.NOTIFY_CREDIT_ACCOUNT:
				self.debug('Com: NOTIFY_CREDIT_ACCOUNT')
				array = msg.get_int_list_arg(1)
				data = {
					'credits_earned': array[0],
					'credits_bought': array[1]
				}
				self.debug(data)
				self.__fire_event(Event.NOTIFY_CREDIT_ACCOUNT, data)
			elif cmd == Freggers.OPEN_QUEST_VIEW:
				self.debug('Com: OPEN_QUEST_VIEW')
				data = msg.get_string_arg(1)
				self.__fire_event(Event.OPEN_QUEST_VIEW, data)
			elif cmd == Freggers.OPEN_QUEST_COMPLETED_VIEW:
				self.debug('Com: OPEN_QUEST_COMPLETED_VIEW')
				data = {
					'quest_label': msg.get_string_arg(1),
					'next_quest_label': msg.get_string_arg(2)
				}
				self.__fire_event(Event.OPEN_QUEST_COMPLETED_VIEW, data)
			elif cmd == Freggers.UPDATE_ROOMITEM_MENU:
				self.debug('Com: UPDATE_ROOMITEM_MENU')
				data = {
					'wob_id': msg.get_int_arg(1),
					'interactions': InteractionData(msg.get_message_arg(2)),
					'primary_interaction_label': msg.get_string_arg(3)
				}
				
				iso_item = self.wob_registry.get_object_by_wobid(data['wob_id'])
				iso_item.remove_interactions()
				IsoItem.create_interaction_menu(iso_item, data['interactions'], data['primary_interaction_label'])
				self.__add_examine_interaction(iso_item)
				self.__fire_event(Event.UPDATE_ROOMITEM_MENU, data)
			
	def get_daily_offer(self):
		resp = self.amf_api.call(AmfAPI.GET_DAILY_OFFER)
		if resp[0] == STATUS_OK:
			return ShopItem.from_data(resp[1])[0]
	
	def __remote_log(self, p1, p2, p3, cb = None):
		self.amf_api.call(AmfAPI.LOG, cb, cb, args = [p1, p2, p3, Capabilities['os'], Capabilities['version'], Freggers.BROWSER])
