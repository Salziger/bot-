#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class CtxtServer:
	
	def __init__(self, utfmsg):
		self.port = utfmsg.get_int_arg(1)
		self.host = CtxtServer.get_host(utfmsg.get_int_list_arg(1)[1:])
	
	@staticmethod
	def get_host(arr):
		arr_len = len(arr)
		if arr == None or arr_len != 4 and arr_len != 8:
			return
		if arr_len == 4:
			s = ''
			for i in arr:
				s += str(i) + '.'
			return s[:len(s) - 1]
		s = ''
		for i in arr:
			s += hex(i).replace('0x','') + ':'
		return s[:len(s) - 1]