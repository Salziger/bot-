#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import random
import threading
import time
import math
import traceback
from datetime import datetime, date, timezone, timedelta

from .freggers import Freggers, Event
from .locale.de import LocaleEN
from .utils.item_search import ItemSearch
from .utils.item_pickup import ItemPickup
from .utils import format_time
from .iso import Status

TIMEZONE = timezone(timedelta(hours = 2))

def get_local_datetime():
	return datetime.now(tz = TIMEZONE)

error_log = open('error.log', 'a')

def log_error(error):
	traceback.print_exc()
	traceback.print_exc(file = error_log)
	error_log.flush()

class FreggersBot(Freggers):
	
	CHAT_CHARS = {
		'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
		'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
		'1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
		'Ä', 'Ö', 'Ü', 'ä', 'ö', 'ü', ',', ';', '.', '-', '_', '!', '?', '<', '>', ':', '#', '\'', '"', '+', '*', '|', '~', '\\', 
		'^', '°', '§', '$', '%', '&', '/', '(', ')', '=', '`', '´', ' '
	}
	
	PET_GUI_PREFIXES = {
		'tp_botanik.suzy',
		'tp_botanik.sparky',
		'tp_botanik.claude',
		'tp_botanik.fluffy',
		'tp_botanik.betty',
		'tp_botanik.pony',
		'tp_botanik.santos',
		'tp_botanik.gwen',
		'tp_botanik.oskar',
		'tp_botanik.ida',
		'tp_botanik.nepo',
		'tp_botanik.nyoko',
		'tp_botanik.marvin'
	}
	
	AP_APARTMENT = 'plattenbau.eigenheim'
	AP_HOOVER_STREET = 'hood.playrent'
	AP_COCONUT_ISLAND = 'beach.inselrent'
	AP_WEIDE = 'tp_botanik.weiderent'
	
	MIN_ROOM_LOAD_DELAY = 0.2
	MAX_ROOM_LOAD_DELAY = 4
	
	MIN_SEARCH_DONE_DELAY = 0.2
	MAX_SEARCH_DONE_DELAY = 8
	
	def __init__(self, username, password, localeItems = LocaleDE, is_debug = False):
		self.username = username
		self.password = password
		self.localeItems = localeItems
		self.level_data = None
		self.balance_data = None
		self.start_level_data = None
		self.room_waits = {}
		self.speed_factor = 0.3 + random.random()
		self.__fregger_check = None
		self.__ants_times = {}
		self.__church_visited_today = False
		self.__e_room_ready = threading.Event()
		self.__e_room_loaded = threading.Event()
		self.__e_show_metromap = threading.Event()
		self.__e_level_data = threading.Event()
		self.__e_balance_data = threading.Event()
		self.__e_success_cb = threading.Event()
		self.__e_timer_bar = threading.Event()
		self.__e_collect = threading.Event()
		self.__e_quest_done = threading.Event()
		self.timer_bar = None
		self.quest = None
		self.trash_items = {
			localeItems.BEER_CRATE,
			localeItems.FISH_BONE,
			localeItems.DUNG_BEATLE,
			localeItems.ACORN
		}
		self.trash_items.update(localeItems.EXPLORER_BADGE_ITEMS_0)
		self.trash_items.update(localeItems.EXPLORER_BADGE_ITEMS_1)
		self.trash_items.update(localeItems.EXPLORER_BADGE_ITEMS_2)
		self.trash_items.update(localeItems.EXPLORER_BADGE_ITEMS_3)
		self.prefered_store_items = {
			localeItems.GNOME
		}
		self.consumable_items = {
			localeItems.DRAGON_FLOWER,
			localeItems.HORSE_FLOWER,
			localeItems.DRAGON_TORCH,
			localeItems.HORSESHOE,
			localeItems.MUSIC_BOX,
			localeItems.BLANKET,
			localeItems.EMPTY_BOTTLE
		}
		self.disposable_consuamables = {
			localeItems.DRAGON_MILK,
			localeItems.DRAGON_MIXED_MILK,
			localeItems.HORSE_MILK,
			localeItems.HORSE_MIXED_MILK,
			localeItems.CHILI,
			localeItems.STRAWBERRY
		}
		self.disposable_consuamables.update(localeItems.LAZY_ANTS)
		self.disposable_consuamables.update(localeItems.MUSHROOMS)
		self.consumable_items.update(self.disposable_consuamables)
		self.start = lambda: None
		super(FreggersBot, self).__init__(log_prefix = '[' + self.username + ']', is_debug = is_debug, localeItems = localeItems)
		self.register_callback(Event.CTXT_ROOM, self.__handle_room_ctxt)
		self.register_callback(Event.SHOW_ACTION_FEEDBACK, self.__handle_show_action)
		self.register_callback(Event.ACTION_SHOW_METROMAP, self.__handle_show_metromap)
		self.register_callback(Event.NOTIFY_LEVEL, self.__handle_level)
		self.register_callback(Event.ENV_ITEM, self.__handle_env_item)
		self.register_callback(Event.SHOW_TIMER_BAR, self.__handle_timer_bar)
		self.register_callback(Event.OPEN_QUEST_VIEW, self.__handle_open_quest_view)
		self.register_callback(Event.OPEN_QUEST_COMPLETED_VIEW, self.__handle_quest_completed)
		self.register_callback(Event.NOTIFY_CREDIT_ACCOUNT, self.__handle_credit_account)
		
	@staticmethod
	def replace_non_chat_chars(str, replacement):
		chat_chars = FreggersBot.CHAT_CHARS
		for i, c in enumerate(str):
			if c not in chat_chars:
				str = str[:i] + replacement + str[i + 1:]
		return str
		
	def init(self):
		self.log('Logging in...')
		if self.init_session(self.username, self.password):
			self.log('Logged in')
			return True
		else:
			self.log('Could not login')
			return False
	
	def boot(self):
		super(FreggersBot, self).boot()
		self.__e_room_ready.wait()
		self.send_show_metroplan()
		self.__e_show_metromap.wait()

	def __handle_credit_account(self, data):
		self.balance_data = data
		self.__e_balance_data.set()
	
	def wait_balance_data(self):
		self.__e_balance_data.wait()
	
	def __handle_open_quest_view(self, data):
		self.quest = data
	
	def __handle_quest_completed(self, data):
		self.quest = data['next_quest_label']
		self.__e_quest_done.set()
	
	def __handle_timer_bar(self, data):
		self.timer_bar = data / 1000
		self.__e_timer_bar.set()
	
	def __handle_room_ctxt(self, room):
		self.debug('Handle CTXT_ROOM:',room.room_context_label,room.gui(),room.room_gui,self.area_name,room.wob_id,
			room.desc,room.topic,room.user_owns_room,room.owner_user_id,room.owner_user_name)
		self.__e_room_loaded.clear()
		self.__e_level_data.clear()
		self.__e_room_ready.set()
		room_waits = self.room_waits.get(room.room_context_label)
		if room_waits != None:
			request_metroplan = False
			for room_wait in list(room_waits):
				owner_id = room_wait['owner_id']
				if owner_id == None or owner_id == room.owner_user_id:
					if room_wait['area_index'] != None:
						request_metroplan = True
					else:
						room_wait['success'] = True
						room_wait['e'].set()
			if request_metroplan:
				self.send_show_metroplan()
	
	def __handle_show_action(self, data):
		if data == self.localeItems.NO_RIGHTS_TO_ENTER_ROOM or data == self.localeItems.ROOM_FULL:
			for room_waits in self.room_waits.values():
				for room_wait in list(room_waits):
					room_wait['success'] = False
					room_wait['e'].set()
	
	def __handle_env_item(self, data):
		self.debug('Handle ENV_ITEM:', data)
		threading.Thread(target = self.__delayed_room_load_notify).start()
	
	def wait_random_delay(self, min, max):
		delay = min + (random.random() * (max - min)) * self.speed_factor
		if delay > 0:
			self.log('Waiting random delay of {} seconds.'.format(delay))
			time.sleep(delay)
	
	def __delayed_room_load_notify(self):
		self.wait_random_delay(FreggersBot.MIN_ROOM_LOAD_DELAY, FreggersBot.MAX_ROOM_LOAD_DELAY)
		self.__e_room_loaded.set()
	
	def __handle_show_metromap(self, metromap_data):
		self.debug('Metromap:', metromap_data)
		self.__metromap = metromap_data
		current_area_index = metromap_data[0]['label']
		c_pos = current_area_index.find('%')
		self.area_index = 0 if c_pos == -1 else int(current_area_index[c_pos + 1:c_pos + 2])
		self.__e_show_metromap.set()
		room_waits = self.room_waits.get(self.room.room_context_label)
		if room_waits != None:
			for room_wait in list(room_waits):
				owner_id = room_wait['owner_id']
				area_index = room_wait['area_index']
				if (owner_id == None or owner_id == self.room.owner_user_id) and (area_index == None or area_index == self.area_index):
					room_wait['success'] = True
					room_wait['e'].set()
	
	class WaitForEvent:
		
		def __init__(self, freggers, event):
			self.__freggers = freggers
			self.event_type = event
			self.event = threading.Event()
			freggers.register_callback(event, self.__cb)
		
		def __cb(self, data):
			self.event.set()
		
		def wait(self):
			self.event.wait()
		
		def clear(self):
			self.event.clear()
		
		def wait_once(self):
			self.wait()
			self.cleanup()
		
		def cleanup(self):
			self.__freggers.unregister_callback(self.event_type, self.__cb)
	
	def get_wait_for_event(self, event):
		return FreggersBot.WaitForEvent(self, event)
	
	def wait_for_event(self, event):
		e = threading.Event()
		cb = lambda data: e.set()
		self.register_callback(event, cb)
		e.wait()
		self.unregister_callback(event, cb)
	
	def go_to_room(self, room_gui, exact):
		plain_room_gui = room_gui
		c_pos = plain_room_gui.find('%')
		area_index = 0
		if c_pos != -1:
			c_end = plain_room_gui.index('.', c_pos)
			area_index = int(plain_room_gui[c_pos + 1:c_end])
			plain_room_gui = plain_room_gui[:c_pos] + plain_room_gui[c_end:]
		c_pos = plain_room_gui.find('#@#')
		owner_id = None
		if c_pos != -1:
			owner_id = int(plain_room_gui[c_pos + 3:])
			plain_room_gui = plain_room_gui[:c_pos]
		if exact:
			self.__e_show_metromap.clear()
			self.send_show_metroplan()
			self.__e_show_metromap.wait()
		if (self.room.room_context_label != plain_room_gui or (owner_id != None and self.room.owner_user_id != owner_id) or 
		   (exact and area_index != self.area_index and owner_id == None)):
			self.log('Going to room {} exact={} ...'.format(room_gui, exact))
			wait = {
				'e': threading.Event(),
				'area_index': area_index if exact else None,
				'owner_id': owner_id,
				'success': False
			}
			waits = self.room_waits.get(plain_room_gui)
			if waits == None:
				waits = []
				self.room_waits[plain_room_gui] = waits
			waits.append(wait)
			self.send_auto_walk_to(room_gui, False, exact)
			wait['e'].wait()
			waits.remove(wait)
			self.log('Arrived in room {} success={}'.format(room_gui, wait['success']))
			return wait['success']
		return True

	def throw_away_effects(self, inv = None):
		self.log('Throwing away effects...')
		if inv == None:
			inv = self.ajax_request_inventory()
		effect_names = self.localeItems.EFFECTS
		target = [1, 1, 1] if self.player == None else self.player.wob_id
		thrown = 0
		slots_thrown = 0
		for item in list(inv):
			if item != None and item['description'] in effect_names:
				for _ in range(item['count']):
					self.ajax_item_usewith(item['id'], target)
					thrown += 1
					time.sleep(0.4)
				slots_thrown += 1
				inv.remove(item)
		self.log('Thrown {} effect(s) out of {} slots.'.format(thrown, slots_thrown))
		return (slots_thrown, thrown)
	
	def get_target_pos(self, wob_id):
		obj = self.wob_registry.get_object_by_wobid(wob_id)
		if obj != None:
			anim = self.animation_manager.animations.get(wob_id, None)
			if anim != None:
				return anim.get_target_pos()
			return obj.iso_obj.get_uvz()
		return None

	def delete_item(self, item):
		self.log('Deleting item \'{}\' count={} id={} ...'.format(item['description'], item['count'], item['id']))
		return self.ajax_delete_item(item['id'])
	
	def delete_trash_items(self, inv = None, queue = None):
		if inv == None:
			inv = self.ajax_request_inventory()
		if queue == None:
			queue = self.ajax_request_item_queue()
		count_inv = 0
		for item in list(inv):
			if item != None and item['description'] in self.trash_items:
				self.delete_item(item)
				inv.remove(item)
				count_inv += 1
		count_queue = 0
		for item in list(queue):
			if item['description'] in self.trash_items:
				self.ajax_inbox_action(item['id'], Freggers.INBOX_ACTION_DECLINE)
				queue.remove(item)
				count_queue += 1
		return (count_inv, count_queue)
	
	@staticmethod
	def count_empty_slots(container):
		count = 0
		for item in container:
			if item == None:
				count += 1
		return count
	
	@staticmethod
	def filter_items(container, item_names):
		return list(filter(lambda item: item != None and item['description'] in item_names, container))
	
	@staticmethod
	def filter_item(container, item_name):
		return list(filter(lambda item: item != None and item['description'] == item_name, container))
	
	@staticmethod
	def count_items(container, item_names):
		count = 0
		for item in container:
			if item != None and item['description'] in item_names:
				count += 1
		return count
	
	@staticmethod
	def count_item(container, item_name):
		count = 0
		for item in container:
			if item != None and item['description'] == item_name:
				count += 1
		return count
	
	def get_item_count(self, item_name):
		count = 0
		inv = self.ajax_request_inventory()
		for item in inv:
			if item != None and item['description'] == item_name:
				count += 1
		queue = self.ajax_request_item_queue()
		for item in queue:
			if item['description'] == item_name:
				count += 1
		return count
	
	def get_items_count(self, item_names):
		count = 0
		inv = self.ajax_request_inventory()
		for item in inv:
			if item != None and item['description'] in item_names:
				count += 1
		queue = self.ajax_request_item_queue()
		for item in queue:
			if item['description'] in item_names:
				count += 1
		return count
	
	def __collect_handle_create_item(self, data):
		self.__collect_remaining_wait = 0
		self.__collect_amount += 1
		self.__e_collect.set()
	
	def __collect_handle_timer_bar(self, duration):
		self.__collect_time = time.time()
	
	def __collect_handle_action_feedback(self, txt):
		if txt.endswith(self.localeItems.USE_WAIT_SUFFIX):
			unit = 1 if self.localeItems.SECONDS in txt else 60
			value = [int(s) for s in txt.split() if s.isdigit()][0]
			self.__collect_remaining_wait = value * unit
		else:
			self.__collect_remaining_wait = 0
		self.__e_collect.set()
	
	def __init_collect(self):
		self.__collect_amount = 0
		self.__collect_remaining_wait = 0
		self.register_callback(Event.NOTIFY_CREATE_ITEM, self.__collect_handle_create_item)
		self.register_callback(Event.SHOW_TIMER_BAR, self.__collect_handle_timer_bar)
		self.register_callback(Event.SHOW_ACTION_FEEDBACK, self.__collect_handle_action_feedback)
	
	def __deinit_collect(self):
		self.unregister_callback(Event.NOTIFY_CREATE_ITEM, self.__collect_handle_create_item)
		self.unregister_callback(Event.SHOW_TIMER_BAR, self.__collect_handle_timer_bar)
		self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, self.__collect_handle_action_feedback)
		self.__collect_amount = None
		self.__collect_remaining_wait = None
	
	def collect_bottles(self, max_amount = 0):
		self.__init_collect()
		room_guis = [{'plattenbau.metro': 'wutzlhofen.schach_parkabfalleimer',
					  'plattenbau.bolzplatz': 'hood.strasse_muelltonne'},
					 {'hood.strasse': 'hood.strasse_muelltonne',
					  'hood.waschsalon': 'hood.waschsalon_plastikmuelleimer'},
					 {'wutzlhofen.uferpromenade': 'wutzlhofen.uferpromenade_abfalleimerblau',
					  'wutzlhofen.schach': 'wutzlhofen.schach_parkabfalleimer',
					  'wutzlhofen.passage': 'wutzlhofen.passage_muelleimer'}]
		len_areas = len(room_guis)
		area_index = random.randint(0, len_areas - 1)
		collected_bottles = 0
		while True:
			self.log('[Bottles] Collecting {} / {}...'.format(collected_bottles, max_amount))
			rooms = room_guis[area_index]
			area_index = (area_index + 1) % len_areas
			for room_label in rooms.keys() if random.random() > 0.5 else reversed(list(rooms.keys())):
				gui = rooms[room_label]
				self.go_to_room(room_label, False)
				self.__e_room_loaded.wait()
				for target in self.sort_iso_items_by_distance(list(filter(lambda iso_item: iso_item.gui == gui and iso_item.has_interaction('SEARCH'), self.wob_registry.iso_items))):
					self.log('[Bottles] Interacting with {} ({})...'.format(target.name, target.gui))
					self.__e_collect.clear()
					self.send_item_interaction(target.wob_id, 'SEARCH')
					self.__e_collect.wait()
					self.wait_random_delay(FreggersBot.MIN_SEARCH_DONE_DELAY, FreggersBot.MAX_SEARCH_DONE_DELAY)
					collected_bottles = self.get_item_count(self.localeItems.EMPTY_BOTTLE)
					if max_amount != 0 and collected_bottles >= max_amount:
						self.__deinit_collect()
						return collected_bottles
	
	def collect_ants(self, max_amount = 0):
		self.__init_collect()
		rooms = ['western.indianerdorf', 'western.camp']
		len_rooms = len(rooms)
		room_index = random.randint(0, len_rooms - 1)
		while True:
			self.log('Collecting ants {} / {}...'.format(self.__collect_amount, max_amount))
			for _ in range(len_rooms):
				room = rooms[room_index]
				room_index = (room_index + 1) % len_rooms
				self.go_to_room('western.rail', False)
				self.__e_room_loaded.wait()
				self.go_to_room(room, False)
				self.__e_room_loaded.wait()
				cactuses = list(filter(lambda iso_item: iso_item.gui == 'western.kaktus02', self.wob_registry.iso_items))
				lim_cactuses = len(cactuses)
				cactus_index = random.randint(0, lim_cactuses - 1)
				for _ in range(lim_cactuses):
					cactus_wob_id = cactuses[cactus_index].wob_id
					cactus_index = (cactus_index + 1) % lim_cactuses
					while True:
						self.log('[Ants] Interacting with cactus')
						self.__e_collect.clear()
						self.send_item_interaction(cactus_wob_id, 'SEARCH')
						self.__e_collect.wait()
						remaining_wait_time = self.__collect_remaining_wait
						if remaining_wait_time == 0:
							self.__ants_times[cactus_wob_id] = self.__collect_time
							self.wait_random_delay(FreggersBot.MIN_SEARCH_DONE_DELAY, FreggersBot.MAX_SEARCH_DONE_DELAY)
							if max_amount != 0 and max_amount <= self.__collect_amount:
								ants_collected = self.__collect_amount
								self.__deinit_collect()
								return ants_collected
							break
						last_cactus_time = self.__ants_times.get(cactus_wob_id)
						if last_cactus_time != None:
							remaining_wait = 184 - (time.time() - last_cactus_time)
							if remaining_wait > 0:
								self.log('[Ants]', 'Waiting {} more seconds.'.format(remaining_wait))
								time.sleep(remaining_wait)
								continue
						idle_time = remaining_wait_time + 1 if remaining_wait_time <= 60 else self.__collect_remaining_wait * 0.75
						self.log('[Ants]', 'Waiting {} seconds before retrying.'.format(idle_time))
						time.sleep(idle_time)
	
	def collect_eggs(self, max_amount = 0):
		self.__init_collect()
		room_guis = [{'plattenbau.metro': ['hood.getraenkedoserot'],
					  'plattenbau.plattenbau': ['hood.getraenkedoserot'],
					  'plattenbau.bolzplatz': ['wutzlhofen.plaza_hydrant']},
					 {'wutzlhofen.plaza': ['wutzlhofen.plaza_hydrant'],
					  'wutzlhofen.diner': ['wutzlhofen.diner_kuehlschrank'],
					  'wutzlhofen.passage': ['wutzlhofen.buchsbaum'],
					  'wutzlhofen.disko': ['wutzlhofen.disko_boxenturm'],
					  'wutzlhofen.wohlwert': ['wutzlhofen.wohlwert_wohlwertkiste'],
					  'wutzlhofen.schach': ['wutzlhofen.schach_baumstumpf'],
					  'wutzlhofen.museum': ['wutzlhofen.museum_schaukasten1'],
					  'wutzlhofen.uferpromenade': ['wutzlhofen.uferpromenade_kiosk'],
					  'wutzlhofen.kroetenbank': ['wutzlhofen.kroetenbank_schirmstaender'],
					  'wutzlhofen.flussdampfer': ['wutzlhofen.flussdampfer_belueftung']},
					 {'hood.gym': ['hood.gym_pressbank1', 'hood.gym_gewicht'],
					  'hood.punk': ['hood.punk_punktisch'],
					  'hood.backalley': ['hood.backalley_ziegelstapel', 'hood.ghettoblaster'],
					  'hood.waschsalon': ['hood.waschsalon_aschenbecher', 'hood.waschsalon_waeschekorb'],
					  'hood.friseur': ['hood.getraenkedoserot'],
					  'hood.outskirts': ['hood.zeitschriftenhaufen', 'hood.ghettoblaster'],
					  'hood.hiphop': ['hood.hiphop_hiphopghetto']},
					 {'western.rail': ['western.kaktus02', 'western.kaktus03'],
					  'western.fort': ['western.fort_pulverfass', 'western.kanone2'],
					  'western.saloonzimmer3': ['western.badezuber'],
					  'western.saloonzimmer2': ['western.badezuber'],
					  'western.camp': ['western.camp_geige'],
					  'western.indianerdorf': ['western.kaktus01']},
					 {'tp_botanik.cafe': ['tp_botanik.loungetisch', 'tp_botanik.spiralentisch']},
					 {'beach.beach3': ['western.kaktus03'],
					  'beach.beach2': ['western.kaktus03']},
					 {'gothics.raum9': ['gothics.raum9_tisch_rund'],
					  'gothics.gruft': ['wutzlhofen.fu_ku2009_pizzabox_002'],
					  'gothics.waldraum02': ['wutzlhofen.schach_baumstumpf']}]
		len_areas = len(room_guis)
		_last_area_indices = [-1, -1]
		def next_area():
			i = random.randint(0, len_areas - 1)
			while i == _last_area_indices[0] or i == _last_area_indices[1]:
				i = random.randint(0, len_areas - 1)
			_last_area_indices[1] = _last_area_indices[0]
			_last_area_indices[0] = i
			return i
		while True:
			self.log('[Eggs] Collecting {} / {}...'.format(self.__collect_amount, max_amount))
			for room_label, guis in room_guis[next_area()].items():
				self.go_to_room(room_label, False)
				self.__e_room_loaded.wait()
				search_targets = list(filter(lambda iso_item: iso_item.gui in guis and iso_item.has_interaction('SEARCH'), self.wob_registry.iso_items))
				lim_targets = len(search_targets)
				target_index = 0 if lim_targets < 2 else random.randint(0, lim_targets - 1)
				for _ in range(lim_targets):
					target = search_targets[target_index]
					target_wob_id = target.wob_id
					target_index = (target_index + 1) % lim_targets
					self.log('[Eggs] Interacting with {} ({})...'.format(target.name, target.gui))
					self.__e_collect.clear()
					self.send_item_interaction(target_wob_id, 'SEARCH')
					self.__e_collect.wait()
					self.wait_random_delay(FreggersBot.MIN_SEARCH_DONE_DELAY, FreggersBot.MAX_SEARCH_DONE_DELAY)
					if max_amount != 0 and self.__collect_amount >= max_amount:
						collected_eggs = self.__collect_amount
						self.__deinit_collect()
						return collected_eggs
	
	def __cb_success(self, data):
		self.__success = True
		self.__e_success_cb.set()
		
	def __cb_failure(self, data):
		self.__success = False
		self.__e_success_cb.set()
	
	def search_covered_wagon(self):
		self.log('Searching covered wagon...')
		if self.room.room_context_label != 'western.backlands':
			if self.room.room_context_label != 'western.indianerdorf':
				self.go_to_room('western.rail', False)
				self.__e_room_loaded.wait()
				self.go_to_room('western.indianerdorf', False)
				self.__e_room_loaded.wait()
			self.go_to_room('western.backlands', False)
		self.__e_room_loaded.wait()
		self.__success = False
		for item in self.wob_registry.iso_items:
			if item.gui == 'western.planwagen':
				self.__e_success_cb.clear()
				self.register_callback(Event.NOTIFY_CREATE_ITEM, self.__cb_success)
				self.register_callback(Event.SHOW_ACTION_FEEDBACK, self.__cb_failure)
				self.send_item_interaction(item.wob_id, 'SEARCH')
				self.__e_success_cb.wait()
				self.unregister_callback(Event.NOTIFY_CREATE_ITEM, self.__cb_success)
				self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, self.__cb_failure)
				break
		self.log('Successfully searched covered wagon:', self.__success)
		return self.__success
	
	def search_noisy_construction_site(self):
		self.log('Searching noisy construction site...')
		self.go_to_room('hood.strasse', False)
		self.__e_room_loaded.wait()
		self.go_to_room('hood.outskirts', False)
		self.__e_room_loaded.wait()
		self.__success = False
		for item in self.wob_registry.iso_items:
			if item.gui == 'wutzlhofen.baustelle':
				self.__e_success_cb.clear()
				self.register_callback(Event.NOTIFY_CREATE_ITEM, self.__cb_success)
				self.register_callback(Event.SHOW_ACTION_FEEDBACK, self.__cb_failure)
				self.send_item_interaction(item.wob_id, 'SEARCH')
				self.__e_success_cb.wait()
				self.unregister_callback(Event.NOTIFY_CREATE_ITEM, self.__cb_success)
				self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, self.__cb_failure)
				break
		self.log('Successfully searched noisy construction site:', self.__success)
		return self.__success
	
	def deliver_ants(self, amount):
		ants_in_queue = None
		inv = self.ajax_request_inventory()
		ants_in_inv = self.count_items(inv, self.localeItems.LAZY_ANTS)
		
		if ants_in_inv == 0 and not self.ensure_empty_slots(1):
			self.log('[Deliver Ants] No inventory slots available.')
			return 0
		
		inv = self.ajax_request_inventory()
		ants_in_inv = self.count_items(inv, self.localeItems.LAZY_ANTS)
		slots_usable = FreggersBot.count_empty_slots(inv) + ants_in_inv
		
		self.go_to_room('gothics.raum9', False)
		self.__e_room_loaded.wait()
		self.go_to_room('gothics.friedhof', False)
		self.__e_room_loaded.wait()
		self.go_to_room('gothics.eule', False)
		self.__e_room_loaded.wait()
		
		wob_id = None
		for item in self.wob_registry.iso_items:
			if item.gui == 'wutzlhofen.ameisenhaufen_bug':
				wob_id = item.wob_id
		if wob_id == None:
			self.log('[Deliver Ants] Anthill not found.')
			return 0
		
		self.__expect_deliver_event = False
		self.__ants_delivered_amount = 0
		self.__ant_delivered_success = False
		self.__e_ant_delivered = threading.Event()
		
		def handle_timer_bar(data):
			if self.__expect_deliver_event:
				self.debug('[Deliver Ants] Timer bar:', data)
				self.__expect_deliver_event = False
				self.__ant_delivered_success = True
				self.__e_ant_delivered.set()
		
		def handle_show_action(data):
			if self.__expect_deliver_event:
				self.debug('[Deliver Ants] Show action:', data)
				self.__expect_deliver_event = False
				self.__ant_delivered_success = False
				self.__e_ant_delivered.set()
		
		self.register_callback(Event.SHOW_ACTION_FEEDBACK, handle_show_action)
		self.register_callback(Event.SHOW_TIMER_BAR, handle_timer_bar)
		
		if ants_in_inv < amount:
			ants_in_queue = self.filter_items(self.ajax_request_item_queue(), self.localeItems.LAZY_ANTS)
		
		deliver_amount = min(amount, ants_in_inv + (0 if ants_in_queue == None else len(ants_in_queue)))
		delivered_amount = 0
		
		while delivered_amount < deliver_amount:
			remaining_amount = deliver_amount - delivered_amount
			if ants_in_inv == 0:
				accept_amount = min(slots_usable, remaining_amount)
				for _ in range(accept_amount):
					ant_in_queue = ants_in_queue.pop(0)
					self.ajax_inbox_action(ant_in_queue['id'], Freggers.INBOX_ACTION_ACCEPT)
				ants_in_inv = self.count_items(self.ajax_request_inventory(), self.localeItems.LAZY_ANTS)
				if ants_in_inv < remaining_amount:
					ants_in_queue = self.filter_items(self.ajax_request_item_queue(), self.localeItems.LAZY_ANTS)
			else:
				self.__expect_deliver_event = True
				self.__e_ant_delivered.clear()
				self.send_item_interaction(wob_id, 'DELIVER_ANT')
				self.__e_ant_delivered.wait()
				if self.__ant_delivered_success:
					self.log('[Deliver Ants] Successfully delivered ant.')
					self.__ant_delivered_success = False
					delivered_amount += 1
					ants_in_inv -= 1
					self.wait_random_delay(1, 1.8)
				else:
					self.log('[Deliver Ants] No ant in inventory to deliver.')
					ants_in_inv = self.count_items(self.ajax_request_inventory(), self.localeItems.LAZY_ANTS)
		
		self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, handle_show_action)
		self.unregister_callback(Event.SHOW_TIMER_BAR, handle_timer_bar)
		del self.__ants_delivered_amount
		del self.__e_ant_delivered
		del self.__expect_deliver_event
		
		return delivered_amount
	
	def return_bottles(self, amount, beer_crates = False):
		bottles_in_queue = None
		inv = self.ajax_request_inventory()
		bottles_in_inv = self.count_items(inv, self.localeItems.EMPTY_BOTTLE)
		
		if not beer_crates:
			for item in list(inv):
				if item != None and item['description'] == self.localeItems.BEER_CRATE:
					self.delete_item(item)
					inv.remove(item)
		
		if bottles_in_inv == 0 and not self.ensure_empty_slots(1):
			self.log('[Return Bottles] No inventory slots available.')
			return 0
		
		inv = self.ajax_request_inventory()
		bottles_in_inv = self.count_items(inv, self.localeItems.EMPTY_BOTTLE)
		slots_usable = FreggersBot.count_empty_slots(inv) + bottles_in_inv
		
		self.go_to_room('hood.strasse', False)
		self.__e_room_loaded.wait()
		self.go_to_room('hood.outskirts', False)
		self.__e_room_loaded.wait()
		
		target = self.find_item_by_gui('hood.recyclingautomat')
		if target == None:
			self.log('[Return Bottles] Could not find reverse vending machine.')
			return 0
		wob_id = target.wob_id
		
		self.__expect_return_event = False
		self.__bottles_returned_amount = 0
		self.__bottles_returned_success = False
		self.__e_bottles_returned = threading.Event()
		
		def handle_timer_bar(data):
			if self.__expect_return_event:
				self.log('[Return Bottles] Timer bar:', data)
				self.__expect_return_event = False
				self.__bottles_returned_success = True
				self.__e_bottles_returned.set()
		
		def handle_show_action(data):
			if self.__expect_return_event:
				self.log('[Return Bottles] Show action:', data)
				self.__expect_return_event = False
				self.__bottles_returned_success = False
				self.__e_bottles_returned.set()
		
		self.register_callback(Event.SHOW_ACTION_FEEDBACK, handle_show_action)
		self.register_callback(Event.SHOW_TIMER_BAR, handle_timer_bar)
		
		if bottles_in_inv < amount:
			bottles_in_queue = self.filter_items(self.ajax_request_item_queue(), self.localeItems.EMPTY_BOTTLE)
		
		return_amount = min(amount, bottles_in_inv + (0 if bottles_in_queue == None else len(bottles_in_queue)))
		returned_amount = 0
		
		while returned_amount < return_amount:
			remaining_amount = return_amount - returned_amount
			if bottles_in_inv == 0:
				accept_amount = min(slots_usable, remaining_amount)
				for _ in range(accept_amount):
					bottle_in_queue = bottles_in_queue.pop(0)
					self.ajax_inbox_action(bottle_in_queue['id'], Freggers.INBOX_ACTION_ACCEPT)
				bottles_in_inv = self.count_items(self.ajax_request_inventory(), self.localeItems.EMPTY_BOTTLE)
				if bottles_in_inv < remaining_amount:
					bottles_in_queue = self.filter_items(self.ajax_request_item_queue(), self.localeItems.EMPTY_BOTTLE)
			else:
				self.__expect_return_event = True
				self.__e_bottles_returned.clear()
				self.send_item_interaction(wob_id, 'RETURN_EMPTY_BOTTLE')
				self.__e_bottles_returned.wait()
				if self.__bottles_returned_success:
					self.log('[Return Bottles] Successfully returned empty bottle.')
					self.__bottles_returned_success = False
					returned_amount += 1
					bottles_in_inv -= 1
					self.wait_random_delay(1, 1.8)
				else:
					self.log('[Return Bottles] No empty bottle in inventory to return.')
					bottles_in_inv = self.count_items(self.ajax_request_inventory(), self.localeItems.EMPTY_BOTTLE)
		
		self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, handle_show_action)
		self.unregister_callback(Event.SHOW_TIMER_BAR, handle_timer_bar)
		del self.__bottles_returned_amount
		del self.__e_bottles_returned
		del self.__expect_return_event
		
		self.log('[Return Bottles] Returned {} empty bottles.'.format(returned_amount))
		
		return returned_amount
	
	def __handle_level(self, data):
		time_now = time.time()
		self.debug('Level data updated:', data)
		self.level_data = data
		self.level_data_timestamp = time_now
		self.__e_level_data.set()
	
	@staticmethod
	def contains(iterable, matchFunc):
		for item in iterable:
			if matchFunc(item):
				return True
		return False
	
	def ensure_empty_slots(self, count, inv = None):
		if inv == None:
			inv = self.ajax_request_inventory()
		remaining_slots = count - FreggersBot.count_empty_slots(inv)
		if remaining_slots > 0:
			self.log('Ensuring {}/{} empty slot(s) in inventory...'.format(remaining_slots, count))
			deleted_slot_count = self.delete_trash_items(inv = inv)[0]
			remaining_slots -= deleted_slot_count
			self.log('Deleted {} trash items.'.format(deleted_slot_count))
			if remaining_slots > 0:
				self.log('Throwing away effects...')
				self.__e_room_loaded.wait()
				effect_slots, effect_count = self.throw_away_effects(inv = inv)
				if effect_slots > 0:
					self.log('Threw {} effects out of {} slots away.'.format(effect_count, effect_slots))
					remaining_slots -= effect_slots
				
				if remaining_slots > 0:
					self.log('Deleting disposable consumables...')
					disposable_item_names = self.disposable_consuamables
					deleted_items = 0
					for item in list(inv):
						if item != None and item['description'] in disposable_item_names:
							if self.delete_item(item):
								deleted_items += 1
								remaining_slots -= 1
								inv.remove(item)
								if remaining_slots == 0:
									break
					if deleted_items > 0:
						self.log('Deleted {} items.'.format(deleted_items))
					if remaining_slots > 0:
						self.log('Trying to store {} more items in the locker...'.format(remaining_slots))
						locker_inv = self.ajax_request_locker()
						empty_locker_slots = FreggersBot.count_empty_slots(locker_inv)
						if remaining_slots <= empty_locker_slots:
							self.log('Going to store {} items in the locker...'.format(remaining_slots))
							self.go_to_room('wutzlhofen.kroetenbank', False)
							self.__e_room_loaded.wait()
							self.log('Waiting for locker to be opened.')
							locker = self.find_item_by_gui('wutzlhofen.kroetenbank_schliessfaecher')
							event_wait = self.get_wait_for_event(Event.ACTION_OPEN_LOCKER)
							self.send_item_interaction(locker.wob_id, 'USE')
							inv_prefered = list(filter(lambda item: item != None and item['description'] in self.prefered_store_items, inv))
							inv_non_consumables = list(filter(lambda item: item != None and item['description'] not in self.consumable_items, inv))
							event_wait.wait_once()
							self.log('Locker was opened.')
							deposited_items = 0
							while remaining_slots > 0 and len(inv) > 0:
								item = None
								if len(inv_prefered) > 0:
									item = inv_prefered.pop()
									print(item, inv)
									inv.remove(item)
								elif len(inv_non_consumables) > 0:
									item = inv_non_consumables.pop()
									print(item, inv)
									inv.remove(item)
								else:
									item = inv.pop()
								
								if item != None:
									if self.ajax_deposit_item(item['id']):
										remaining_slots -= 1
										deposited_items += 1
							self.log('Deposited {} items in locker.'.format(deposited_items))
							return remaining_slots == 0
						else:
							self.log('Not enough slots available in locker. There are only {} empty slots to store {} items.'.format(empty_locker_slots, remaining_slots))
							return False
		return True
	
	def closest_room_item(self, item_gui):
		self.__e_room_loaded.wait()
		return self.closest_iso_item(self.find_items_by_gui(item_gui))
	
	def closest_iso_item(self, iso_items):
		if len(iso_items) > 1:
			if self.player != None:
				player_pos = self.player.iso_obj.get_uvz()
				closest_distance = -1
				closest_item = None
				for iso_item in iso_items:
					distance = iso_item.iso_obj.get_uvz().distance(player_pos)
					if distance < closest_distance or closest_distance == -1:
						closest_item = iso_item
						closest_distance = distance
				return closest_item
			else:
				return None
		return None if len(iso_items) == 0 else iso_items[0]
	
	def get_room_items_by_distance(self):
		return self.sort_iso_items_by_distance(self.wob_registry.iso_items)
	
	def sort_iso_items_by_distance(self, iso_items, player = None):
		if player == None:
			player = self.player
		if len(iso_items) > 1:
			if player != None:
				player_pos = player.iso_obj.get_uvz()
				return sorted(list(iso_items), key = lambda x: x.iso_obj.get_uvz().distance(player_pos))
			else:
				return None
		return iso_items
	
	def pickup_room_item(self, wob_id):
		return ItemPickup(self, wob_id).pickup_once()
	
	def search_room_item(self, wob_id):
		return ItemSearch(self, wob_id).search_once()
	
	def pickup_closest_room_item(self, item_gui):
		item = self.closest_room_item(item_gui)
		if item != None:
			return self.pickup_room_item(item.wob_id)
		return False
	
	def search_closest_room_item(self, item_gui):
		item = self.closest_room_item(item_gui)
		if item != None:
			return self.search_room_item(item.wob_id)
		return False
	
	def pickup_any(self, item_gui):
		pickup = ItemPickup(self, 0)
		for iso_item in self.get_room_items_by_distance():
			if iso_item.gui == item_gui:
				pickup.wob_id = iso_item.wob_id
				if pickup.pickup():
					pickup.cleanup()
					return iso_item
		pickup.cleanup()
		return None
	
	def ensure_item_in_inv(self, item_name, relation_id = 0, price = 0):
		for inv_item in self.ajax_request_inventory():
			if inv_item != None and inv_item['description'] == item_name:
				return inv_item
		if self.ensure_empty_slots(1):
			for queue_item in self.ajax_request_item_queue():
				if queue_item['description'] == item_name:
					self.ajax_inbox_action(queue_item['id'], Freggers.INBOX_ACTION_ACCEPT)
					return queue_item
			if relation_id != 0 and price != 0:
				if self.ajax_buy_item(relation_id, price):
					for inv_item in self.ajax_request_inventory():
						if inv_item != None and inv_item['description'] == item_name:
							return inv_item
		else:
			return -1
		return 0
	
	def care_pompom(self, room, exact):
		room += '#@#' + str(self.user_id)
		self.go_to_room(room, exact)
		self.__e_room_loaded.wait()
		self.log('[Pompom] Looking for Pompom to cuddle.')
		for item in self.wob_registry.iso_items:
			for interaction in item.interactions:
				if interaction.label == 'CUDDLE_POMPOM':
					pompom_wob_id = item.wob_id
					event = threading.Event()
					def cb(data):
						event.set()
					self.register_callback(Event.SHOW_TIMER_BAR, cb)
					cuddle_count = 0
					self.log('[Pompom] Found Pompom.')
					failure_count = 0
					while True:
						for property in item.get_properties():
							if property.key == 'hintbubble' and property.value == 'cuddle_me':
								event.clear()
								self.log('[Pompom] Cuddling...')
								self.send_item_interaction(pompom_wob_id, 'CUDDLE_POMPOM')
								if event.wait(5):
									time.sleep(1)
									failure_count = 0
									cuddle_count += 1
									self.log('[Pompom] Cuddled {} times.'.format(cuddle_count))
									self.wait_random_delay(20, 23)
								else:
									failure_count += 1
									if failure_count >= 5:
										self.log('[Pompom] Cannot cuddle - aborting.')
										return False
							elif property.key == 'item_description' and len([int(s) for s in property.value.split() if s.isdigit()]) == 0:
								self.log('[Pompom] Pompom is happy for now.')
								self.unregister_callback(Event.SHOW_TIMER_BAR, cb)
								return True
						time.sleep(0.3)
		self.log('[Pompom] Could not find Pompom in room.')
		return False
	
	def __care_pet_give_effect(self, wob_id, effect_name, relation_id, price):
		self.log('[PetCare] Ensuring effect \'{}\' is in inventory...'.format(effect_name))
		item = self.ensure_item_in_inv(effect_name, relation_id, price)
		if item:
			self.log('[PetCare] Throwing effect \'{}\' at {}...'.format(effect_name, wob_id))
			self.ajax_item_usewith(item['id'], wob_id)
			return True
		else:
			self.log('[PetCare] Could not make sure effect \'{}\' is in inventory.'.format(effect_name))
			return False
		
	def __care_pet(self, wob_id, room, exact):
		#Drachen-Ei TRANSFORM
		while True:
			wob = self.wob_registry.get_object_by_wobid(wob_id)
			if wob == None:
				self.log('[PetCare] Pet was not found!')
				break
			
			primary_interaction = wob.get_primary_interaction()
			if primary_interaction != None and primary_interaction.label == 'PONY_HELP' and len(wob.interactions) == 6:
				self.log('[PetCare] Pet \'{}\' - {} is happy for now.'.format(wob.name, wob.gui))
				break
			
			for property in wob.get_properties():
				if property.key == 'hintbubble':
					hint = property.value
					if hint == 'drink_dragon' or hint == 'drink_pony':
						pony_drink = hint == 'drink_pony'
						drink_name = self.localeItems.HORSE_MILK if pony_drink else self.localeItems.DRAGON_MILK
						drink_source_gui = 'tp_botanik.milchwagen_horse' if pony_drink else 'tp_botanik.fueldispenser_dragon'
						self.log('[PetCare] Pet wants to drink \'{}\'.'.format(drink_name))
						inv = self.ajax_request_inventory()
						drinks = FreggersBot.filter_item(inv, drink_name)
						if len(drinks) == 0:
							self.log('[PetCare] No \'{}\' in inventory.'.format(drink_name))
							if not self.ensure_empty_slots(1):
								self.log('[PetCare] No inventory space available.')
								return False
							drinks_in_queue = FreggersBot.filter_item(self.ajax_request_item_queue(), drink_name)
							if len(drinks_in_queue) == 0:
								self.log('[PetCare] No \'{}\' in item queue either. Collecting new...'.format(drink_name))
								self.go_to_room('tp_botanik.fairy', False)
								self.__e_room_loaded.wait()
								drink_source = self.find_item_by_gui(drink_source_gui)
								if drink_source != None:
									self.log('[PetCare] Drink source found.')
									self.__e_success_cb.clear()
									self.register_callback(Event.NOTIFY_CREATE_ITEM, self.__cb_success)
									self.register_callback(Event.SHOW_ACTION_FEEDBACK, self.__cb_failure)
									count = 0
									for _ in range(3):
										self.__e_success_cb.clear()
										self.send_item_interaction(drink_source.wob_id, 'SEARCH')
										self.__e_success_cb.wait()
										if not self.__success:
											break
										count += 1
									self.log('[PetCare] Collected drink \'{}\' {} times.'.format(drink_name, count))
									self.unregister_callback(Event.NOTIFY_CREATE_ITEM, self.__cb_success)
									self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, self.__cb_failure)	
								else:
									self.log('[PetCare] Could not find drink source for \'{}\'.'.format(drink_name))
									return False
								self.log('[PetCare] Going back to room {}.'.format(room))
								self.go_to_room(room, exact)
								self.__e_room_loaded.wait()
							else:
								self.log('[PetCare] Requesting \'{}\' from item queue...'.format(drink_name))
								dragon_drink = drinks_in_queue.pop(0)
								self.ajax_inbox_action(dragon_drink['id'], Freggers.INBOX_ACTION_ACCEPT)
								self.log('[PetCare] Successfully accepted \'{}\' from item queue.'.format(drink_name))
						self.log('[PetCare] Giving \'{}\' to \'{}\' - {}...'.format(drink_name, wob.name, wob.gui))
						self.send_item_interaction(wob_id, 'PONY_MILK' if pony_drink else 'DRAGON_FUEL')
						time.sleep(2.5)
						self.log('[PetCare] Gave \'{}\' - {} its drink.'.format(wob.name, wob.gui))
					elif hint == 'cuddle_me':
						self.log('[PetCare] Pet needs to be cuddled.')
						self.__e_timer_bar.clear()
						self.send_item_interaction(wob_id, 'PET')
						self.__e_timer_bar.wait()
						time.sleep(self.timer_bar)
					elif hint == 'blanket_purple' or hint == 'blanket_green':
						self.log('[PetCare] Pet needs blanket.')
						green_blanket = hint == 'blanket_green'
						inv = self.ajax_request_inventory()
						imgurl = 'tp_botanik/kuscheldeckegruen_horse' if green_blanket else 'tp_botanik/kuscheldecke_horse'
						blankets = list(filter(lambda item: item != None and imgurl in item['imgurl'], inv))
						if len(blankets) == 0:
							self.log('[PetCare] No blanket in inventory.')
							if not self.ensure_empty_slots(1):
								self.log('[PetCare] No inventory space available.')
								return False
							blankets_in_queue = list(filter(lambda item: item != None and imgurl in item['imgurl'], self.ajax_request_item_queue()))
							if len(blankets_in_queue) == 0:
								self.log('[PetCare] No blanket in item queue. Trying to pickup from room...')
								blanket_gui = 'tp_botanik.kuscheldeckegruen_horse' if green_blanket else 'tp_botanik.kuscheldecke_horse'
								if self.pickup_closest_room_item(blanket_gui):
									self.log('[PetCare] Blanket picked up.')
								else:
									self.log('[PetCare] Buying new blanket...')
									self.ajax_buy_item(2401 if green_blanket else 2400, 20)
									self.log('[PetCare] Bought new blanket.')
							else:
								blanket = blankets_in_queue.pop(0)
								self.ajax_inbox_action(blanket['id'], Freggers.INBOX_ACTION_ACCEPT)
						self.log('[PetCare] Giving blanket to pet...')
						self.send_item_interaction(wob_id, primary_interaction.label)
						time.sleep(2.5)
					elif hint == 'no_blanket_purple' or hint == 'no_blanket_green':
						self.log('[PetCare] Pet wants removal of blanket.')
						self.send_item_interaction(wob_id, 'PONY_NO_BLANKET_PURPLE' if hint == 'no_blanket_purple' else 'PONY_NO_BLANKET_GREEN')
						time.sleep(2.5)
					elif hint == 'no_diaper':
						self.log('[PetCare] Pet wants removal of diaper.')
						for item in self.wob_registry.iso_items.copy():
							if item.gui == 'tp_botanik.windel_horse':
								self.send_item_interaction(item.wob_id, 'USE')
								time.sleep(0.9 + 2)
					elif hint == 'no_dung':
						self.log('[PetCare] Pet wants removal of dung.')
						for item in self.wob_registry.iso_items.copy():
							if item.gui == 'tp_botanik.pferdeapfel2_horse':
								self.send_item_interaction(item.wob_id, 'USE')
								time.sleep(0.9 + 2)
					elif hint == 'musical_box':
						self.log('[PetCare] Pet wants music to be played.')
						for item in self.wob_registry.iso_items:
							if item.gui == 'tp_botanik.spieluhr_horse':
								self.send_item_interaction(item.wob_id, 'USE')
								time.sleep(5)
								break
					elif hint == 'mixed_drink_dragon' or hint == 'mixed_drink_pony':
						pony_drink = hint == 'mixed_drink_pony'
						drink_name = self.localeItems.HORSE_MIXED_MILK if pony_drink else self.localeItems.DRAGON_MIXED_MILK
						self.log('[PetCare] Pet needs mixed drink \'{}\'.'.format(drink_name))
						inv = self.ajax_request_inventory()
						mixed_drinks = FreggersBot.filter_item(inv, drink_name)
						if len(mixed_drinks) == 0:
							self.log('[PetCare] There are no \'{}\' in inventory.'.format(drink_name))
							ingredient_name = self.localeItems.STRAWBERRY if pony_drink else self.localeItems.CHILI
							ingredient_source_gui = 'tp_botanik.erdbeerstaude_horse' if pony_drink else 'tp_botanik.chilistaude_dragon'
							ingredients = FreggersBot.filter_item(inv, ingredient_name)
							ingredient_present = len(ingredients) > 0
							milk_name = self.localeItems.HORSE_MILK if pony_drink else self.localeItems.DRAGON_MILK
							milk_source_gui = 'tp_botanik.milchwagen_horse' if pony_drink else 'tp_botanik.fueldispenser_dragon'
							milks = FreggersBot.filter_item(inv, milk_name)
							milk_present = len(milks) > 0
							empty_slots_needed = (0 if ingredient_present else 1) + (0 if milk_present else 1)
							if empty_slots_needed > 0:
								if not self.ensure_empty_slots(empty_slots_needed):
									self.log('[PetCare] No inventory space available.')
									return False
								inv_queue = self.ajax_request_item_queue()
								ingredients_in_queue = FreggersBot.filter_item(inv_queue, ingredient_name)
								milks_in_queue = FreggersBot.filter_item(inv_queue, milk_name)
								
								if len(ingredients_in_queue) > 0:
									ingredient = ingredients_in_queue.pop()
									self.ajax_inbox_action(ingredient['id'], Freggers.INBOX_ACTION_ACCEPT)
									ingredients.append(ingredient)
									inv.append(ingredient)
									ingredient_present = True
								
								if len(milks_in_queue) > 0:
									milk = milks_in_queue.pop()
									self.ajax_inbox_action(milk['id'], Freggers.INBOX_ACTION_ACCEPT)
									milks.append(milk)
									inv.append(milk)
									milk_present = True
								
								if not milk_present or not ingredient_present:
									self.go_to_room('tp_botanik.fairy', False)
									self.__e_room_loaded.wait()
									
									ingredient_source = self.find_item_by_gui(ingredient_source_gui)
									milk_source = self.find_item_by_gui(milk_source_gui)
									search = ItemSearch(self, 0)
									milk_collected = 0
									ingredient_collected = 0
									
									if not milk_present and not ingredient_present:
										search.wob_id = ingredient_source.wob_id
										if not search.search():
											self.log('[PetCare] Could not collect ingredient \'{}\'.'.format(ingredient_name))
											return False
										search.wob_id = milk_source.wob_id
										if not search.search():
											self.log('[PetCare] Could not collect milk \'{}\'.'.format(milk_name))
											return False
										milk_collected += 1
										ingredient_collected += 1
										self.log('[PetCare] Collected both ingredients \'{}\' and \'{}\' to mix \'{}\'.'.format(milk_name, ingredient_name, drink_name))
									
									search.wob_id = milk_source.wob_id
									for _ in range(max(0, 3 - len(milks) - len(milks_in_queue) - milk_collected)):
										if not search.search():
											self.log('[PetCare] Could not collect milk \'{}\'.'.format(milk_name))
											return False
										
									search.wob_id = ingredient_source.wob_id
									for _ in range(max(0, 3 - len(ingredients) - len(ingredients_in_queue) - ingredient_collected)):
										if not search.search():
											self.log('[PetCare] Could not collect ingredient \'{}\'.'.format(ingredient_name))
											return False
									search.cleanup()
									
									self.log('[PetCare] Going back to room {}.'.format(room))
									self.go_to_room(room, exact)
									self.__e_room_loaded.wait()
							if self.ajax_item_interact(FreggersBot.filter_item(self.ajax_request_inventory(), milk_name)[0]['id'], 'MIX'):
								self.log('[PetCare] Mixed \'{}\' and \'{}\' to \'{}\'.'.format(milk_name, ingredient_name, drink_name))
							else:
								self.log('[PetCare] Error mixing \'{}\' and \'{}\' to \'{}\'.'.format(milk_name, ingredient_name, drink_name))
								return False
						self.send_item_interaction(wob_id, 'PONY_STRAWBERRY_MILK' if pony_drink else 'DRAGON_CHILI_FUEL')
					elif hint == 'food_pony' or hint == 'food_dragon':
						self.log('[PetCare] Pet needs food.')
						pony_food = hint == 'food_pony'
						food_name = self.localeItems.STRAWBERRY if pony_food else self.localeItems.CHILI
						food_item = self.ensure_item_in_inv(food_name)
						if not food_item:
							if food_item == 0:
								self.log('[PetCare] Collecting food \'{}\' 3 times...'.format(food_name))
								food_source_name = 'tp_botanik.erdbeerstaude_horse' if pony_food else 'tp_botanik.chilistaude_dragon'
								self.go_to_room('tp_botanik.fairy', False)
								self.__e_room_loaded.wait()
								food_source = self.find_item_by_gui(food_source_name)
								search = ItemSearch(self, food_source.wob_id)
								for _ in range(3):
									search.search()
								search.cleanup()
								self.log('[PetCare] Collected food \'{}\' 3 times.'.format(food_name))
								self.log('[PetCare] Going back to room {}.'.format(room))
								self.go_to_room(room, exact)
								self.__e_room_loaded.wait()
							else:
								self.log('[PetCare] Could not get food \'{}\' into inventory.'.format(food_name))
								return False
						self.send_item_interaction(wob_id, 'PONY_STRAWBERRY' if pony_food else 'DRAGON_CHILI')
						self.log('[PetCare] Gave pet its food \'{}\'.'.format(food_name))
					elif hint == 'flowers_dragon' or hint == 'flowers_pony':
						pony_flowers = hint == 'flowers_pony'
						flowers_name = self.localeItems.HORSE_FLOWER if pony_flowers else self.localeItems.DRAGON_FLOWER
						flower = self.ensure_item_in_inv(flowers_name, 1976 if pony_flowers else 2399, 20)
						if flower != None:
							self.log('[PetCare] Giving flowers \'{}\' to pet.'.format(flowers_name))
							self.send_item_interaction(wob_id, 'PONY_FLOWERS' if pony_flowers else 'DRAGON_FLOWERS')
							time.sleep(2.5)
						else:
							self.log('[PetCare] Could not get flower \'{}\'.')
							return False
					elif hint == 'activator_dragon' or hint == 'activator_pony':
						pony_activator = hint == 'activator_pony'
						activator_name = self.localeItems.HORSESHOE if pony_activator else self.localeItems.DRAGON_TORCH
						activator_gui = 'tp_botanik.hufeisen_horse' if pony_activator else 'tp_botanik.torch_dragon'
						self.log('[PetCare] Pet needs activator \'{}\'.'.format(activator_name))
						if not FreggersBot.contains(self.ajax_request_inventory(), lambda item: item != None and item['description'] == activator_name):
							self.log('[PetCare] There is no \'{}\' in the inventory.'.format(activator_name))
							if not self.ensure_empty_slots(1):
								self.log('[PetCare] No inventory space available.')
								return False
							if self.pickup_any(activator_gui) == None:
								self.log('[PetCare] Could not pickup a \'{}\' - buying a new one.'.format(activator_name))
								self.ajax_buy_item(1978 if pony_activator else 2403, 20)
							else:
								self.log('[PetCare] Picked up a \'{}\'.'.format(activator_name))
						self.log('[PetCare] Giving dragon torch to pet...')
						self.send_item_interaction(wob_id, 'PONY_HORSE_SHOE' if pony_activator else 'DRAGON_TORCH')
						time.sleep(2.5)
					elif hint == 'magic_clover':
						self.log('[PetCare] Pet needs clover effect.')
						if not self.__care_pet_give_effect(wob_id, self.localeItems.EFFECT_CLOVER, 2164, 3):
							return False
						time.sleep(2.5)
					elif hint == 'magic_DragonSymbols':
						self.log('[PetCare] Pet needs dragon symbols effect.')
						if not self.__care_pet_give_effect(wob_id, self.localeItems.EFFECT_SYMBOLS, 2774, 3):
							return False
						time.sleep(2.5)
					elif hint == 'magic_glitter':
						self.log('[PetCare] Pet needs glitter effect.')
						if not self.__care_pet_give_effect(wob_id, self.localeItems.EFFECT_GLITTER, 2138, 1):
							return False
						time.sleep(2.5)
					elif hint == 'magic_hearts':
						self.log('[PetCare] Pet needs hearts effect.')
						if not self.__care_pet_give_effect(wob_id, self.localeItems.EFFECT_HEARTS, 1977, 5):
							return False
						time.sleep(2.5)
					elif hint == 'magic_stars':
						self.log('[PetCare] Pet needs stars effect.')
						if not self.__care_pet_give_effect(wob_id, self.localeItems.EFFECT_STARS, 2116, 3):
							return False
						time.sleep(2.5)
					elif hint == 'magic_butterflies':
						self.log('[PetCare] Pet needs butterflies effect.')
						if not self.__care_pet_give_effect(wob_id, self.localeItems.EFFECT_BUTTERFLIES, 2242, 3):
							return False
						time.sleep(2.5)
					elif hint == 'magic_snow':
						self.log('[PetCare] Pet needs snowflakes effect.')
						if not self.__care_pet_give_effect(wob_id, self.localeItems.EFFECT_SNOWFLAKES, 2198, 3):
							return False
						time.sleep(2.5)
					elif hint == 'magic_Fire':
						self.log('[PetCare] Pet needs fireball effect.')
						if not self.__care_pet_give_effect(wob_id, self.localeItems.EFFECT_FIREBALL, 2632, 3):
							return False
						time.sleep(2.5)
					else:
						self.log('[PetCare] Unhandled hint:', hint)
						self.log('Pet:', wob.gui, wob.name)
						self.log('Pet interaction:', primary_interaction, wob.interactions)
						self.log('Pet properties:', wob.get_properties())
			time.sleep(2.5)
	
	def go_to_home(self, room, exact):
		self.go_to_room(room + '#@#' + str(self.user_id), exact)
	
	def care_pets(self, room, exact):
		room += '#@#' + str(self.user_id)
		self.go_to_room(room, exact)
		self.__e_room_loaded.wait()
		pets = []
		for item in self.wob_registry.iso_items:
			if item.gui.startswith('tp_botanik.'):
				for pet_gui_prefix in FreggersBot.PET_GUI_PREFIXES:
					if item.gui.startswith(pet_gui_prefix):
						pets.append(item.wob_id)
						break
		self.log('[PetCare] Found {} pets.'.format(len(pets)))
		for pet_wob_id in pets:
			self.__care_pet(pet_wob_id, room, exact)
		self.log('[PetCare] Took care of all pets in room {}.'.format(room))
	
	def find_item_by_gui(self, gui):
		for item in self.wob_registry.iso_items:
			if item.gui == gui:
				return item
		return None
	
	def find_items_by_gui(self, gui):
		list = []
		for item in self.wob_registry.iso_items:
			if item.gui == gui:
				list.append(item)
		return list
	
	def find_item_by_name(self, name):
		for item in self.wob_registry.iso_items:
			if item.name == name:
				return item
		return None
	
	def find_items_by_name(self, name):
		list = []
		for item in self.wob_registry.iso_items:
			if item.name == name:
				list.append(item)
		return list
	
	def find_player_room(self, name):
		if self.wob_registry.get_player_by_name(name) != None:
			return ''
		else:
			req_profile = self._session.get(self.localeItems.URL + '/sidebar/profile/user/' + name)
			if req_profile.status_code == 200:
				text_profile = req_profile.text
				loc_start = text_profile.find('gotoSpecifiedRoom(\'', text_profile.find('user-go-button'))
				if loc_start != -1:
					loc_start += 19
					loc_end = text_profile.find('\'', loc_start)
					loc = text_profile[loc_start:loc_end]
					return loc
		return None
		
	def get_is_badge_completed(self, badge_id, badge_page = None):
		if badge_page == None:
			badge_page = self.get_badge_page()
		if badge_page != None:
			badge_start = badge_page.find('badge_id_' + str(badge_id) + '"')
			if badge_start != -1:
				i = badge_page.find('ba-requirement', badge_start)
				return (badge_page.find('ba-progress-container', badge_start, badge_page.find('ba-badge-desc', badge_start)) == -1 and 
					badge_page.find('ba-requirement-achieved', i, badge_page.find('"', i)) != -1)
		return None
	
	def get_badge_page(self, user_id = None):
		if user_id == None:
			user_id = self.user_id
		req_badges = self._session.get(self.localeItems.URL + '/sidebar/badge/user_badges?user_id=' + user_id)
		if req_badges.status_code == 200:
			return req_badges.text
		return None
	
	def get_badge_tasks(self, badge_id, user_id = None):
		if user_id == None:
			user_id = self.user_id
		req_badge = self._session.get(self.localeItems.URL + '/sidebar/badge/user_badge_detail?badge_id={};user_id={}'.format(badge_id, user_id))
		if req_badge.status_code == 200:
			badge_info = req_badge.text
			tasks = []
			start = badge_info.find('ba-description')
			i = badge_info.find('ba-requirement-todo', start)
			while i != -1:
				tasks.append((i, False))
				i = badge_info.find('ba-requirement-todo', i + 19)
			i = badge_info.find('ba-requirement-done', start)
			while i != -1:
				tasks.append((i, True))
				i = badge_info.find('ba-requirement-done', i + 19)
			result = []
			for x in sorted(tasks, key = lambda x: x[0]):
				result.append(x[1])
			return result
		return None

	def get_has_fregger_check(self):
		if self.__fregger_check != None:
			return self.__fregger_check
		else:
			val = self.get_is_badge_completed(19)
			self.__fregger_check = val
			return val
	
	def get_has_30_visitors_badge(self):
		return self.get_is_badge_completed(13)
	
	def cut_clover(self, amount):
		self.log('[Cut Clover] Cutting {} clover...'.format(amount))
		self.go_to_room('tp_botanik.azubi', False)
		self.__e_room_loaded.wait()
		self.__clover_count = 0
		self.__clover_expect_event = 0
		clover_cut_event = threading.Event()
		def clover_cb_set_hand_held(data):
			if self.__clover_expect_event == 1 and data['gui'] == 'tp_botanik.tp_botanik_klee':
				self.__clover_expect_event = 0
				self.__clover_count = data['count']
				self.__clover_consumer_wob_id = data['consumer_wobids'][0]
				self.log('[Cut Clover] {}/8'.format(self.__clover_count))
				clover_cut_event.set()
		def clover_cb_clear_hand_held():
			if self.__clover_expect_event == 2:
				self.__clover_expect_event = 0
				self.__clover_count = 0
				self.log('[Cut Clover] Put in press.')
				clover_cut_event.set()
		def clover_cb_show_action(data):
			if self.__clover_expect_event == 1:
				self.__clover_expect_event = 0
				self.log('[Cut Clover] Clover not ready yet. Moving on...')
				clover_cut_event.set()
		self.register_callback(Event.SHOW_ACTION_FEEDBACK, clover_cb_show_action)
		self.register_callback(Event.SET_HAND_HELD, clover_cb_set_hand_held)
		self.register_callback(Event.CLEAR_HAND_HELD, clover_cb_clear_hand_held)
		clovers = self.find_items_by_gui('tp_botanik.tp_botanik_klee')
		for _ in range(math.ceil(amount / 8)):
			remaining = min(8, amount)
			while self.__clover_count < remaining:
				clovers_copy = list(clovers)
				for _ in range(len(clovers)):
					clover = self.closest_iso_item(clovers_copy)
					clovers_copy.remove(clover)
					clover_cut_event.clear()
					self.__clover_expect_event = 1
					self.send_item_interaction(clover.wob_id, 'CUT')
					clover_cut_event.wait()
					self.wait_random_delay(0.3, 1.5)
					if self.__clover_count >= remaining:
						break
			clover_cut_event.clear()
			self.__clover_expect_event = 2
			self.send_use_handheld_with(self.__clover_consumer_wob_id)
			clover_cut_event.wait()
			self.wait_random_delay(0.3, 2.5)
		self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, clover_cb_show_action)
		self.unregister_callback(Event.SET_HAND_HELD, clover_cb_set_hand_held)
		self.unregister_callback(Event.CLEAR_HAND_HELD, clover_cb_clear_hand_held)
		del self.__clover_consumer_wob_id
		del self.__clover_count
		del self.__clover_expect_event
		self.log('[Cut Clover] Done.')
	
	def unwrap_gifts(self, max_amount = 7):
		guis = ['wutzlhofen.kiste_a_tutorial', 'wutzlhofen.kiste_b_tutorial', 'wutzlhofen.kiste_c_tutorial', 'wutzlhofen.kiste_d_tutorial', 'wutzlhofen.kiste_f_tutorial', 'wutzlhofen.kiste_h_tutorial']
		unwrap_target_map = {
			self.localeItems.GIFT_0: (49, 182, 47, 0),
			self.localeItems.GIFT_1: (157, 208, 47, 6),
			self.localeItems.GIFT_2: (21, 176, 47, 0),
			self.localeItems.GIFT_3: (68, 149, 47, 6),
			self.localeItems.GIFT_4: (152, 150, 47, 0),
			self.localeItems.GIFT_5: (156, 228, 47, 0),
			self.localeItems.GIFT_6: (28, 266, 47, 0),
			self.localeItems.GIFT_7: (156, 228, 47, 0),
			self.localeItems.GIFT_8: (68, 149, 47, 6),
			self.localeItems.GIFT_9: (21, 278, 47, 0),
			self.localeItems.GIFT_10: (157, 155, 47, 0)
		}
		self.log('[Unwrap Gifts] Unwrapping up to {} gift(s)...'.format(max_amount))
		if not self.ensure_empty_slots(1):
			self.log('[Unwrap Gifts] No inventory space available.')
			return False
		self.go_to_home(FreggersBot.AP_APARTMENT, False)
		self.__e_room_loaded.wait()
		
		unwrap_event = threading.Event()
		place_event = threading.Event()
		def unwrap_cb_notify_inv(data):
			unwrap_event.set()
		def unwrap_cb_env_stat(data):
			if data['wobid'] == self.player.wob_id and data['status'] == Status.CARRYING and data['value'] == None:
				place_event.set()
		self.register_callback(Event.NOTIFY_INVENTORY, unwrap_cb_notify_inv)
		self.register_callback(Event.ENV_STAT, unwrap_cb_env_stat)
		count = 0
		
		def place_objects():
			for item in self.ajax_request_inventory():
				if item != None and item['description'] in unwrap_target_map:
					self.ajax_item_interact(item['id'], 'PLACE')
					place_event.clear()
					self.send_place_object(*unwrap_target_map[item['description']])
					place_event.wait()
					self.log('[Unwrap Gifts] Placed \'{}\'.'.format(item['description']))
		
		for iso_item in list(self.wob_registry.iso_items):
			if iso_item.gui in guis:
				if count >= max_amount:
					break
				self.log('[Unwrap Gifts] Found gift {} - unwrapping...'.format(iso_item.gui))
				unwrap_event.clear()
				self.send_item_interaction(iso_item.wob_id, 'UNWRAP')
				unwrap_event.wait()
				place_objects()
				count += 1
				self.log('[Unwrap Gifts] {}/{}'.format(count, max_amount))
		place_objects()
		self.unregister_callback(Event.NOTIFY_INVENTORY, unwrap_cb_notify_inv)
		self.unregister_callback(Event.ENV_STAT, unwrap_cb_env_stat)
		self.log('[Unwrap Gifts] Unwrapped {}/{} gift(s).'.format(count, max_amount))
		return count
	
	def feed_sheeps(self):
		self.log('[Feed Sheeps] Giving clover to sheeps...')
		self.go_to_room('tp_botanik.azubi', False)
		self.__e_room_loaded.wait()
		
		self.__feedsheeps_expect_event = 0
		feed_event = threading.Event()
		weed_source = self.find_item_by_gui('tp_botanik.grashaufen')
		sheeps = self.find_items_by_gui('tp_botanik.schaf')
		
		def feed_sheeps_cb_set_hand_held(data):
			if self.__feedsheeps_expect_event == 1 and data['gui'] == 'tp_botanik.powerriegel':
				self.__feedsheeps_expect_event = 0
				feed_event.set()
				self.log('[Feed Sheeps] Collected {}x clover.'.format(data['count']))
		def feed_sheeps_cb_update_wob(data):
			if self.__feedsheeps_expect_event == 2 and data.effect != None and data.effect.gui == 'dotsflowup':
				self.__feedsheeps_expect_event = 0
				feed_event.set()
				self.log('[Feed Sheeps] Fed sheep.')
		
		self.register_callback(Event.SET_HAND_HELD, feed_sheeps_cb_set_hand_held)
		self.register_callback(Event.ACTION_UPDATE_WOB, feed_sheeps_cb_update_wob)
		
		self.__feedsheeps_expect_event = 1
		self.send_item_interaction(weed_source.wob_id, 'TAKE_POWERRIEGEL')
		feed_event.wait()
		sheeps = self.sort_iso_items_by_distance(sheeps)
		
		self.wait_random_delay(0.5, 2.5)
		
		for x in range(2):
			for sheep in sheeps:
				feed_event.clear()
				self.__feedsheeps_expect_event = 2
				self.send_use_handheld_with(sheep.wob_id)
				feed_event.wait()
				self.wait_random_delay(0.5, 2)
			if x == 0:
				self.wait_random_delay(3.7, 4)
			self.wait_random_delay(0.5, 3)
		
		self.unregister_callback(Event.SET_HAND_HELD, feed_sheeps_cb_set_hand_held)
		self.unregister_callback(Event.ACTION_UPDATE_WOB, feed_sheeps_cb_update_wob)
		del self.__feedsheeps_expect_event
		
		self.log('[Feed Sheeps] Done.')
		
	def complete_quest(self):
		quest = self.quest
		if quest != None:
			self.__e_quest_done.clear()
			self.log('[Quest] Completing quest \'{}\'...'.format(quest))
			if quest == 'DAILY_SEASON_EASTER_DELIVER_EGGS':
				eggs_in_inv = self.filter_items(self.ajax_request_inventory(), self.localeItems.EASTER_EGGS)
				if len(eggs_in_inv) == 0 and not self.ensure_empty_slots(1):
					self.log('[Quest] No inventory space available.')
					return False
				eggs_in_queue = None
				eggs_count = 0
				for egg_slot in eggs_in_inv:
					eggs_count += egg_slot['count']
				if eggs_count < 10:
					eggs_in_queue = self.filter_items(self.ajax_request_item_queue(), self.localeItems.EASTER_EGGS)
					missing_eggs = 10 - eggs_count - len(eggs_in_queue)
					if missing_eggs > 0:
						self.log('[Quest] Collecting {} easter eggs.'.format(missing_eggs))
						self.collect_eggs(max_amount = missing_eggs)
						eggs_in_queue = self.filter_items(self.ajax_request_item_queue(), self.localeItems.EASTER_EGGS)
						eggs_in_inv = self.filter_items(self.ajax_request_inventory(), self.localeItems.EASTER_EGGS)
				
				self.go_to_room('wutzlhofen.park', False)
				self.__e_room_loaded.wait()
				target = self.find_item_by_gui('tp_botanik.monstereasterbasket')
				if target == None:
					self.log('[Quest] Could not find monster easter egg.')
					return False
				
				for _ in range(10):
					egg = None
					if len(eggs_in_inv) == 0:
						egg = eggs_in_queue.pop(0)
						self.ajax_inbox_action(egg['id'], Freggers.INBOX_ACTION_ACCEPT)
						self.log('[Quest] Accepted egg from queue.')
					else:
						egg = eggs_in_inv[0]
						if egg['count'] == 1:
							del eggs_in_inv[0]
						else:
							egg['count'] -= 1
					self.ajax_item_usewith(egg['id'], target.wob_id)
					self.log('[Quest] Threw egg at the monster easter egg.')
					self.wait_random_delay(0.5, 2.5)
				
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			elif quest == 'TUTORIAL_UNWRAP_ALL_BOXES': #2
				self.log('[Quest] Unwrapping a gift in the apartment...')
				if self.unwrap_gifts(max_amount = 1) == 0:
					self.log('[Quest] Could not unwrap a gift.')
					return False
				self.__e_quest_done.wait()
				self.log('[Quest] Completed. Completing next...')
				return self.complete_quest()
			elif quest == 'TUTORIAL_UNWRAP_AND_PLACE' or quest == 'TUTORIAL_PLACE_ALL_ITEMS': #3
				self.log('[Quest] Unwrapping and placing all gifts in the apartment...')
				self.unwrap_gifts(max_amount = 6)
				if not self.__e_quest_done.wait(3):
					inv = self.ajax_request_inventory()
					slot_count = len(inv)
					if not self.ensure_empty_slots(slot_count - 3, inv = inv):
						self.log('[Quest] No inventory space available.')
						return False
					for item in inv:
						if item != None:
							item_menu = self.ajax_item_menu(item['id'], 'display')
							print(item_menu)
							break
					self.__e_quest_done.wait()
				self.log('[Quest] Completed. Completing next...')
				return self.complete_quest()
			elif quest == 'TUTORIAL_DELIVER_CLOVER': #4
				self.cut_clover(amount = 6)
				self.__e_quest_done.wait()
				self.log('[Quest] Completed. Completing next...')
				return self.complete_quest()
			elif quest == 'TUTORIAL_FIND_EIGENHEIM': #1
				self.log('[Quest] Going to apartment...')
				self.go_to_home(FreggersBot.AP_APARTMENT, False)
				self.__e_quest_done.wait()
				self.log('[Quest] Completed. Completing next...')
				return self.complete_quest()
			elif quest == 'TUTORIAL_FEED_THE_SHEEP': #5
				self.log('[Quest] Feeding 6 sheeps...')
				self.feed_sheeps()
				self.__e_quest_done.wait()
				self.log('[Quest] Completed. Completing next...')
				return self.complete_quest()
			elif quest == 'TUTORIAL_COLLECT_FIRST_INGREDIENT': #6
				self.log('[Quest] Collecting wood...')
				self.go_to_room('tp_botanik.azubi', False)
				self.__e_room_loaded.wait()
				wood_source = self.find_item_by_gui('western.stumpfmitbeil_dispenser')
				self.send_item_interaction(wood_source.wob_id, 'SEARCH')
				self.__e_quest_done.wait()
				self.log('[Quest] Completed. Completing next...')
				return self.complete_quest()
			elif quest == 'TUTORIAL_CRAFT_ITEM': #7
				self.log('[Quest] Crafting item...')
				wood_in_inv = self.filter_item(self.ajax_request_inventory(), self.localeItems.WOOD)
				if len(wood_in_inv) == 0:
					if not self.ensure_empty_slots(1):
						self.log('[Quest] No inventory space available.')
						return False
					wood_in_queue = self.filter_item(self.ajax_request_item_queue(), self.localeItems.WOOD)
					if len(wood_in_queue) == 0:
						self.log('[Quest] Collecting wood...')
						self.go_to_room('tp_botanik.azubi', False)
						self.__e_room_loaded.wait()
						wood_source = self.find_item_by_gui('western.stumpfmitbeil_dispenser')
						self.send_item_interaction(wood_source.wob_id, 'SEARCH')
						self.__e_quest_done.wait()
					else:
						self.log('[Quest] Accepting wood from item queue...')
						self.ajax_inbox_action(wood_in_queue[0]['id'], Freggers.INBOX_ACTION_ACCEPT)
				self.craft_item(20, 8, 0)
				self.__e_quest_done.wait()
				self.log('[Quest] Completed. Completing next...')
				return self.complete_quest()
			elif quest == 'TUTORIAL_UNLOCK_CRAFTING_CATEGORY': #8
				self.log('[Quest] Unlocking crafting category...')
				self.__e_level_data.wait()
				if self.level_data['level'] == 1:
					self.collect_ants(max_amount = 3)
					self.deliver_ants(amount = 3)
				self.unlock_crafting_category(25)
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return self.complete_quest()
			elif quest == 'DAILY_DELIVER_SNAILS':
				self.log('[Quest] Collecting 3 snails...')
				self.go_to_room('tp_botanik.azubi', False)
				self.__e_room_loaded.wait()
				self.__snail_count = 0
				self.__snail_consumer_wob_id = None
				snail_pickup_event = threading.Event()
				def snail_cb_set_hand_held(data):
					if data['gui'] == 'tp_botanik.eimerschnecken':
						self.__snail_count = data['count']
						self.__snail_consumer_wob_id = data['consumer_wobids'][0]
						self.log('[Quest] Snail picked up ({}/4).'.format(self.__snail_count))
						snail_pickup_event.set()
				self.register_callback(Event.SET_HAND_HELD, snail_cb_set_hand_held)
				snail_guis = ['tp_botanik.schneckegelb', 'tp_botanik.schneckerot', 'tp_botanik.schneckelila', 'tp_botanik.schneckeblau']
				while self.__snail_count < 4:
					for iso_item in list(self.wob_registry.iso_items):
						if iso_item.gui in snail_guis:
							snail_pickup_event.clear()
							self.send_item_interaction(iso_item.wob_id, 'FILL_BUCKET')
							snail_pickup_event.wait()
							if self.__snail_count >= 4:
								break
					time.sleep(0.1)
				self.log('[Quest] Picked up {} snails. Delivering...'.format(self.__snail_count))
				self.send_use_handheld_with(self.__snail_consumer_wob_id)
				self.__e_quest_done.wait()
				self.unregister_callback(Event.SET_HAND_HELD, snail_cb_set_hand_held)
				del self.__snail_count
				del self.__snail_consumer_wob_id
				self.log('[Quest] Completed.')
				return True
			elif quest == 'DAILY_RETURN_EMPTY_BOTTLES':
				self.log('[Quest] Collecting 3 empty bottles...')
				self.collect_bottles(max_amount = 3)
				if self.return_bottles(amount = 3, beer_crates = False) == 3:
					self.__e_quest_done.wait()
					self.log('[Quest] Completed.')
					return True
				self.log('[Quest] Could not return 3 empty bottles.')
				return False
			elif quest == 'DAILY_DELIVER_DUNG':
				self.log('[Quest] Delivering 8 buckets of dung to the composter...')
				self.go_to_room('tp_botanik.azubi', False)
				self.__e_room_loaded.wait()
				self.__dung_count = 0
				self.__dung_consumer_wob_id = None
				self.__dung_expect_event = 0
				self.__dung_success = False
				self.__dung_sheep_wob_id = None
				self.__dung_sheep_state = 0
				dung_event = threading.Event()
				def dung_cb_set_hand_held(data):
					if self.__dung_expect_event == 1 and data['gui'] == 'tp_botanik.eimerkacke':
						self.__dung_expect_event = 0
						self.__dung_count = data['count']
						self.__dung_consumer_wob_id = data['consumer_wobids'][0]
						self.log('[Quest] Dung collected ({}/4).'.format(self.__dung_count))
						dung_event.set()
					elif self.__dung_expect_event == 3 and data['gui'] == 'tp_botanik.powerriegel':
						self.__dung_expect_event = 0
						dung_event.set()
						self.log('[Quest] Collected clover ({}) to feed sheep.'.format(data['count']))
				def dung_cb_show_action(data):
					if self.__dung_expect_event == 1:
						self.__dung_expect_event = 0
						self.__dung_success = False
						dung_event.set()
				def dung_cb_update_wob(data):
					if self.__dung_expect_event == 2:
						if data.effect != None:
							if data.effect.gui == 'poof':
								self.__dung_expect_event = 0
								self.__dung_sheep_state = 1
								dung_event.set()
						elif data.animation != None:
							if data.animation.name == 'happy':
								self.__dung_expect_event = 0
								self.__dung_sheep_state = 2
								dung_event.set()
							elif data.animation.name == 'needtopee':
								self.__dung_expect_event = 0
								self.__dung_sheep_state = 3
								dung_event.set()
					elif self.__dung_expect_event == 4:
						if data.effect != None:
							if data.effect.gui == 'dotsflowup':
								self.__dung_expect_event = 0
								dung_event.set()
				def dung_cb_clear_hand_held():
					if self.__dung_expect_event == 5:
						self.__dung_expect_event = 0
						dung_event.set()
				
				self.register_callback(Event.SET_HAND_HELD, dung_cb_set_hand_held)
				self.register_callback(Event.SHOW_ACTION_FEEDBACK, dung_cb_show_action)
				self.register_callback(Event.ACTION_UPDATE_WOB, dung_cb_update_wob)
				self.register_callback(Event.CLEAR_HAND_HELD, dung_cb_clear_hand_held)
				
				toilets = self.find_items_by_gui('tp_botanik.dixieklo')
				sheeps = self.find_items_by_gui('tp_botanik.schaf')
				weed_source = self.find_item_by_gui('tp_botanik.grashaufen')
				
				for _ in range(2):
					while self.__dung_count < 4:
						for sheep in sheeps:
							self.log('[Quest] Petting sheep...')
							dung_event.clear()
							self.__dung_sheep_state = 0
							self.__dung_expect_event = 2
							self.send_item_interaction(sheep.wob_id, 'PAT')
							dung_event.wait()
							if self.__dung_sheep_state == 2:
								self.log('[Quest] Feeding sheep, before retrying to pet...')
								dung_event.clear()
								self.__dung_expect_event = 3
								self.send_item_interaction(weed_source.wob_id, 'TAKE_POWERRIEGEL')
								dung_event.wait()
								self.log('[Quest] Giving clover to sheeps...')
								for s in sheeps:
									dung_event.clear()
									self.__dung_expect_event = 4
									self.send_use_handheld_with(s.wob_id)
									dung_event.wait()
								self.send_clear_handheld()
								dung_event.clear()
								self.__dung_expect_event = 2
								self.send_item_interaction(sheep.wob_id, 'PAT')
								dung_event.wait()
						for toilet in toilets:
							self.log('[Quest] Collecting dung from toilet...')
							dung_event.clear()
							self.__dung_expect_event = 1
							self.send_item_interaction(toilet.wob_id, 'FILL_BUCKET')
							dung_event.wait()
							if self.__dung_count >= 4:
								break
					self.log('[Quest] Bringing dung to the compost...')
					dung_event.clear()
					self.__dung_expect_event = 5
					self.send_use_handheld_with(self.__dung_consumer_wob_id)
					dung_event.wait()
					self.__dung_count = 0
					self.log('[Quest] Dung is in compost.')
				self.unregister_callback(Event.SET_HAND_HELD, dung_cb_set_hand_held)
				self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, dung_cb_show_action)
				self.unregister_callback(Event.ACTION_UPDATE_WOB, dung_cb_update_wob)
				self.unregister_callback(Event.CLEAR_HAND_HELD, dung_cb_clear_hand_held)
				del self.__dung_count
				del self.__dung_consumer_wob_id
				del self.__dung_expect_event
				del self.__dung_success
				del self.__dung_sheep_wob_id
				del self.__dung_sheep_state
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			elif quest == 'DAILY_WATER_THE_PLANTS':
				self.log('[Quest] Watering 6 exotic plants...')
				self.go_to_room('tp_botanik.azubi', False)
				self.__e_room_loaded.wait()
				water_source = self.find_item_by_gui('tp_botanik.trog')
				watering_event = threading.Event()
				self.__watering_pump_success = False
				self.__watering_expect_event = 0
				self.__water_count = 0
				self.__watering_target_wob_ids = None
				def watering_cb_show_action(data):
					if self.__watering_expect_event == 1 and data == self.localeItems.ENOUGH_WATER:
						self.__watering_expect_event = 0
						watering_event.set()
				def watering_cb_update_wob(data):
					if (self.__watering_expect_event == 1 or self.__watering_expect_event == 3) and data.effect != None and data.effect.gui == 'dotsflowup':
						self.__watering_expect_event = 0
						self.__watering_pump_success = True
						watering_event.set()
				def watering_cb_set_hand_held(data):
					if self.__watering_expect_event == 2 and data['gui'] == 'tp_botanik.giesskanne':
						self.__watering_expect_event = 0
						if self.__watering_target_wob_ids == None:
							self.__watering_target_wob_ids = data['consumer_wobids']
						self.__water_count = data['count']
						self.log('[Quest] Collected water ({}/3).'.format(self.__water_count))
						watering_event.set()
						
				self.register_callback(Event.SHOW_ACTION_FEEDBACK, watering_cb_show_action)
				self.register_callback(Event.ACTION_UPDATE_WOB, watering_cb_update_wob)
				self.register_callback(Event.SET_HAND_HELD, watering_cb_set_hand_held)

				for _ in range(2):
					while self.__water_count < 3:
						self.__watering_expect_event = 1
						watering_event.clear()
						self.send_item_interaction(water_source.wob_id, 'PUMP')
						watering_event.wait()
						self.wait_random_delay(2.1, 3.5)
						if self.__watering_pump_success:
							watering_event.clear()
							self.__watering_expect_event = 1
							self.send_item_interaction(water_source.wob_id, 'PUMP')
							watering_event.wait()
							self.wait_random_delay(2.1, 3.5)
						watering_event.clear()
						self.__watering_expect_event = 2
						self.send_item_interaction(water_source.wob_id, 'TAKE_WATER')
						watering_event.wait()
						self.wait_random_delay(0.3, 2.5)
					for _ in range(self.__water_count):
						plant_wob_id = self.__watering_target_wob_ids.pop(random.randint(0, len(self.__watering_target_wob_ids) - 1))
						self.log('[Quest] Watering exotic plant...')
						watering_event.clear()
						self.__watering_expect_event = 3
						self.send_use_handheld_with(plant_wob_id)
						watering_event.wait()
						self.log('[Quest] Watered exotic plant.')
						self.wait_random_delay(0.3, 1.5)
					self.__water_count = 0
				self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, watering_cb_show_action)
				self.unregister_callback(Event.ACTION_UPDATE_WOB, watering_cb_update_wob)
				self.unregister_callback(Event.SET_HAND_HELD, watering_cb_set_hand_held)
				del self.__watering_pump_success
				del self.__watering_expect_event
				del self.__water_count
				del self.__watering_target_wob_ids
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			elif quest == 'DAILY_DELIVER_FERTILIZER':
				self.log('[Quest] Delivering fertilizer to 6 exotic plants...')
				self.go_to_room('tp_botanik.azubi', False)
				self.__e_room_loaded.wait()
				fertilizer_source = self.find_item_by_gui('tp_botanik.komposthaufen')
				fertilize_event = threading.Event()
				self.__fertilize_expect_event = 0
				self.__fertilizer_count = 0
				self.__fertilizer_target_wob_ids = None
				def fertilize_cb_set_handheld(data):
					if self.__fertilize_expect_event == 1 and data['gui'] == 'tp_botanik.dungersack':
						self.__fertilize_expect_event = 0
						self.__fertilizer_count = data['count']
						if self.__fertilizer_target_wob_ids == None:
							self.__fertilizer_target_wob_ids = data['consumer_wobids']
						fertilize_event.set()
				def fertilize_cb_timer_bar(data):
					if self.__fertilize_expect_event == 2:
						self.__fertilize_expect_event = 0
						fertilize_event.set()
					print(data)
				self.register_callback(Event.SHOW_TIMER_BAR, fertilize_cb_timer_bar)
				self.register_callback(Event.SET_HAND_HELD, fertilize_cb_set_handheld)
				for _ in range(2):
					while self.__fertilizer_count < 4:
						self.__fertilize_expect_event = 1
						fertilize_event.clear()
						self.send_item_interaction(fertilizer_source.wob_id, 'TAKE_DUENGER') #Timerbar: 800
						fertilize_event.wait()
						self.wait_random_delay(0.8, 2)
					for _ in range(self.__fertilizer_count):
						plant_wob_id = self.__fertilizer_target_wob_ids.pop(random.randint(0, len(self.__fertilizer_target_wob_ids) - 1))
						self.log('[Quest] Giving fertilizer to exotic plant...')
						fertilize_event.clear()
						self.__fertilize_expect_event = 2
						self.send_use_handheld_with(plant_wob_id) #Timerbar: 1600
						fertilize_event.wait()
						self.log('[Quest] Gave fertilizer to exotic plant.') 
						self.wait_random_delay(1.6, 3)
					self.__fertilizer_count = 0
				self.unregister_callback(Event.SHOW_TIMER_BAR, fertilize_cb_timer_bar)
				self.unregister_callback(Event.SET_HAND_HELD, fertilize_cb_set_handheld)
				del self.__fertilize_expect_event
				del self.__fertilizer_count
				del self.__fertilizer_target_wob_ids
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			elif quest == 'DAILY_DELIVER_MUSHROOMS':
				self.log('[Quest] Collecting 6 mushrooms...')
				guis = ['gothics.schwammerl1',
						'gothics.schwammerl3',
						'gothics.dickesschwammerl1',
						'gothics.dickesschwammerl4',
						'gothics.schwammerl5',
						'gothics.dickesschwammerl3',
						'gothics.dickesschwammerl5',
						'gothics.schwammerl2']
				inv = self.ajax_request_inventory()
				queue = self.ajax_request_item_queue()

				if self.count_item(inv, self.localeItems.MUSHROOM_BIG_BLUE) > 0 or self.count_item(queue, self.localeItems.MUSHROOM_BIG_BLUE) > 0:
					guis.remove('gothics.schwammerl1')
				if self.count_item(inv, self.localeItems.MUSHROOM_BIG_RED) > 0 or self.count_item(queue, self.localeItems.MUSHROOM_BIG_RED) > 0:
					guis.remove('gothics.schwammerl2')
				if self.count_item(inv, self.localeItems.MUSHROOM_BIG_BROWN) > 0 or self.count_item(queue, self.localeItems.MUSHROOM_BIG_BROWN) > 0:
					guis.remove('gothics.schwammerl5')
				if self.count_item(inv, self.localeItems.MUSHROOM_BIG_GRAY) > 0 or self.count_item(queue, self.localeItems.MUSHROOM_BIG_GRAY) > 0:
					guis.remove('gothics.schwammerl3')
				if self.count_item(inv, self.localeItems.MUSHROOM_SMALL_BROWN) > 0 or self.count_item(queue, self.localeItems.MUSHROOM_SMALL_BROWN) > 0:
					guis.remove('gothics.dickesschwammerl1')
				if self.count_item(inv, self.localeItems.MUSHROOM_SMALL_GRAY) > 0 or self.count_item(queue, self.localeItems.MUSHROOM_SMALL_GRAY) > 0:
					guis.remove('gothics.dickesschwammerl4')
				if self.count_item(inv, self.localeItems.MUSHROOM_SMALL_ORANGE) > 0 or self.count_item(queue, self.localeItems.MUSHROOM_SMALL_ORANGE) > 0:
					guis.remove('gothics.dickesschwammerl3')
				if self.count_item(inv, self.localeItems.MUSHROOM_SMALL_WHITE) > 0 or self.count_item(queue, self.localeItems.MUSHROOM_SMALL_WHITE) > 0:
					guis.remove('gothics.dickesschwammerl5')
				
				if len(guis) > 2:
					self.go_to_room('gothics.raum9', False)
					self.__e_room_loaded.wait()
					self.go_to_room('gothics.friedhof', False)
					self.__e_room_loaded.wait()
					self.go_to_room('gothics.eule', False)
					self.__e_room_loaded.wait()
					self.__mushrooms_expect_gui = None
					self.__mushrooms_pickup_wob_id = None
					self.__mushrooms_pickup_success = False
					self.__mushrooms_collected = 0
					mushroom_pickup_event = threading.Event()
					def mushrooms_cb_create_item(data):
						if data['gui'] == self.__mushrooms_expect_gui:
							self.__mushrooms_collected += 1
							self.__mushrooms_pickup_success = True
					def mushrooms_cb_env_remove_item(data):
						if self.__mushrooms_pickup_wob_id in data['wobids']:
							mushroom_pickup_event.set()
					def mushrooms_cb_show_action(data):
						if data == self.localeItems.MUSHROOM_ALREADY_IN_INV:
							self.__mushrooms_pickup_success = True
							mushroom_pickup_event.set()
					self.register_callback(Event.NOTIFY_CREATE_ITEM, mushrooms_cb_create_item)
					self.register_callback(Event.ENV_REMOVE_ITEMS, mushrooms_cb_env_remove_item)
					self.register_callback(Event.SHOW_ACTION_FEEDBACK, mushrooms_cb_show_action)
					while self.__mushrooms_collected < 6 and len(guis) > 0:
						mushroom = self.closest_iso_item(list(filter(lambda iso_item: iso_item.gui in guis, self.wob_registry.iso_items)))
						self.log('[Quest] Picking up mushroom \'{}\'...'.format(mushroom.name))
						self.__mushrooms_expect_gui = mushroom.gui
						self.__mushrooms_pickup_success = False
						self.__mushrooms_pickup_wob_id = mushroom.wob_id
						mushroom_pickup_event.clear()
						count_before = self.__mushrooms_collected
						self.send_item_interaction(mushroom.wob_id, 'USE')
						mushroom_pickup_event.wait()
						if self.__mushrooms_pickup_success:
							guis.remove(mushroom.gui)
							if count_before < self.__mushrooms_collected:
								self.log('[Quest] Picked up mushroom \'{}\'.'.format(mushroom.name))
						self.wait_random_delay(FreggersBot.MIN_SEARCH_DONE_DELAY, FreggersBot.MAX_SEARCH_DONE_DELAY)
					self.unregister_callback(Event.NOTIFY_CREATE_ITEM, mushrooms_cb_create_item)
					self.unregister_callback(Event.ENV_REMOVE_ITEMS, mushrooms_cb_env_remove_item)
					self.unregister_callback(Event.SHOW_ACTION_FEEDBACK, mushrooms_cb_show_action)
					del self.__mushrooms_expect_gui
					del self.__mushrooms_pickup_wob_id
					del self.__mushrooms_pickup_success
					del self.__mushrooms_collected
				self.go_to_room('western.rail', False)
				self.__e_room_loaded.wait()
				self.go_to_room('western.indianerdorf', False)
				self.__e_room_loaded.wait()
				
				mushrooms_in_inv = len(self.filter_items(self.ajax_request_inventory(), self.localeItems.MUSHROOMS))
				if mushrooms_in_inv == 0 and not self.ensure_empty_slots(1):
					self.log('[Quest] No inventory space available.')
					return False
				
				mushrooms_in_queue = self.filter_items(self.ajax_request_item_queue(), self.localeItems.MUSHROOMS)
				mushroom_deliver_event = threading.Event()
				def mushrooms_cb_timer_bar(data):
					mushroom_deliver_event.set()
				self.register_callback(Event.SHOW_TIMER_BAR, mushrooms_cb_timer_bar)
				
				target = self.find_item_by_gui('western.feuerstelle_topf')
				len_mushrooms = mushrooms_in_inv + len(mushrooms_in_queue)
				for _ in range(len_mushrooms):
					if mushrooms_in_inv == 0:
						item = mushrooms_in_queue.pop(0)
						self.ajax_inbox_action(item['id'], Freggers.INBOX_ACTION_ACCEPT)
					else:
						mushrooms_in_inv -= 1
					mushroom_deliver_event.clear()
					self.send_item_interaction(target.wob_id, 'DELIVER_MUSHROOM')
					mushroom_deliver_event.wait()
					self.log('[Quest] Delivered mushroom.')
					self.wait_random_delay(1, 2.5)
				self.unregister_callback(Event.SHOW_TIMER_BAR, mushrooms_cb_timer_bar)
				self.log('[Quest] Delivered {} mushrooms.'.format(len_mushrooms))
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			elif quest == 'DAILY_DELIVER_ANTS':
				self.log('[Quest] Delivering 2 ants...')
				ant_count = (len(self.filter_items(self.ajax_request_inventory(), self.localeItems.LAZY_ANTS)) + 
							len(self.filter_items(self.ajax_request_item_queue(), self.localeItems.LAZY_ANTS)))
				remaining = 2 - ant_count
				if remaining > 0:
					self.collect_ants(max_amount = remaining)
				self.deliver_ants(amount = 2)
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			elif quest == 'DAILY_DELIVER_CLOVER':
				self.cut_clover(amount = 16)
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			elif quest == 'DAILY_FEED_THE_SHEEP':
				self.log('[Quest] Feeding 6 sheeps...')
				self.feed_sheeps()
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			elif quest == 'DAILY_REMOVE_PARASITES':
				self.log('[Quest] Removing parasites from 9 exotic plants...')
				self.go_to_room('tp_botanik.azubi', False)
				self.__e_room_loaded.wait()
				bugs_event = threading.Event()
				def bugs_cb_timer_bar(data):
					bugs_event.set()
				self.register_callback(Event.SHOW_TIMER_BAR, bugs_cb_timer_bar)
				plants = list(filter(lambda iso_item: iso_item.has_interaction('REMOVE_BUGS'), self.wob_registry.iso_items))
				for _ in range(len(plants)):
					plant = self.sort_iso_items_by_distance(plants)[0]
					plants.remove(plant)
					bugs_event.clear()
					self.send_item_interaction(plant.wob_id, 'REMOVE_BUGS')
					bugs_event.wait()
					self.wait_random_delay(0.6, 1.8)
				self.unregister_callback(Event.SHOW_TIMER_BAR, bugs_cb_timer_bar)
				self.__e_quest_done.wait()
				self.log('[Quest] Completed.')
				return True
			else:
				print('[Quest] Unknown quest:', quest)
		return False
	
	def complete_badges(self):
		search = ItemSearch(self, 0)
		def search_badge_item(wob_id):
			search.wob_id = wob_id
			search.search()
			self.wait_random_delay(0.5, 3.5)
		badge_page = self.get_badge_page()
		if not self.get_is_badge_completed(8, badge_page = badge_page):
			self.log('[Badge] Completing explorer badge - Wutzlhofen...')
			tasks = self.get_badge_tasks(8)
			if not tasks[0]:
				self.go_to_room('wutzlhofen.flussdampfer', False)
				self.wait_room_loaded()
				search_badge_item(self.find_item_by_gui('wutzlhofen.flussdampfer_kabeltrommel').wob_id)
			if not tasks[1]:
				self.go_to_room('wutzlhofen.biergarten', False)
				self.wait_room_loaded()
				search_badge_item(self.find_item_by_gui('wutzlhofen.biergarten_biergartenschirmstaender').wob_id)
			if not tasks[2]:
				self.go_to_room('wutzlhofen.bistro', False)
				self.wait_room_loaded()
				search_badge_item(next(filter(lambda x: x.has_interaction('SEARCH'), self.find_items_by_gui('wutzlhofen.bistro_sofadreisitzer'))).wob_id)
		if not self.get_is_badge_completed(9):
			self.log('[Badge] Completing explorer badge - Hood...')
			tasks = self.get_badge_tasks(9)
			if not tasks[0]:
				self.go_to_room('hood.outskirts', False)
				self.wait_room_loaded()
				search_badge_item(next(filter(lambda x: x.has_interaction('SEARCH'), self.find_items_by_gui('hood.outskirts_muellhaufen'))).wob_id)
			if not tasks[1]:
				self.go_to_room('hood.strasse', False)
				self.wait_room_loaded()
				search_badge_item(self.find_item_by_gui('hood.strasse_muelltonneliegend').wob_id)
			if not tasks[2]:
				self.go_to_room('hood.waschsalon', False)
				self.wait_room_loaded()
				search_badge_item(next(filter(lambda x: x.has_interaction('SEARCH'), self.find_items_by_gui('hood.waschsalon_waschmaschine'))).wob_id)
		if not self.get_is_badge_completed(10):
			self.log('[Badge] Completing explorer badge - Tumbleweed Valley')
			tasks = self.get_badge_tasks(10)
			if not tasks[0]:
				self.go_to_room('western.fort', False)
				self.wait_room_loaded()
				search_badge_item(next(filter(lambda x: x.iso_obj.get_uvz().x == 239, self.find_items_by_gui('western.kanonenkugeln'))).wob_id)
			if not tasks[1]:
				self.go_to_room('western.saloonzimmer1', False)
				self.wait_room_loaded()
				search_badge_item(self.find_item_by_gui('western.badezuber').wob_id)
			if not tasks[2]:
				self.go_to_room('western.backlands', False)
				self.wait_room_loaded()
				search_badge_item(self.find_item_by_gui('western.backlands_sitzstein1').wob_id)
		if not self.get_is_badge_completed(20):
			self.log('[Badge] Completing explorer badge - Schattenland')
			tasks = self.get_badge_tasks(20)
			if not tasks[0]:
				self.go_to_room('gothics.friedhof', False)
				self.wait_room_loaded()
				time.sleep(1.5)
				search_badge_item(next(filter(lambda x: x.has_interaction('SEARCH'), self.find_items_by_gui('gothics.friedhof_uferbank'))).wob_id)
			if not tasks[1]:
				self.go_to_room('gothics.gruft', False)
				self.wait_room_loaded()
				search_badge_item(next(filter(lambda x: x.has_interaction('SEARCH'), self.find_items_by_gui('hood.getraenkedoserot'))).wob_id)
			if not tasks[2]:
				self.go_to_room('gothics.kirche', False)
				self.wait_room_loaded()
				search_badge_item(self.find_item_by_gui('gothics.kirche_reliquienschrein').wob_id)
		search.cleanup()

		if not self.get_is_badge_completed(21):
			self.log('[Badge] Completing games badge')
			tasks = self.get_badge_tasks(21)
			if not tasks[0]:
				self.send_set_status(Status.PLAYING, 'astrovoids')
				self.send_delete_status(Status.PLAYING)
			if not tasks[1]:
				self.send_set_status(Status.PLAYING, 'jewels')
				self.send_delete_status(Status.PLAYING)
			if not tasks[2]:
				self.send_set_status(Status.PLAYING, 'puzzle')
				self.send_delete_status(Status.PLAYING)
			if not tasks[3]:
				self.send_set_status(Status.PLAYING, 'deserthunter')
				self.send_delete_status(Status.PLAYING)
			if not tasks[4]:
				self.send_set_status(Status.PLAYING, 'whackthehampster')
				self.send_delete_status(Status.PLAYING)
		
		if not self.get_is_badge_completed(31):
			self.log('[Badge] Completing sounds badge')
			tasks = self.get_badge_tasks(31)
			if not tasks[0]:
				self.go_to_room('hood.backalley', False)
				self.wait_room_loaded()
				self.send_user_command('miau')
			if not tasks[1]:
				self.go_to_room('western.saloon', False)
				self.wait_room_loaded()
				self.send_user_command('ruelps')
			if not tasks[2]:
				self.go_to_room('wutzlhofen.museum', False)
				self.wait_room_loaded()
				self.send_user_command('nies')
			if not tasks[3]:
				self.go_to_room('gothics.kirche', False)
				self.wait_room_loaded()
				self.send_user_command('gaehn')
			if not tasks[4]:
				self.go_to_home('plattenbau.eigenheim', False)
				self.wait_room_loaded()
				self.send_user_command('furz')

		if not self.__church_visited_today and not self.get_is_badge_completed(41) and get_local_datetime().weekday() == 6:
			self.log('[Badge] Completing church visitor badge')
			self.go_to_room('gothics.kirche', False)
			self.__church_visited_today = True
			self.wait_room_loaded()
			self.wait_random_delay(0.5, 3)	

	def daily_routine(self, skip_first_cycle = False, idle_room = 'plattenbau%2.eigenheim', idle_room_alt = 'plattenbau.plattenbau', 
		care_pets = False, care_pompom = False, complete_quests = False, complete_badges = False, maintain_amount = 25, overload_amount = 100, min_deliver_amount = 3, 
		loop_min_idle_sec = 60 * 60, loop_max_idle_sec = 2 * 60 * 60):
		self.log('Beginning daily routine...')

		if skip_first_cycle:
			self.__church_visited_today = True

		self.send_delete_status(Status.PRANKED)
		self.send_delete_status(Status.PLAYING)
		self.send_delete_status(Status.GHOST)
		self.send_delete_status(Status.SPOOK)
		self.send_delete_status(Status.WITCHBROOM)
		self.send_delete_status(Status.CLOAK)
		self.send_set_status(Status.NOSOUND)
		
		next_quick_strong = 0

		loop_min_idle_sec *= 1000
		loop_max_idle_sec *= 1000
		
		last_day = -1
		ant_amount = self.get_items_count(self.localeItems.LAZY_ANTS)
		
		total_ants_delivered = 0
		total_ants_collected = 0
		total_covered_wagon = 0
		total_construction_site = 0
		total_time_idle = 0
		start_time = time.time()
		
		last_delivery = -1

		self.__e_level_data.wait()
		start_level = self.level_data['level']
		
		while True:
			if next_quick_strong <= time.time():
				self.send_set_status(Status.QUICK_STRONG)
				next_quick_strong = time.time() + 604800
				self.log('Added strong speed effect.')

			if complete_quests:
				self.complete_quest()
			
			now_day = get_local_datetime().day
			day_change = now_day != last_day and (last_day != -1 or not skip_first_cycle) 
			
			empty_slots = FreggersBot.count_empty_slots(self.ajax_request_inventory())
			while empty_slots > 0:
				self.log('Filling {} empty slots with ants...'.format(empty_slots))
				ants_in_queue = self.filter_items(self.ajax_request_item_queue(), self.localeItems.LAZY_ANTS)
				missing_ants = empty_slots - len(ants_in_queue)
				for _ in range(min(empty_slots, len(ants_in_queue))):
					ant_in_queue = ants_in_queue.pop(0)
					self.ajax_inbox_action(ant_in_queue['id'], Freggers.INBOX_ACTION_ACCEPT)
					self.log('Filled empty slot with ant.')
				if missing_ants > 0:
					self.log('Not enough ants available to fill all empty slots. Collecting {} ants...'.format(missing_ants))
					self.collect_ants(max_amount = missing_ants)
				empty_slots = FreggersBot.count_empty_slots(self.ajax_request_inventory())
			
			if day_change:
				self.__church_visited_today = False
				if self.search_covered_wagon():
					total_covered_wagon += 1
				if self.search_noisy_construction_site():
					total_construction_site += 1
			
			self.__e_level_data.wait()
			level_up_expected = self.level_data['xp_total'] == self.level_data['xp_cap']
			ants_to_deliver = 20 if day_change else math.ceil((self.level_data['xp_cap'] - self.level_data['xp_current']) / 559)
			if not level_up_expected and ants_to_deliver < min_deliver_amount:
				self.log('Not enough ants to deliver ({} / {}). Waiting for a higher xp cap.'.format(ants_to_deliver, min_deliver_amount))
				ants_to_deliver = 0
				
			if ant_amount < ants_to_deliver:
				self.log('Collecting {} ants to deliver...'.format(ants_to_deliver - ant_amount))
				collected_ants = self.collect_ants(max_amount = ants_to_deliver - ant_amount)
				ant_amount += collected_ants
				total_ants_collected += collected_ants
				self.log('Collected {} ants.'.format(collected_ants))
			
			if ants_to_deliver > 0:
				if last_delivery != -1:
					self.log('Last delivery is {} ago.'.format(format_time(time.time() - last_delivery)))
				self.log('Delivering {} ants...'.format(ants_to_deliver))
				delivered_ants = self.deliver_ants(amount = ants_to_deliver)
				if delivered_ants == 0:
					level_up_expected = False
				ant_amount -= delivered_ants
				total_ants_delivered += delivered_ants
				last_delivery = time.time()
				self.log('Delivered {} ants.'.format(delivered_ants))
			
			if not level_up_expected:
			
				if ant_amount < maintain_amount:
					collect_amount = maintain_amount - ant_amount + overload_amount
					self.log('Collecting {} ants to maintain the minimum amount of ants...'.format(collect_amount))
					collected_ants = self.collect_ants(max_amount = collect_amount)
					ant_amount += collected_ants
					total_ants_collected += collected_ants                                            
					self.log('Collected {} ants.'.format(collected_ants))
				
				self.log('[Stats] Ants: current = {} | collected = {} | delivered = {}'.format(ant_amount, total_ants_collected, total_ants_delivered))
				self.log('[Stats] Construction site searches:', total_construction_site)
				self.log('[Stats] Covered wagon searches:', total_covered_wagon)
				self.log('[Stats] Level-ups:', (self.level_data['level'] - start_level))
				self.log('[Stats] Total time idling:', format_time(total_time_idle))
				self.log('[Stats] Total time running:', format_time(time.time() - start_time))
				
				if complete_badges:
					self.complete_badges()
				self.delete_trash_items()

				self.go_to_home(idle_room, True)
				
				if care_pets:
					self.care_pets(idle_room, True)
				
				if care_pompom:
					self.care_pompom(idle_room, True)
				
				self.daily_routine_on_idle()

				idle_time = random.randint(loop_min_idle_sec, loop_max_idle_sec) / 1000
				self.log('Idling for {}...'.format(format_time(idle_time)))
				time.sleep(idle_time)
				total_time_idle += idle_time
				
				self.go_to_room(idle_room_alt, False)
			
			last_day = now_day

	def daily_routine_on_idle(self):
		seats = list(filter(lambda item: item.get_primary_interaction() != None and item.get_primary_interaction().label == 'SIT_DOWN', self.wob_registry.iso_items))
		if len(seats) > 0:
			self.send_item_interaction(random.choice(seats).wob_id, 'SIT_DOWN')

	def print_items(self):
		for wob in self.wob_registry.iso_items:
			print(wob.wob_id, wob.gui, wob.name, wob.interactions, wob.get_properties())
	
	def wait_room_loaded(self):
		self.__e_room_loaded.wait()
