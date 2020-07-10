#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from .effect import EffectData
from .position import Position
from .path import Path
from .animation import AnimationData
from freggersbot.net.utf_message import UtfMessage

class ActionThrow:
	
	def __init__(self, utfmsg):
		self.gui = utfmsg.get_string_arg(1)
		if utfmsg.get_arg_type(2) == UtfMessage.TYPE_RECORD:
			self.source = utfmsg.get_message_arg(2).get_int_list_arg(0)
		else:
			self.source = utfmsg.get_int_arg(2)
		if utfmsg.get_arg_type(3) == UtfMessage.TYPE_RECORD:
			self.target = utfmsg.get_message_arg(3).get_int_list_arg(0)
		else:
			self.target = utfmsg.get_int_arg(3)
		array = utfmsg.get_int_list_arg(4)
		self.height = array[0]
		self.duration = array[1]
		if utfmsg.get_arg_type(5) == UtfMessage.TYPE_RECORD:
			self.ghost_trail = None #GhosttrailData.fromUtfMessage(param1.get_message_arg(5) as UtfMessage);
		if utfmsg.get_arg_type(6) == UtfMessage.TYPE_RECORD:
			self.end_effect_data = EffectData.from_utfmsg(utfmsg.get_message_arg(6))

class ActionUpdateWob:
	
	def __init__(self, utfmsg):
		self.wob_id = utfmsg.get_int_arg(1)
		if utfmsg.get_arg_type(2) == UtfMessage.TYPE_INT:
			self.position = Position.from_array(utfmsg.get_int_list_arg(2))
		else:
			self.path = Path.from_utfmsg(utfmsg.get_message_arg(2))
		self.animation = AnimationData.from_utfmsg(utfmsg.get_message_arg(3))
		self.sound = None #SoundBlock.fromUtfMessage(param1.get_message_arg(4) as UtfMessage);
		self.lightmap = None #LightmapData.fromUtfMessage(param1.get_message_arg(5) as UtfMessage);
		self.effect = EffectData.from_utfmsg(utfmsg.get_message_arg(6))
		if utfmsg.get_arg_type(7) == UtfMessage.TYPE_INT:
			if utfmsg.get_int_arg(7) == 0:
				self.ghost_trail = None
		elif utfmsg.get_arg_type(7) == UtfMessage.TYPE_RECORD:
			self.ghost_trail = None #GhosttrailData.fromUtfMessage(param1.get_message_arg(7) as UtfMessage);