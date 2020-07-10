#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import requests
import pyamf

from pyamf import remoting
from pyamf.remoting import STATUS_OK, STATUS_ERROR, STATUS_DEBUG

class AmfAPI:

	SEND_STATS = 'LiveStats.log'
	GET_RENDER_PARTS = 'Core.get_renderparts'
	GET_DAILY_OFFER = 'Core.get_today_offered_items'
	GET_STICKY_COUNT = 'Core.get_stickycount'
	LOG = 'Core.log'
	HANDLE_GAME_ENDED = 'Games.stage_ended'
	GET_PRIMARY_ROOM_LABEL = 'Core.get_primary_room_label'
	
	def __init__(self, url, session = requests.Session()):
		self.__url = url
		self._session = session
	
	def call(self, cmd, callback = None, error_callback = None, args = []):
		req = remoting.Request(target = cmd, body = args)
		env = remoting.Envelope(pyamf.AMF0)
		env['/0'] = req
		req_data = remoting.encode(env).getvalue()
		resp = self._session.post(self.__url, 
								   data = req_data, 
								   headers = {'Content-Type': 'application/x-amf'})
		if resp.status_code == 200:
			resp_msg = remoting.decode(resp.content)['/0']
			resp_status = resp_msg.status
			if resp_status == STATUS_OK:
				if callback != None:
					callback(resp_msg.body)
				return (resp_status, resp_msg.body)
			elif resp_status == STATUS_ERROR:
				if error_callback != None:
					error_callback(resp_msg.body)
				return (resp_status, resp_msg.body)
			elif resp_status == STATUS_DEBUG:
				print('Amf DEBUG response:')
				print(resp_msg.body)
				return (resp_status, resp_msg.body)
		return (-1, None)