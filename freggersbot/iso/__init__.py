#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class IsoObject:
	
	def __init__(self, uvz):
		self.__uvz = uvz
		self.visible = True
		self.flag_args = {}
		
		self.__current_direction = -1
		self.type = 0
	
	def set_direction(self, direction):
		self.__current_direction = direction % 8
	
	def get_direction(self):
		return self.__current_direction
	
	def set_positionv(self, uvz):
		if uvz == None or self.__uvz == uvz:
			return
		self.__uvz.setv(uvz)
	
	def set_position(self, u, v, z):
		self.__uvz.set(u, v, z)
	
	def set_iso_u(self, u):
		self.__uvz.x = u
	
	def set_iso_v(self, v):
		self.__uvz.y = v
	
	def set_iso_z(self, z):
		self.__uvz.z = z
	
	def get_uvz(self):
		return self.__uvz.clone()

class Status:

	COMPOSING = 0
	IDLE = 1
	AWAY = 2
	SHRINK = 4
	SIT = 5
	NOSOUND = 6
	PLAYING = 7
	CARRYING = 8
	GHOST = 9
	CLOAK = 10
	SPOOK = 11
	MODEL = 12
	QUICK_LIGHT = 13
	QUICK_STRONG = 14
	WITCHBROOM = 15
	PRANKED = 16
	
	@staticmethod
	def get_object_status_data(utfmsg):
		if utfmsg == None:
			return None
		status_data = {}
		lim = utfmsg.get_arg_count() // 2
		for x in range(lim):
			stat_key = utfmsg.get_int_arg(x * 2)
			if stat_key == Status.AWAY:
				status_data[stat_key] = utfmsg.get_string_arg(x * 2 + 1)
			elif stat_key == Status.COMPOSING or stat_key == Status.IDLE:
				status_data[stat_key] = utfmsg.get_int_arg(x * 2 + 1)
			elif stat_key == Status.NOSOUND or stat_key == Status.PLAYING or stat_key == Status.SHRINK or stat_key == Status.SIT or stat_key == Status.GHOST or stat_key == Status.CLOAK or stat_key == Status.SPOOK or stat_key == Status.MODEL or stat_key == Status.QUICK_LIGHT or stat_key == Status.QUICK_STRONG or stat_key == Status.PRANKED:
				status_data[stat_key] = 1
			elif stat_key == Status.CARRYING:
				msg = utfmsg.get_message_arg(x * 2 + 1)
				if msg == None:
					status_data[stat_key] = None
				else:
					carry_obj = status_data[stat_key] = {}
					carry_obj["wobid"] = msg.get_int_arg(0)
					carry_obj["gui"] = msg.get_string_arg(1)
		return status_data