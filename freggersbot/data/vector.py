#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import math

class Vector3D:
	
	def __init__(self, x = 0, y = 0, z = 0):
		self.x = x
		self.y = y
		self.z = z
		
	def __eq__(self, obj):
		return isinstance(obj, Vector3D) and obj.x == self.x and obj.y == self.y and obj.z == self.z
	
	def __str__(self):
		return 'Vector3D[x={}, y={}, z={}]'.format(self.x, self.y, self.z)
	
	def setv(self, vector):
		self.x = vector.x
		self.y = vector.y
		self.z = vector.z
	
	def set(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def subtract(self, vector):
		return Vector3D(self.x - vector.x, self.y - vector.y, self.z - vector.z)
	
	def distance_to(self, x, y, z):
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2 + (z - self.z) ** 2)
	
	def distance(self, vector):
		return self.distance_to(vector.x, vector.y, vector.z)
	
	def rounded(self):
		return Vector3D(round(self.x), round(self.y), round(self.z))

	def as_array(self):
		return [self.x, self.y, self.z]
	
	def as_tuple(self):
		return (self.x, self.y, self.z)
	
	def clone(self):
		return Vector3D(self.x, self.y, self.z)