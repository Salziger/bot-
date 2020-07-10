#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class ItemInteraction:
	
	TYPE_PRIMARY = 1
	TYPE_SECONDARY = 2
	KEY_LABEL = 'label'
	KEY_NAME = 'name'
	KEY_PRODUCES = 'produces'
	
	def __init__(self, label, name, type = TYPE_PRIMARY, produces = None):
		self.label = label
		self.name = name
		self.type = type
		self.produces = produces
		
	@staticmethod
	def create_from_data(data, primary_interaction_label):
		if data == None or ItemInteraction.KEY_LABEL not in data or ItemInteraction.KEY_NAME not in data:
			return None
		label = data[ItemInteraction.KEY_LABEL]
		type = ItemInteraction.TYPE_PRIMARY if label == primary_interaction_label else ItemInteraction.TYPE_SECONDARY
		return ItemInteraction(label, data[ItemInteraction.KEY_NAME], type, None if ItemInteraction.KEY_PRODUCES not in data else data[ItemInteraction.KEY_PRODUCES])
	
	@staticmethod
	def create_interactions_from_data_list(data_list, primary_interaction_label):
		if data_list == None:
			return None
		data_len = len(data_list)
		interactions = [None] * data_len
		for x in range(data_len):
			interaction = ItemInteraction.create_from_data(data_list[x], primary_interaction_label)
			if interaction != None:
				interaction.cb = lambda client, provider, interaction, params = None: client.send_item_interaction(provider.wob_id,interaction.label,params)
				interactions[x] = interaction
		return interactions
		
	def __str__(self):
		return 'ItemInteraction[label={}, name={}]'.format(self.label, self.name)
	
	def __repr__(self):
		return self.__str__()