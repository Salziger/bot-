#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from .point2point_movement import Point2PointMovement

class AnimationManager:
	
	def __init__(self):
		self.running = False
		self.animations = {}
		self.last_update = 0
		self.ignore_animations = False
		self.on_complete = lambda animation: None

	def start(self, time):
		self.last_update = time
		self.running = True
	
	def stop(self):
		self.running = False
		self.last_update = 0
		self.animations.clear()

	def moveground(self, target, points, duration, age, level, ref):
		if not self.running:
			return
		if self.ignore_animations:
			self.animations.clear()
			return
		animation = Point2PointMovement(target, points, duration, level, ref)
		animation.update(age)
		self.animations[target] = animation
		return animation
	
	def update(self, time):
		if not self.running:
			return
		if self.ignore_animations:
			self.animations.clear()
			return
		elapsed = time - self.last_update
		for target in reversed(list(self.animations.keys())):
			animation = self.animations[target]
			animation.update(elapsed)
			if animation.is_finished():
				del self.animations[target]
				self.on_complete(animation)
				animation.on_complete(animation)
				animation.cleanup()
		self.last_update = time
	
	def has_animation(self, target):
		return target in self.animations
	
	def get_animation(self, target):
		return self.animations[target]
		
	def clear_animation(self, target):
		if target in self.animations:
			del self.animations[target]
			return True
		return False