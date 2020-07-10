#Copyright (c) 2020 Jan Kiefer
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from .container_decoder import MediaContainerDecoder

class Decoder:
	
	VERSION_NUMBER = 'Version'
	TILEBASE = 'Tilebase'
	SOUNDS = 'Sounds'
	TRIGGER = 'Trigger'
	TRIGGERS = 'Triggers'
	LIGHTMAP = 'Lightmap'
	LIGHTMAPS = 'Lightmaps'
	IMAGES = 'Images'
	OFFSET_X = 'OffsetX'
	OFFSET_Y = 'OffsetY'
	POLYGON = 'Polygon'
	LABEL = 'Label'
	LVL_AREA_NAME = 'AreaName'
	LVL_ROOM_NAME = 'RoomName'
	LVL_UNITS_U = 'Units-U'
	LVL_UNITS_V = 'Units-V'
	LVL_UNITS_Z = 'Units-Z'
	LVL_MAP = 'LevelMap'
	LVL_COLLISIONMAP = 'CollisionMap'
	LVL_OPTIONALS_COUNT = 'OptDataBlockCount'
	LVL_MASKS = 'Masks'
	LVL_SWFOBJECTS = 'SWFObjects'
	SOUND_LENGTH = 'Length'
	SOUND_OBJ = 'Sound'
	SWF_BOUNDS = 'SwfBounds'
	SWF_DIRECTION = 'SwfDirection'
	SWF_DATA = 'SwfData'
	BLOCK_TYPE_SOUND = 'SND'
	BLOCK_TYPE_SWF = 'SWF'
	BLOCK_TYPE_LIGHTMAP = 'LMP'
	BLOCK_TYPE_TRIGGER = 'TRG'
	BLOCK_TYPE_IMAGE = 'IMG'
	TYPE_LEVEL = 'LVL'
	TYPE_LEVELBG = 'BG'
	TYPE_ISOOBJ = 'OBJ'
	TYPE_MEDIAPACK = 'MED'
	OBJ_DEFAULT_DIRECTION = 'DefaultDirection'
	OBJ_DEFAULT_ANIMATION = 'DefaultAnimation'
	OBJ_DEFAULT_FRAME = 'DefaultFrame'
	OBJ_ANIMATIONS = 'Animations'
	OBJ_ANIM_DIRECTIONS = 'Directions'
	OBJ_ANIM_MIRRORING = 'Mirroring'
	OBJ_ANIM_ISOCOMPONENTBOUNDS = 'Bounds'
	OBJ_ANIM_ORIGINAL_GRIP = 'OriginalGrip'
	OBJ_ANIM_GRIPIMAGES = 'GripImages'
	OBJ_ANIM_FRAMES = 'Frames'
	OBJ_ISOCOMPONENT = 'IsoComponent'
	OBJ_TOP_HEIGHT = 'TopHeight'
	OBJ_TOTAL_HEIGHT = 'TotalHeight'
	OBJ_ANIM_MASKS = 'AnimationMasks'
	OBJ_SIT_BOUNDS = 'SitBounds'
	OBJ_SIT_DIRECTIONS = 'SitDirections'
	OBJ_GRIP_DIRECTION = 'GripDirection'
	OBJ_SIZE_U = 'sizeU'
	OBJ_SIZE_V = 'sizeV'
	MIRROR_MASK = 1
	BOUNDS_MASK = 2
	IFF_TOTAL_HEIGHT = 1
	IFF_TOP_HEIGHT = 2
	IFF_GRIP_OFF_U = 4
	IFF_GRIP_OFF_V = 8
	IFF_GRIP_DATA = 15
	IFD_FRAME_OFF_X = 1
	IFD_FRAME_OFF_Y = 2
	IFD_FRAME_DATA = 4
	IFD_MASK_OFF_X = 8
	IFD_MASK_OFF_Y = 15
	IFD_MASK_DATA = 32
	GRIP_MIRROR_MATRIX = (-6.12303176911189e-17,1,1,6.12303176911189e-17)
	BG_IMAGE = 'BgImage'
	BG_HEIGHT = 'BgHeight'
	BG_WIDTH = 'BgWidth'
	BG_LIGHTMAP = 'BgLightmap'
	BG_OFFSET = 'BgOffset'
	
	ISOGRID_UPT = 16
	
	def __init__(self):
		pass
	
	@staticmethod
	def create_bitmap_data(data, width):
		pass
		
	@staticmethod
	def get_cropped_bitmap_data_at(index, j, k, v_bitmap):
		pass
	
	@staticmethod
	def check_container_type(container, type):
		return container[0][0] == MediaContainerDecoder.TYPE_STRING and container[0][1] == type
	
	@staticmethod
	def decode_level(container, v_bitmap = False):
		result = {}
		if not Decoder.check_container_type(container, Decoder.TYPE_LEVEL):
			print('Media not holding level data')
			return None
		ver_num = container[1]
		if ver_num[0] != MediaContainerDecoder.TYPE_BYTE:
			print('Invalid level version format')
			return None
		ver_num = ver_num[1]
		result[Decoder.VERSION_NUMBER] = ver_num
		if ver_num == 2:
			if Decoder.decode_level_v2(container, result, v_bitmap):
				return result
		else:
			print('Unsupported level format version:', ver_num)
		return None
	
	@staticmethod
	def decode_level_v2(content, result, v_bitmap):
		index = 2
		
		area_name = content[index]
		if area_name[0] != MediaContainerDecoder.TYPE_STRING:
			print('Invalid area name type')
			return False
		result[Decoder.LVL_AREA_NAME] = area_name[1]
		index += 1
		
		room_name = content[index]
		if room_name[0] != MediaContainerDecoder.TYPE_STRING:
			print('Invalid room name type')
			return False
		result[Decoder.LVL_ROOM_NAME] = room_name[1]
		index += 1
		
		units_u = content[index]
		if units_u[0] != MediaContainerDecoder.TYPE_INT:
			print('Invalid Unit-U type')
			return False
		units_u = units_u[1]
		result[Decoder.LVL_UNITS_U] = units_u
		index += 1
		
		units_v = content[index]
		if units_v[0] != MediaContainerDecoder.TYPE_INT:
			print('Invalid Unit-V type')
			return False
		units_v = units_v[1]
		result[Decoder.LVL_UNITS_V] = units_v
		index += 1
		
		units_z = content[index]
		if units_z[0] != MediaContainerDecoder.TYPE_INT:
			print('Invalid Unit-Z type')
			return False
		units_z = units_z[1]
		result[Decoder.LVL_UNITS_Z] = units_z
		index += 1
		
		tilebase = content[index]
		if tilebase[0] != MediaContainerDecoder.TYPE_BYTE:
			print('Invalid tilebase type')
			return False
		result[Decoder.TILEBASE] = tilebase[1]
		index += 1
		
		map = content[index]
		if map[0] != MediaContainerDecoder.TYPE_RAWBYTES:
			print('Invalid map type')
			return False
		map = map[1]
		if map.size() != units_u * units_v * 4:
			print('Invalid map size: {} Expected: {}'.format(map.size(), units_u * units_v * 4))
			return False
		map_data = [None] * units_u * units_v * 4
		for map_v in range(units_v):
			for map_u in range(units_u):
				map_data[int(map_v * units_u + map_u)] = map.read_int()
		result[Decoder.LVL_MAP] = map_data
		index += 1
		
		collision_map = content[index]
		if collision_map[0] != MediaContainerDecoder.TYPE_RAWBYTES:
			print('Invalid collision map type')
			return False
		result[Decoder.LVL_COLLISIONMAP] = Decoder.create_bitmap_data(collision_map[1], units_u)
		index += 1
		
		mask = content[index]
		if mask[0] != MediaContainerDecoder.TYPE_RAWBYTES:
			print('Invalid mask positioning map type')
			return False
		index += 1
		mask = mask[1]
		mask_size_expected = units_u // Decoder.ISOGRID_UPT * units_v // Decoder.ISOGRID_UPT
		if mask.size() * 8 < mask_size_expected:
			print('Size of mask map too small')
			return False
		masks = [None] * mask_size_expected
		mask.position = 0
		buffer = 0
		for x in range(mask_size_expected):
			if x % 8 == 0:
				buffer = mask.read_unsigned_byte()
			if buffer & 128 != 0:
				bitmap = content[index]
				if bitmap[0] != MediaContainerDecoder.TYPE_BITMAP:
					print('Invalid mask type at index', index)
				masks[x] = Decoder.get_cropped_bitmap_data_at(index, 0xFFFFFFFF, 0, v_bitmap)
				index += 1
			buffer <<= 1
		result[Decoder.LVL_MASKS] = masks
		
		opt_blocks_count = content[index]
		if opt_blocks_count[0] != MediaContainerDecoder.TYPE_INT:
			print('Invalid optional blocks count type')
			return False
		opt_blocks_count = opt_blocks_count[1]
		index += 1
		
		sounds = {}
		swf_objects = {}
		
		result[Decoder.SOUNDS] = sounds
		result[Decoder.LVL_SWFOBJECTS] = swf_objects
		
		j = 0
		while True:
			if j >= opt_blocks_count:
				return True
			block_type = content[index]
			if block_type[0] != MediaContainerDecoder.TYPE_STRING:
				print('Invalid optional block type at index', index)
				return False
			block_type = block_type[1]
			index += 1
			if block_type == Decoder.BLOCK_TYPE_SOUND:
				sound_label = content[index]
				if sound_label[0] != MediaContainerDecoder.TYPE_STRING:
					print('Invalid sound label type at index', index)
					return False
				sound_label = sound_label[1]
				index += 1
				if sound_label in sounds:
					print('Duplicate sound label at index', index)
					return False
				
				sound_len = content[index]
				if sound_len[0] != MediaContainerDecoder.TYPE_INT:
					print('Invalid sound length type at index', index)
					return False
				sound_len = sound_len[1]
				index += 1
				
				sound = content[index]
				if sound[0] != MediaContainerDecoder.TYPE_MP3:
					print('Invalid sound type at index', index)
					return False
				sound = sound[1]
				index += 1
				
				sound_obj = {}
				sound_obj[Decoder.SOUND_LENGTH] = sound_len
				sound_obj[Decoder.SOUND_OBJ] = sound
				sounds[sound_label] = sound_obj
			elif block_type == Decoder.BLOCK_TYPE_SWF:
				swf_obj = {}
				
				swf_label = content[index]
				if swf_label[0] != MediaContainerDecoder.TYPE_STRING:
					print('Invalid swf label type at index', index)
					return False
				swf_label = swf_label[1]
				index += 1
				
				if swf_label in swf_objects:
					print('Duplicate swf object at index', index)
					return False
				
				swf_objects[swf_label] = swf_obj
				
				swf_direction = content[index]
				if swf_direction[0] != MediaContainerDecoder.TYPE_BYTE:
					print('Invalid swf direction type at index', index)
					return False
				swf_direction = swf_direction[1]
				if swf_direction == 0:
					print('Swf direction cannot be zero')
					return False
				
				k = -1
				tmp = 0
				
				while swf_direction > 0:
					k += 1
					tmp = swf_direction & 1
					swf_direction >>= 1
					if tmp > 0:
						break
				
				if swf_direction > 0:
					print('Swf direction must has more than one bit set:', content[index][1])
					return False
				
				swf_obj[Decoder.SWF_DIRECTION] = k
				index += 1
				
				swf_bounds = content[index]
				if swf_bounds[0] != MediaContainerDecoder.TYPE_RAWBYTES:
					print('Invalid swf bounds type at index', index)
					return False
				swf_bounds = swf_bounds[1]
				if swf_bounds.size() != 16:
					print('Invalid swf bounds size: {} Expected: 16'.format(swf_bounds.size()))
					return False
				swf_obj[Decoder.SWF_BOUNDS] = {'x': swf_bounds.read_int(),
											   'y': swf_bounds.read_int(),
											   'width': swf_bounds.read_int(),
											   'height': swf_bounds.read_int()}
				index += 1
				
				swf_data = content[index]
				if swf_data[0] != MediaContainerDecoder.TYPE_ROOMCOMP:
					print('Invalid swf data type')
					return False
				swf_obj[Decoder.SWF_DATA] = swf_data[1]
				
			else:
				break
			index += 1
			j += 1
		
		print('Unknown block type at index', index)
		return False