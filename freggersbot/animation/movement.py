#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from ..data.vector import Vector3D

class Movement:
	
	def __init__(self, target, duration, ref, on_complete = None):
		self.segment_playtime = 0
		self.segment_index = -1
		self.total_playtime = 0
		self.target = target
		self.duration = duration
		self.ref = ref
		self.on_complete = on_complete if on_complete != None else lambda animation: None

	def get_target_pos(self):
		return self.segments[-1].points[-1]

	def set_segments(self, segments):
		if segments == None or len(segments) < 1:
			self.cleanup()
			return
		self.segments = segments
		self.segment_index = 0
	
	def update(self, time_delta):
		if self.segment_index < 0 or self.segment_index >= len(self.segments):
			return True
		self.segment_playtime += time_delta
		self.total_playtime += time_delta
		segment = self.segments[self.segment_index]
		if self.segment_playtime >= segment.duration:
			while self.segment_playtime >= segment.duration and self.segment_index < len(self.segments):
				self.segment_playtime -= segment.duration
				self.segment_index += 1
				if self.segment_index < len(self.segments):
					segment = self.segments[self.segment_index]
				else:
					segment = self.segments[-1]
					self.segment_playtime = segment.duration
		segment.compute(self.segment_playtime)
		direction = segment.direction
		if direction > -1 and self.target.get_direction() != direction:
			self.target.set_direction(direction)
		if self.target.get_uvz() != segment.position:
			self.target.set_positionv(segment.position)
	
	def is_finished(self):
		return self.segment_index >= len(self.segments)
	
	def cleanup(self):
		self.segment_playtime = 0
		self.total_playtime = 0
		self.duration = -1
		self.segment_index = -1
		self.target = None
		self.ref = None

class PathSegment:
	
	def __init__(self, points, duration, level):
		self.direction = -1
		self.position = Vector3D()
		self.points = points
		self.duration = duration
		self.level = level
	
	def compute(self, duration):
		pass
	
	def get_start(self):
		if self.points == None or len(self.points) == 0:
			return None
		return self.points[0]
	
	def get_end(self):
		if self.points == None or len(self.points) == 0:
			return None
		return self.points[-1]
	
	def __str__(self):
		return 'AMPathSegment[points=({}),ground={}]'.format(self.points, self.level != None)
	
	def __repr__(self):
		return self.__str__()

class MovementWayPoint:
	
	def __init__(self, u, v, z, millis):
		self.iso_u = u
		self.iso_v = v
		self.iso_z = z
		self.millis = millis
	
	def as_vector(self):
		return Vector3D(self.iso_u, self.iso_v, self.iso_z)
	
	def __str__(self):
		return 'MWP[isoU={},isoV={},isoZ={},millis={}]'.format(self.iso_u, self.iso_v, self.iso_z, self.millis)
	
	def __repr__(self):
		return self.__str__()
		
	@staticmethod
	def get_movement_waypoints(path):
		result = []
		for waypoint in path.waypoints:
			pos = waypoint.position
			result.append(MovementWayPoint(pos.u, pos.v, pos.z, waypoint.duration))
		return result