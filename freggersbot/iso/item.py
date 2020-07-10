#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from ..data.item_interaction import ItemInteraction
from .container import IsoObjectContainer

class IsoItem(IsoObjectContainer):
	
	def __init__(self, wob_id, item_properties):
		super(IsoItem, self).__init__(wob_id)
		if item_properties != None:
			self.iso_obj.type = item_properties.type
			self.interactive = item_properties.selectable
	
	@staticmethod
	def create_from_data(item_data):
		if item_data == None or item_data.wob_id == None or item_data.gui == None:
			return None
		iso_item = IsoItem(item_data.wob_id, item_data.properties)
		iso_item.gui = item_data.gui
		iso_item.name = item_data.name
		if item_data.interactions.get_data() != None:
			IsoItem.create_interaction_menu(iso_item, item_data.interactions, item_data.primary_interaction_label)
		return iso_item
	
	@staticmethod
	def create_interaction_menu(iso_item, interaction_data, primary_interaction_label):
		iso_item.interactions = ItemInteraction.create_interactions_from_data_list(interaction_data.get_data(), primary_interaction_label)
	
	@staticmethod
	def create_from_map_data(data):
		if data == None or 'wobid' not in data or 'gui' not in data:
			return None
		iso_item = IsoItem(data['wobid'], data['props'])
		iso_item.gui = data['gui']
		iso_item.name = data['name']
		if 'interactions' in data:
			iso_item.interactions = ItemInteraction.create_interactions_from_data_list(data['interactions'], data.primary_interaction_label)
		return iso_item