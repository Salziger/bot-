#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from freggersbot.utils.bytebuffer import ByteBuffer

class MediaContainerDecoder:
	
	TYPE_BITMAP = 0
	TYPE_RAWBYTES = 1
	TYPE_STRING = 2
	TYPE_INT = 3
	TYPE_BYTE = 4
	TYPE_ISOCOMP = 5
	TYPE_ARGB32 = 6
	TYPE_ROOMCOMP = 7
	TYPE_MP3 = 8
	TYPE_NULL = 99
	
	def __init__(self):
		self.__content = None
		self.__on_complete = None
		self.__count = 0
		self.__done = 0
	
	@staticmethod
	def swf_create_sound(data):
		pass
		
	@staticmethod
	def __extract_bitmap(data):
		pass
		
	@staticmethod
	def __load_iso_comp(data):
		pass
	
	def __set_content_at(self, index, elem):
		self.__content[index][1] = elem
		self.__done += 1
	
	def decode_data_bytes(self, data):
		data = ByteBuffer(data = data)
		data.uncompress()
		count = self.__count = data.read_unsigned_int()
		self.__content = []
		ba = None
		for index in range(count):
			type = data.read_unsigned_byte()
			size = data.read_unsigned_int()
			
			if size == 0:
				type = MediaContainerDecoder.TYPE_NULL
			else:
				next_pos = data.position + size
				ba = ByteBuffer()
				ba.write_byte_buffer(data, data.position, size)
				ba.position = 0
				data.position = next_pos
			self.__content.append([type, None])
			
			if type == MediaContainerDecoder.TYPE_ARGB32 or type == MediaContainerDecoder.TYPE_RAWBYTES:
				self.__content[index][1] = ba
				self.__done += 1
			elif type == MediaContainerDecoder.TYPE_STRING:
				self.__content[index][1] = ba.to_string()
				self.__done += 1
			elif type == MediaContainerDecoder.TYPE_INT:
				self.__content[index][1] = ba.read_int()
				self.__done += 1
			elif type == MediaContainerDecoder.TYPE_BYTE:
				self.__content[index][1] = ba.read_unsigned_byte()
				self.__done += 1
			elif type == MediaContainerDecoder.TYPE_MP3:
				self.__set_content_at(index, MediaContainerDecoder.swf_create_sound(ba))
			elif type == MediaContainerDecoder.TYPE_BITMAP:
				self.__set_content_at(index, MediaContainerDecoder.__extract_bitmap(ba))
			elif type == MediaContainerDecoder.TYPE_ROOMCOMP or type == MediaContainerDecoder.TYPE_ISOCOMP:
				self.__set_content_at(index, MediaContainerDecoder.__load_iso_comp(ba))
			else:
				self.__done += 1
		
		if self.__done >= self.__count:
			return self.__content
		return None