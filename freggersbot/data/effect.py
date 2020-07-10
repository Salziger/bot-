#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class EffectData:
	
	def __init__(self, utfmsg):
		self.gui = utfmsg.get_string_arg(0)
		array = utfmsg.get_int_list_arg(1)
		self.duration = array[0]
		self.update_interval = 30 if len(array) < 2 else array[1]
	
	@staticmethod
	def from_utfmsg(utfmsg):
		if utfmsg == None:
			return None
		return EffectData(utfmsg)