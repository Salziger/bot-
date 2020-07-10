#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from .list_cmd import ListCmd
from .item import ItemData
from .avatar import AvatarData

class EnvItem(ListCmd):
	
	START_LIST = 1
	
	def __init__(self):
		self.__item_list = []
		self.__complete = False
		self.add = False
	
	def feed(self, utfmsg):
		meta = utfmsg.get_int_list_arg(0)
		self.add = meta[3] == 0
		flag = meta[2]
		if (flag & 1) != 0:
			self.__item_list = []
		index = EnvItem.START_LIST
		while index < utfmsg.get_arg_count():
			m = utfmsg.get_message_arg(index)
			if m != None:
				self.__item_list.append(ItemData(m))
			index += 1
		self.__complete = (flag & 2) != 0
	
	def is_complete(self):
		return self.__complete
	
	def get_data(self):
		return self.__item_list

class EnvUser(ListCmd):
	
	START_LIST = 2
	
	def __init__(self):
		self.__avatar_list = []
		self.__complete = False
	
	def feed(self, utfmsg):
		meta = utfmsg.get_int_list_arg(0)[2]
		if meta & 1 != 0:
			self.__avatar_list = []
		for index in range(EnvUser.START_LIST, utfmsg.get_arg_count(), 1):
			msg = utfmsg.get_message_arg(index)
			self.__avatar_list.append(AvatarData(msg))
		self.__complete = meta & 2 != 0
	
	def is_complete(self):
		return self.__complete
	
	def get_data(self):
		return self.__avatar_list

class EnvMisc:
	
	def __init__(self, utfmsg):
		self.sounds = None #SoundBlock.listFromUtfMessage(param1.get_message_arg(1) as UtfMessage);