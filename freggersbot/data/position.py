#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class Position:
	
	def __init__(self, u, v, z, direction = 0):
		self.u = u
		self.v = v
		self.z = z
		self.direction = direction
	
	@staticmethod
	def from_array(array):
		if array == None:
			return None
		return Position(array[0], array[1], array[2], direction = array[3])
	
	def __str__(self):
		return 'Position({}, {}, {}, {})'.format(self.u, self.v, self.z, self.direction)