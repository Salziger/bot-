#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from .container_decoder import MediaContainerDecoder

class ResourceManager:
	
	PARAM_ROOM_BASE_URL = 'roombaseurl'
	PARAM_PORTABLE_BASE_URL = 'portablebaseurl'
	PARAM_NPC_BASE_URL = 'npcbaseurl'
	PARAM_ITEM_BASE_URL = 'itembaseurl'
	PARAM_SOUND_BASE_URL = 'soundbaseurl'
	PARAM_MED_BASE_URL = 'medbaseurl'
	PARAM_OVERLAY_BASE_URL = 'overlaybaseurl'
	PARAM_IMG_FACTORY = 'imgfactory'
	RELEASE_IMMEDIATELY = 0
	RELEASE_WHEN_EXPIRED = 1
	RELEASE_NEVER = 2
	RELEASE_ON_LEVEL_LOAD = 3
	PACK_TYPE_MEDIAPACK = 'MED'
	PACK_TYPE_ISOPACK = 'ISO'
	__LOAD_SUCCESS = 'success'
	__LOAD_FAILED = 'failure'
	
	verbose_mode = False
	
	def __init__(self):
		self.__inited = False
		self.__cache_buster = ''
		self.__image_buster = ''
		self.__last_res_id = 0
		self.__last_req_id = 0
		self.__max_res_age = 0
		self.__total_decoded = 0
		self.__failed_decoding = 0
		self.__failed_loading = 0
		
		self.__level_cache = LRUCache(32)
		self.__background_cache = LRUCache(32)
		self.__resource_data = []
		self.__resource_ids = []
		self.__resource_names = []
		self.__processing_objects = {}
		self.__data_pack_lookup = {}
		
	def configure(self, cfg):
		if 'v' in cfg:
			self.__cache_buster = '?v=' + cfg["v"]
		if 'imgv' in cfg:
			self.__image_buster = '?v=' + cfg["imgv"]
		self.__config = cfg
		self.__inited = True
	
	def request_level(self, freggers, level, err_callback = None, keep_cache = False, use_cache = False):
		if not self.__inited or ResourceManager.PARAM_ROOM_BASE_URL not in self.__config:
			print('[i] [ResourceManager] Not initialized or invalid config.')
			return False
		if use_cache:
			lvl = self.__level_cache.get(level.identifier)
			if lvl != None:
				level.set(lvl)
				#level._load_complete(lvl.clone())
				return True
		if not keep_cache:
			for x in range(len(self.__resource_data)):
				resource = self.__resource_data[x]
				if resource.cache_mode == ResourceManager.RELEASE_ON_LEVEL_LOAD:
					self.__remove_resource(x)
		resp = freggers._session.get(freggers.localeItems.URL + self.__config[ResourceManager.PARAM_ROOM_BASE_URL] + '/' + level.area_name + '/' + level.room_name + '/' + level.room_name + '.bin' + self.__image_buster)
		if resp.status_code == 200:
			media_container_dec = MediaContainerDecoder()
			media_container = media_container_dec.decode_data_bytes(resp.content)
			level.decode(media_container)
			self.__level_cache.put(level.identifier, level.clone())
			print('[i] [ResourceManager] Successfully loaded level {}.'.format(level.identifier))
			return True
		else:
			print('[e] [ResourceManager] Invalid response received while loading level:', resp.status_code)
		return False
		
	def __remove_resource(self, index):
		if index < 0:
			return
		del self.__resource_ids[index]
		resource_data = self.__resource_data.pop(index)
		del self.__resource_names[index]
		#if resource_data != None:
		#	if data.resource is ADataPack do unregisterDataPack(data.resource)
		#		pass

class LRUCache:
	
	def __init__(self, max_size):
		self.__cache = {}
		self.__max_size = max_size
		self.__current_size = 0
		self.__head = None
		self.__tail = None
	
	def put(self, k, v):
		e = LRUCache.LRUEntry(k, v)
		if k not in self.__cache:
			self.__current_size += 1
		self.__cache[k] = e
		self.__set_most_recently_used(e)
		if self.__tail == None:
			self.__tail = e
		if self.__current_size > self.__max_size:
			self.__purge_lru_elements()
	
	def get(self, k):
		e = self.__cache.get(k)
		if e != None:
			self.__set_most_recently_used(e)
			return e.v
		return None
	
	def remove(self, k):
		e = self.__cache.pop(k, None)
		if e != None:
			if e == self.__head:
				self.__head = e.next
			if e == self.__tail:
				self.__tail = e.prev
			if e.prev != None:
				e.prev.next = e.next
			if e.next != None:
				e.next.prev = e.prev
		self.__current_size -= 1
		
	def __set_most_recently_used(self, e):
		if e == self.__head:
			return
		if e.prev != None:
			e.prev.next = e.next
			if e == self.__tail:
				self.__tail = e.prev
				self.__tail.next = None
		if e.next != None:
			e.next.prev = e.prev
		e.next = self.__head
		e.prev = None
		if self.__head != None:
			self.__head.prev = e
		self.__head = e
	
	def __purge_lru_elements(self):
		while self.__current_size > self.__max_size:
			self.remove(self.__tail.k)
		
	class LRUEntry:
		
		def __init__(self, k, v):
			self.k = k
			self.v = v
			self.prev = None
			self.next = None

RESOURCE_MANAGER = ResourceManager()