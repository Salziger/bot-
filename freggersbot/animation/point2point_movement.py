#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from .movement import Movement, PathSegment
from ..iso.iso_star import IsoStar

class Point2PointMovement(Movement):
	
	def __init__(self, target, points, duration, level, ref):
		super(Point2PointMovement, self).__init__(target, duration, ref, None)
		
		if points == None:
			self.cleanup()
			return
		
		index = 0
		while index < len(points):
			if points[index].millis == 0:
				del points[index]
			else: #original code without else (index increased on every iteration)
				index += 1
		
		len_points = len(points)
		
		if len_points == 0:
			self.cleanup()
			return
		
		src_vector = self.target.get_uvz()
		target_vector = points[0].as_vector()
		segments = [LinearPathSegment([src_vector, target_vector], points[0].millis, level)]
		
		index = 0
		while index < len_points - 1:
			wp = points[index]
			if wp != None:
				src_vector = wp.as_vector()
				wp = points[index + 1]
				if wp != None:
					target_vector = wp.as_vector()
					duration = wp.millis
					if src_vector != None and target_vector != None:
						segments.append(LinearPathSegment([src_vector, target_vector], duration, level))
			index += 1
		self.set_segments(segments)
		
class LinearPathSegment(PathSegment):
	
	def __init__(self, points, duration, level):
		super(LinearPathSegment, self).__init__(points, duration, level)
		self.delta = points[1].subtract(points[0])
		self.direction = IsoStar.compute_direction(self.delta)
	
	def compute(self, duration):
		c = duration / self.duration
		start = self.points[0]
		self.position.x = start.x + c * self.delta.x
		self.position.y = start.y + c * self.delta.y
		self.position.z = start.z + c * self.delta.z
		if self.level != None:
			self.position.z = self.level.get_height_at(self.position.x, self.position.y)
	
	def __str__(self):
		return 'AMLinearPathSegment[points=({}),ground={}]'.format(self.points, self.level != None)