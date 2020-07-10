#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from freggersbot.utils.bytebuffer import ByteBuffer

class UtfMessage:
	
	MAX_SIZE = 8193
	TYPE_UNKNOWN = -1
	TYPE_RECORD = 0
	TYPE_CHARS = 1
	TYPE_SHORTINT = 2
	TYPE_LONGINT = 3
	TYPE_NULL = 4
	TYPE_BOOLTRUE = 5
	TYPE_BOOLFALSE = 6
	TYPE_INT = 8
	TYPE_BOOLEAN = 9
	
	def __init__(self):
		self.__arg_type_list = []
		self.__arg_list = []
		self.__flag_prepared = False
		self.__read_buffer = 0
		self.__read_expected = 0
		self.__data_pos = 0
		self.__data_expected = 0
		self.__data = ByteBuffer()
	
	@staticmethod
	def as_hash(msg):
		pass
	
	@staticmethod
	def as_array(msg):
		pass
	
	@staticmethod
	def gen_header(k, v):
		return v << 3 & 65528 | k & 7
	
	@staticmethod
	def header_type(header):
		return header & 7
	
	@staticmethod
	def header_size(header):
		return header >> 3 & 8191
	
	@staticmethod
	def encode_to_utf8(val):
		res = bytearray()
		if val >= 0 and val <= 127:
			res.append(val & 127)
		elif val > 2047:
			res.append(224 | val >> 12 & 15)
			res.append(128 | val >> 6 & 63)
			res.append(128 | val & 63)
		else:
			res.append(192 | val >> 6 & 31)
			res.append(128 | val & 63)
		return res
	
	def add_message_arg(self, msg):
		self.__arg_type_list.append(UtfMessage.TYPE_RECORD)
		self.__arg_list.append(msg)
		self.__flag_prepared = False
		return self
	
	def add_string_arg(self, s):
		self.__arg_type_list.append(UtfMessage.TYPE_CHARS)
		self.__arg_list.append(s)
		self.__flag_prepared = False
		return self
	
	def add_int_arg(self, i):
		return self.add_int_list_arg([i])
	
	def add_int_list_arg(self, i_array):
		self.__arg_type_list.append(UtfMessage.TYPE_INT)
		self.__arg_list.append(i_array)
		self.__flag_prepared = False
		return self
	
	def add_null_arg(self):
		self.__arg_type_list.append(UtfMessage.TYPE_NULL)
		self.__arg_list.append(None)
		self.__flag_prepared = False
		return self
	
	def add_boolean_arg(self, val):
		self.__arg_type_list.append(UtfMessage.TYPE_BOOLEAN)
		self.__arg_list.append(val)
		self.__flag_prepared = False
		return self
	
	def get_arg_count(self):
		return len(self.__arg_list)
	
	def get_arg_type(self, index):
		return self.__arg_type_list[index]
	
	def estimate(self):
		amount = 1
		for index in range(len(self.__arg_type_list)):
			arg = self.__arg_list[index]
			arg_type = self.__arg_type_list[index]
			
			if arg_type == UtfMessage.TYPE_RECORD:
				amount += arg.estimate()
			elif arg_type == UtfMessage.TYPE_CHARS:
				amount += len(arg) + 1
			elif UtfMessage.TYPE_INT:
				max_val = 0
				for i in arg:
					max_val = max(abs(i), max_val)
				if max_val < 32768:
					amount += 1 + len(arg)
				else:
					amount += 1 + 2 * len(arg)
			elif arg_type == UtfMessage.TYPE_NULL or arg_type == UtfMessage.TYPE_BOOLEAN:
				amount += 1
		return amount
	
	def freespace(self):
		return UtfMessage.MAX_SIZE - self.estimate()
	
	def get_message_arg(self, index):
		if index < len(self.__arg_type_list) and self.__arg_type_list[index] == UtfMessage.TYPE_RECORD:
			return self.__arg_list[index]
		return None
	
	def get_string_arg(self, index):
		if index < len(self.__arg_type_list) and self.__arg_type_list[index] == UtfMessage.TYPE_CHARS:
			return self.__arg_list[index]
		return None
		
	def get_int_arg(self, index):
		if index < len(self.__arg_type_list) and self.__arg_type_list[index] == UtfMessage.TYPE_INT:
			list = self.__arg_list[index]
			if len(list) > 0:
				return list[0]
		return None
	
	def get_int_list_arg(self, index):
		if index < len(self.__arg_type_list) and self.__arg_type_list[index] == UtfMessage.TYPE_INT:
			return self.__arg_list[index]
		return None
	
	def get_null_arg(self, index):
		return None
	
	def get_boolean_arg(self, index):
		if index < len(self.__arg_type_list) and self.__arg_type_list[index] == UtfMessage.TYPE_BOOLEAN:
			return self.__arg_list[index] == True
		return None
	
	def reset(self, prepare):
		self.__arg_type_list.clear()
		self.__arg_list.clear()
		self.__flag_prepared = False
		if prepare:
			self.__data_pos = 0
			self.__data = ByteBuffer()
			self.__data_expected = 0
			self.__flag_prepared = True
	
	def add_data_to(self, msg):
		msg.add_data(self.__data, 0, self.__data_pos)
		return self.__data_pos
	
	def add_data(self, data, offset, len):
		self.__flag_prepared = False
		self.__data.write_byte_buffer(data, offset * 2, len * 2)
		self.__data_pos += len
	
	def set_data(self, data, pos):
		if self.__flag_prepared:
			self.reset(True)
		self.__data = data
		self.__data_pos = pos
		self.__flag_prepared = False
	
	def extract_data_to(self, offset, len, msg):
		data = ByteBuffer()
		data.write_byte_buffer(self.__data, offset * 2, len * 2)
		msg.set_data(data, len)
		return offset + len
	
	def copy_data_to(self, msg, offset):
		data = ByteBuffer()
		data.write_byte_buffer(self.__data, offset * 2, self.__data_pos * 2)
		msg.set_data(data, self.__data_pos)
		return self.__data_pos
	
	def get_arg(self, index):
		return self.__arg_list[index]
	
	def pack(self):
		flag_success = True
		self.__data = ByteBuffer()
		self.__data.write_short(0)
		self.__data_pos = 1
		index = 0
		while index < len(self.__arg_list) and flag_success:
			arg = self.__arg_list[index]
			arg_type = self.__arg_type_list[index]
			
			if arg_type == UtfMessage.TYPE_RECORD:
				if arg.pack():
					self.__data_pos += arg.add_data_to(self)
				else:
					flag_success = False
			elif arg_type == UtfMessage.TYPE_CHARS:
				self.__data.write_short(UtfMessage.gen_header(UtfMessage.TYPE_CHARS, len(arg)))
				for x in range(len(arg)):
					self.__data.write_short(ord(arg[x]))
			elif arg_type == UtfMessage.TYPE_INT:
				max_val = 0
				for i in arg:
					max_val = max(max_val, abs(i))
				int_type = UtfMessage.TYPE_SHORTINT if max_val < 32768 else UtfMessage.TYPE_LONGINT
				if int_type == UtfMessage.TYPE_SHORTINT:
					self.__data.write_short(UtfMessage.gen_header(int_type, len(arg)))
					for i in arg:
						self.__data.write_short(i + 65536 & 65535)
				else:
					self.__data.write_short(UtfMessage.gen_header(int_type, len(arg) * 2))
					for i in arg:
						self.__data.write_int(i)
			elif arg_type == UtfMessage.TYPE_NULL:
				self.__data.write_short(UtfMessage.gen_header(UtfMessage.TYPE_NULL, 0))
			elif arg_type == UtfMessage.TYPE_BOOLEAN:
				self.__data.write_short(UtfMessage.gen_header(UtfMessage.TYPE_BOOLTRUE if arg == True else UtfMessage.TYPE_BOOLFALSE, 0))
			else:
				flag_success = False
			self.__data_pos = self.__data.size() // 2
			index += 1
		self.__data.position = 0
		self.__data.write_short(UtfMessage.gen_header(UtfMessage.TYPE_RECORD, self.__data_pos - 1))
		self.__data.position = self.__data_pos * 2
		if flag_success:
			self.__flag_prepared = True
		return flag_success
	
	def unpack(self):
		flag_success = True
		self.__data.position = 0
		header = self.__data.read_short() & 65535
		if UtfMessage.header_type(header) != UtfMessage.TYPE_RECORD:
			print('pack error: record type')
			return False
		size = UtfMessage.header_size(header)
		while self.__data.position < (size + 1) * 2 and flag_success:
			arg = None
			header = self.__data.read_short() & 65535
			arg_type = UtfMessage.header_type(header)
			arg_size = UtfMessage.header_size(header)
			if arg_type == UtfMessage.TYPE_RECORD:
				msg = UtfMessage()
				self.__data.position = 2 * self.extract_data_to(self.__data.position // 2 - 1, arg_size + 1, msg)
				if msg.unpack():
					arg = msg
				else:
					flag_success = False
			elif arg_type == UtfMessage.TYPE_CHARS:
				arg = ''
				for _ in range(arg_size):
					arg += chr(self.__data.read_short() & 65535)
			elif arg_type == UtfMessage.TYPE_SHORTINT:
				arg = []
				for _ in range(arg_size):
					val = self.__data.read_short() & 65535
					if val >= 32768:
						val -= 65536
					arg.append(val)
				arg_type = UtfMessage.TYPE_INT
			elif arg_type == UtfMessage.TYPE_LONGINT:
				arg = []
				for _ in range(0, arg_size, 2):
					arg.append(self.__data.read_int())
				arg_type = UtfMessage.TYPE_INT
			elif arg_type == UtfMessage.TYPE_NULL:
				arg = None
			elif arg_type == UtfMessage.TYPE_BOOLTRUE:
				arg = True
				arg_type = UtfMessage.TYPE_BOOLEAN
			elif arg_type == UtfMessage.TYPE_BOOLFALSE:
				arg = False
				arg_type = UtfMessage.TYPE_BOOLEAN
			else:
				arg_type = UtfMessage.TYPE_UNKNOWN
				arg = []
				for _ in range(arg_size):
					arg.append(self.__data.read_short())
			self.__arg_type_list.append(arg_type)
			self.__arg_list.append(arg)
		self.__data_pos = self.__data.position // 2
		if flag_success:
			self.__flag_prepared = True
		return self.__flag_prepared
			
	def dump(self, name = ''):
		if not self.__flag_prepared:
			self.unpack()
		dump = name + '{  # RECORD ' + str(len(self.__arg_list)) + ' args\n'
		
		for index in range(len(self.__arg_list)):
			arg = self.__arg_list[index]
			dump += name + str(index) + ': '
			arg_type = self.__arg_type_list[index]
			if arg_type == UtfMessage.TYPE_RECORD:
				dump += arg.dump(name + '    ')
			elif arg_type == UtfMessage.TYPE_CHARS:
				dump += '"' + arg + '"  # STRING length ' + str(len(arg)) + '\n'
			elif arg_type == UtfMessage.TYPE_INT:
				dump += '['
				for k in range(len(arg)):
					if k > 0:
						dump += ','
					dump += str(arg[k])
				dump += ']  # INT ' + str(len(arg)) + ' args\n'
			elif arg_type == UtfMessage.TYPE_NULL:
				dump += 'NULL\n'
			elif arg_type == UtfMessage.TYPE_BOOLEAN:
				dump += 'true\n' if arg == True else 'false\n'
			elif arg_type == UtfMessage.TYPE_UNKNOWN:
				dump += 'UNKNOWN \'' + str(arg) + '\'\n'
		dump += name + '}  # end RECORD data_pos=' + str(self.__data_pos) + ' chunks: ' + str(self.__data.size()) + '\n'
		return dump
		
	def is_prepared(self):
		return self.__flag_prepared
		
	def get_length(self):
		if not self.__flag_prepared:
			self.pack()
		return self.__data.position // 2
	
	def read(self, sock):
		while True:
			r = sock.recv(1)
			if len(r) == 0:
				return False
			b = r[0]
			j = b >> 4 & 15
			if j >= 8 and j <= 11:
				self.__read_buffer = self.__read_buffer << 6 | b & 63
				self.__read_expected -= 1
				if self.__read_expected < 0:
					break
			elif j == 12 or j == 13:
				self.__read_buffer = b & 31
				self.__read_expected = 1
			elif j == 14:
				self.__read_buffer = b & 15
				self.__read_expected = 2
			elif j == 15:
				self.__read_buffer = b & 7
				self.__read_expected = 3
			else:
				self.__read_buffer = b & 127
				self.__read_expected = 0
			if self.__read_expected == 0:
				self.__data.write_short(self.__read_buffer & 0xFFFF)
				self.__data_pos += 1
				if self.__data_pos == 1 and self.__read_buffer == 0:
					self.__flag_prepared = True
					return True
				self.__read_buffer = 0
				if self.__data_expected == 0:
					prev_pos = self.__data.position
					self.__data.position = 0
					header = self.__data.read_short() & 0xFFFF
					self.__data.position = prev_pos
					if UtfMessage.header_type(header) != UtfMessage.TYPE_RECORD:
						self.__data_expected = 0
						self.__flag_prepared = True
						return True
					self.__data_expected = UtfMessage.header_size(header) + 1
				if self.__data_pos >= self.__data_expected:
					if self.__data_pos > self.__data_expected:
						return True
					self.reset(False)
					self.unpack()
					return True
		self.__read_buffer = 0
		return False
	
	def send(self, sock):
		if not self.__flag_prepared:
			self.pack()
		msg = bytearray()
		self.__data.position = 0
		while self.__data.available() > 0:
			s = self.__data.read_short() & 65535
			if s == 0:
				msg.extend([0])
			else:
				msg.extend(UtfMessage.encode_to_utf8(s))
		sock.sendall(msg)
		return len(msg)
	
	def hex_dump(self):
		data = self.__data
		if data == None or data.size() == 0:
			return ''
		str = 'Binary data: '
		data.position = 0
		while data.available() > 0:
			hex_short = hex(data.read_short() & 65535).replace('0x','')
			str += '0' * (4 - len(hex_short)) + hex_short + ' '
		return str
	
	def clone(self):
		msg = UtfMessage()
		if self.__arg_list != None:
			msg.__arg_list = self.__arg_list.copy()
		if self.__arg_type_list != None:
			msg.__arg_type_list = self.__arg_type_list.copy()
		msg.__flag_prepared = self.__flag_prepared
		msg.__data_expected = self.__data_expected
		msg.__data_pos = self.__data_pos
		if self.__data != None:
			data = ByteBuffer()
			data.write_byte_buffer(self.__data, 0, self.__data.size()) #ANOMALY data.readBytes(this.data);
			msg.__data = data
		msg.__read_expected = self.__read_expected
		msg.__read_buffer = self.__read_buffer
		return msg