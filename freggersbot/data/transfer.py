#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from .avatar import AvatarData

class TrRoomJoin:
	
	def __init__(self, utfmsg):
		self.data = AvatarData(utfmsg, start_index = 1)

class TrRoomLeave:
	
	def __init__(self, utfmsg):
		array = utfmsg.get_int_list_arg(1)
		self.wob_id = array[0]
		self.user_id = array[1]

class TrRoomReject:

	def __init__(self, utfmsg):
		self.reason = utfmsg.get_int_arg(1)