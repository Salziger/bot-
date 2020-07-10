#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from ..iso import Status
from ..net.utf_message import UtfMessage
from .position import Position
from .path import Path
from .animation import AnimationData
from .effect import EffectData

class AvatarData:
	
	def __init__(self, utfmsg, start_index = 0):
		self.username = utfmsg.get_string_arg(0 + start_index)
		array = utfmsg.get_int_list_arg(1 + start_index)
		self.wob_id = array[0]
		self.user_id = array[1]
		self.gender = array[2]
		self.rights = array[3]
		self.status = Status.get_object_status_data(utfmsg.get_message_arg(2 + start_index))
		if utfmsg.get_arg_type(3 + start_index) == UtfMessage.TYPE_INT:
			self.position = Position.from_array(utfmsg.get_int_list_arg(3 + start_index))
		else:
			self.path = Path.from_utfmsg(utfmsg.get_message_arg(3 + start_index))
		self.animation = AnimationData.from_utfmsg(utfmsg.get_message_arg(4 + start_index))
		self.sound = None #SoundBlock.fromUtfMessage(param1.get_message_arg(5 + param2) as UtfMessage);
		self.lightmap = None #LightmapData.fromUtfMessage(param1.get_message_arg(6 + param2) as UtfMessage);
		self.effect = EffectData.from_utfmsg(utfmsg.get_message_arg(7 + start_index))
		self.ghost_trail = None #GhosttrailData.fromUtfMessage(param1.get_message_arg(8 + param2) as UtfMessage);