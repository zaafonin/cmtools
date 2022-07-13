struct Header {
	char	ucm2	[0x08];
	char	name	[0x40];
	u32		num_frames;
	u32		num_polygons;
	u32		num_vertices;
	u32		num_tags;
	u32		var2;
} [[static]];

struct Vertex {
	float	x, y, z, nx, ny, nz, u, v;
} [[static]];

struct Frame {
	Vertex	vtx_buf	[header.num_vertices];
};

struct TagName {
	char	name	[0x10];
} [[static]];

struct Tag {
	float	data1	[0x0C];
	float	x, y, z;
	float	data2;
} [[static]];

struct FrameTags {
	Tag		tags	[header.num_tags];
};

struct Cylinder {
	float	data	[0x10];
};

struct Rect {
	float	data	[0x3C];
};

Header		header 									@ 0x00;
u32			indices		[header.num_polygons * 3]	@$;
Frame		frames		[header.num_frames]			@$;
TagName		tag_names	[header.num_tags]			@$;
FrameTags	tags		[header.num_frames]			@$;
// Hitbox not fully documented
u32			num_cylinders							@$;
u32			num_rects								@$;
Cylinder	cylinders								@$;
Rect		rects									@$;
