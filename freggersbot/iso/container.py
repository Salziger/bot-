#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from . import IsoObject
from ..data.vector import Vector3D
from ..data.item_interaction import ItemInteraction

class IsoObjectContainer:
	
	ICONSCALE = 0.5
	GHOST_ALPHA = 0.5
	
	def __init__(self, wob_id):
		self.__properties = {}
		self.wob_id = wob_id
		self.iso_obj = IsoObject(Vector3D())
		self.state_values = {}
		self.set_states = {}
		self.interactions = []
		
		self.on_screen = False
		self.last_request = None
		self.num_stickies = 0
		self.interactive = True
		
		self.properties_cb = lambda x, y, z: None
		
	def set_state(self, state_id, enabled, value):
		self.set_states[state_id] = enabled
		self.state_values[state_id] = value if enabled else None
		self.apply_states()
	
	def clear_states(self):
		for state_id in self.state_values.keys():
			self.state_values[state_id] = None
			self.set_states[state_id] = False
			self.apply_state(state_id)
	
	def apply_state(self, state_id):
		pass
	
	def apply_states(self):
		pass
	
	def is_state_set(self, state_id):
		if state_id in self.set_states:
			return self.set_states[state_id]
		return False
	
	def get_state(self, state_id):
		if state_id in self.state_values:
			return self.state_values[state_id]
		return None
	
	def get_properties(self):
		if self.__properties == None:
			return None
		return self.__properties.copy()
	
	def set_properties(self, properties):
		old = self.__properties
		self.__properties = [] if properties == None else properties.copy()
		if self.properties_cb != None:
			self.properties_cb(self, self.__properties.copy(), old)
	
	def get_interaction(self, name):
		if self.interactions == None:
			return None
		for x in range(len(self.interactions)):
			if self.interactions[x].label == name:
				return self.interactions[x]
		return None
	
	def get_interaction_at(self, index):
		if self.interactions == None or index < 0 or index >= len(self.interactions):
			return None
		return self.interactions[index]
	
	def add_interaction(self, label, name):
		if self.interactions == None:
			self.interactions = []
		for interaction in self.interactions:
			if interaction.label == label:
				interaction.name = name
				return
		self.interactions.append(ItemInteraction(label, name)) #TODO: ItemInteraction(label,name)
	
	def remove_interaction(self, label):
		if self.interactions == None:
			return
		at = -1
		for x in range(len(self.interactions)):
			if self.interactions[x].label == label:
				at = x
				break
		if at != -1:
			del self.interactions[at]
		if len(self.interactions) == 0:
			self.interactions = None
	
	def remove_interactions(self):
		self.interactions.clear()
		self.interactions = None
	
	def has_interaction(self, label):
		if self.interactions == None:
			return False
		for interaction in self.interactions:
			if interaction.label == label:
				return True
		return False
	
	def get_primary_interaction(self):
		for interaction in self.interactions:
			if interaction.type == ItemInteraction.TYPE_PRIMARY:
				return interaction
		return None
	
	def get_first_secondary_interaction(self):
		for interaction in self.interactions:
			if interaction.type == ItemInteraction.TYPE_SECONDARY:
				return interaction
		return None
	
	def has_interactions(self, type = ItemInteraction.TYPE_PRIMARY | ItemInteraction.TYPE_SECONDARY):
		for interaction in self.interactions:
			if interaction.type & type != 0:
				return True
		return False
	
	def is_throw_target(self):
		return True
	
	def is_trash(self):
		return False