#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import time

def time_ms():
	return int(round(time.time() * 1000))

def format_time(time):
	seconds = int(time)
	if seconds > 0:
		s = str(seconds % 60) + 'sec'
		minutes = seconds // 60
		if minutes > 0:
			s = str(minutes % 60) + 'min ' + s
			hours = minutes // 60
			if hours > 0:
				s = str(hours % 24) + 'h ' + s
				days = hours // 24
				if days > 0:
					s = str(days) + 'd ' + s
		return s
	else:
		return '0sec'