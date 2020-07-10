#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class InteractionData:
	
	def __init__(self, utfmsg):
		self.__data = None
		if utfmsg == None:
			return
		arg_len = utfmsg.get_arg_count()
		if arg_len == 0:
			return
		data = []
		for i in range(arg_len):
			msg = utfmsg.get_message_arg(i)
			data.append({
				'label': msg.get_string_arg(0),
				'name': msg.get_string_arg(1),
				'produces': msg.get_string_arg(2)
			})
		if len(data) == 0:
			return
		self.__data = data
	
	def get_data(self):
		return self.__data