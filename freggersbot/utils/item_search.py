#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import threading
from freggersbot.freggers import Event

class ItemSearch:
	
	def __init__(self, freggers, wob_id):
		self.wob_id = wob_id
		self.__event = threading.Event()
		self.__freggers = freggers
		freggers.register_callback(Event.NOTIFY_CREATE_ITEM, self.__cb_success)
		freggers.register_callback(Event.SHOW_ACTION_FEEDBACK, self.__cb_failure)
	
	def search(self):
		self.__success = False
		self.__event.clear()
		self.__freggers.send_item_interaction(self.wob_id, 'SEARCH')
		self.__event.wait()
		return self.__success
	
	def search_once(self):
		success = self.search()
		self.cleanup()
		return success
	
	def cleanup(self):
		self.__freggers.unregister_callback(Event.NOTIFY_CREATE_ITEM, self.__cb_success)
		self.__freggers.unregister_callback(Event.SHOW_ACTION_FEEDBACK, self.__cb_failure)
	
	def __cb_success(self, data):
		self.__success = True
		self.__event.set()
	
	def __cb_failure(self, data):
		self.__success = False
		self.__event.set()