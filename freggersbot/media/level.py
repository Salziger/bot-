#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from .decoder import Decoder

class Level:
	
	HEIGHT_OFFSET = 12
	HEIGHT_MAX = 4095
	
	def __init__(self, area_name, room_name):
		self.area_name = area_name
		self.room_name = room_name
		self.identifier = area_name + '.' + room_name
		
	def init(self, u, v, tilebase):
		self.bounds = (0, 0, u, v)
		self.base = tilebase
		self.version = 1
		self.map = [0] * (u * v)
		self.max_z = 0
	
	def set(self, level):
		self.bounds = level.bounds
		self.base = level.base
		self.version = level.version
		self.map = level.map
		self.max_z = level.max_z
		self.masks = level.masks
		self.collision_map = level.collision_map
		self.sound_data = level.sound_data
		self.room_components = level.room_components
	
	def decode(self, container):
		data = Decoder.decode_level(container)
		self.init_from_decoded_data(data)
		return True
	
	def init_from_decoded_data(self, data):
		if data == None:
			return False
		self.map = data[Decoder.LVL_MAP]
		self.masks = data[Decoder.LVL_MASKS]
		self.version = data[Decoder.VERSION_NUMBER]
		self.bounds = (0, 0, data[Decoder.LVL_UNITS_U], data[Decoder.LVL_UNITS_V])
		self.max_z = data[Decoder.LVL_UNITS_Z]
		self.base = data[Decoder.TILEBASE]
		self.collision_map = data[Decoder.LVL_COLLISIONMAP]
		self.sound_data = data[Decoder.SOUNDS]
		self.room_components = data[Decoder.LVL_SWFOBJECTS]
		return True
		
	def get_height_at(self, x, y):
		if x >= self.bounds[2] or y >= self.bounds[3]:
			return -1
		pos = int(y * self.bounds[2] + x)
		if pos < 0 or pos >= len(self.map):
			return -1
		return self.map[pos] >> Level.HEIGHT_OFFSET & Level.HEIGHT_MAX
	
	def clone(self):
		lvl = Level(self.area_name, self.room_name)
		lvl.map = self.map
		lvl.masks = self.masks
		lvl.version = self.version
		lvl.bounds = self.bounds
		lvl.max_z = self.max_z
		lvl.base = self.base
		lvl.collision_map = self.collision_map
		lvl.sound_data = self.sound_data
		lvl.room_components = self.room_components
		return lvl