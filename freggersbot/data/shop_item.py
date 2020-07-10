#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class ShopItem:
	
	def __init__(self, label, name, description, iconUrl, price, base_price, room_label, shop_name):
		self.label = label
		self.name = name
		self.description = description
		self.iconUrl = iconUrl
		self.price = price
		self.base_price = base_price
		self.room_label = room_label
		self.shop_name = shop_name
	
	@staticmethod
	def from_data(data):
		items = []
		for label in data.keys():
			entry = data.get(label)
			items.append(ShopItem(label, entry['name'], entry['description'], entry['icon_url'], 
				entry['price'], entry['base_price'], entry['room_label'], entry['shop_name']))
		return items