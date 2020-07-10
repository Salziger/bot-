#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import struct
import zlib

class ByteBuffer:
	
	def __init__(self, data = None, byteorder = 'big'):
		self.byteorder = byteorder
		self.position = 0
		self.__data = data if data != None else bytearray()
	
	def write_byte(self, x):
		self.__data[self.position:self.position + 1] = struct.pack('b', x)
		self.position += 1
	
	def write_short(self, x):
		bytes = struct.pack('>H', x)
		self.__data[self.position:self.position + 2] = bytes
		self.position += 2
	
	def write_int(self, x):
		self.__data[self.position:self.position + 4] = struct.pack('>I', x)
		self.position += 4
		
	def write_byte_buffer(self, buffer, offset, length):
		self.__data[self.position:self.position + length] = buffer.__data[offset:offset + length]
		self.position += length
	
	def read_byte(self):
		if self.available() < 1:
			raise ByteBuffer.NoDataAvailableError()
		x = struct.unpack('b', bytearray([self.__data[self.position]]))[0]
		self.position += 1
		return x
	
	def read_unsigned_byte(self):
		if self.available() < 1:
			raise ByteBuffer.NoDataAvailableError()
		x = struct.unpack('B', bytearray([self.__data[self.position]]))[0]
		self.position += 1
		return x
	
	def read_short(self):
		if self.available() < 2:
			raise ByteBuffer.NoDataAvailableError()
		x = struct.unpack('>h', self.__data[self.position:self.position + 2])[0]
		self.position += 2
		return x
	
	def read_unsigned_short(self):
		if self.available() < 2:
			raise ByteBuffer.NoDataAvailableError()
		x = struct.unpack('>H', self.__data[self.position:self.position + 2])[0]
		self.position += 2
		return x
	
	def read_int(self):
		if self.available() < 4:
			raise ByteBuffer.NoDataAvailableError()
		x = struct.unpack('>i', self.__data[self.position:self.position + 4])[0]
		self.position += 4
		return x
	
	def read_unsigned_int(self):
		if self.available() < 4:
			raise ByteBuffer.NoDataAvailableError()
		x = struct.unpack('>I', self.__data[self.position:self.position + 4])[0]
		self.position += 4
		return x
		
	def uncompress(self):
		self.__data = zlib.decompress(self.__data)
	
	def to_string(self):
		return self.__data.decode('utf-8')
	
	def available(self):
		return len(self.__data) - self.position
	
	def size(self):
		return len(self.__data)
		
	def __str__(self):
		return 'ByteBuffer(size={}, pos={}, byteorder={})'.format(len(self.__data), self.position, self.byteorder) 
		
	class NoDataAvailableError(Exception):
		pass