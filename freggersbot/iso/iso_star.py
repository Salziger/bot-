#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class IsoStar:
	
	@staticmethod
	def compute_direction(vector):
		dir = -1
		if vector.x != 0 or vector.y != 0:
			if vector.x == 0:
				if vector.y > 0:
					dir = 6
				elif vector.y < 0:
					dir = 2
			else:
				p = vector.y / vector.x
				if p < -2:
					dir = 2 if vector.x > 0 else 6
				elif p >= -2 and p < -0.5:
					dir = 1 if vector.x > 0 else 5
				elif p >= -0.5 and p < 0.5:
					dir = 0 if vector.x > 0 else 4
				elif p >= 0.5 and p < 2:
					dir = 7 if vector.x > 0 else 3
				elif p >= 2:
					dir = 6 if vector.x > 0 else 2
		return dir