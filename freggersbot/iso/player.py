#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from ..iso.container import IsoObjectContainer

class Player(IsoObjectContainer):
	
	def __init__(self, user_id, wob_id):
		super(Player, self).__init__(wob_id)
		self.user_id = user_id
	
	@staticmethod
	def create_from_data(avatar_data):
		if avatar_data.username == None or avatar_data.user_id <= 0:
			return None
		player = Player(avatar_data.user_id, avatar_data.wob_id)
		player.name = avatar_data.username
		player.rights = avatar_data.rights
		status = avatar_data.status
		if status != None:
			for x in range(len(status)):
				if status.get(x) != None:
					player.set_state(x, True, status[x])
		return player