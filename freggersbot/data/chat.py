#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class ChatUsr:
	
	def __init__(self, utfmsg):
		self.wob_id = utfmsg.get_int_arg(1)
		self.message = utfmsg.get_string_arg(2)
		self.type = utfmsg.get_int_list_arg(0)[2]
		self.mode = 0 if utfmsg.get_arg_count() <= 3 else utfmsg.get_int_arg(3)
		self.overheard = False if utfmsg.get_arg_count() <= 4 else utfmsg.get_boolean_arg(4)

class ChatSrv:
	
	def __init__(self, utfmsg):
		self.message = utfmsg.get_string_arg(1)