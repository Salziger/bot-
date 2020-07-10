#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class CtxtRoom:
	
	def __init__(self, utfmsg):
		self.room_context_label = utfmsg.get_string_arg(1)
		self.room_gui = utfmsg.get_string_arg(2)
		self.desc = utfmsg.get_string_arg(3)
		self.sounds = utfmsg.get_message_arg(4) #SoundBlock.listFromUtfMessage( utfmsg )
		m = utfmsg.get_int_list_arg(5)
		self.brightness = m[0]
		self.wob_id = m[1]
		self.topic = utfmsg.get_string_arg(6)
		self.show_animmation = utfmsg.get_boolean_arg(7)
		self.user_owns_room = utfmsg.get_boolean_arg(8)
		if utfmsg.get_arg_count() > 10:
			self.owner_user_id = utfmsg.get_int_arg(9)
			self.owner_user_name = utfmsg.get_string_arg(10)
		else:
			self.owner_user_id = 0
			self.owner_user_name = None
			
	def gui(self):
		return self.room_gui.split('.',1)[1]