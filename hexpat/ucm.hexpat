struct Header {
	char	magic	[0x08];
	char	name	[0x10];
	padding	[0x30];
	u32		var1;
	u32		polygons;
	u32		vertices;
	u32		tags;
	u32		var2;
};

struct Vertex {
	float	x, y, z, nx, ny, nz, u, v;
};

struct TagName {
	char	name	[0x10];
};

struct Tag {
	float	unknown	[0x10];
};

struct UCM {
	Header	header;
	u32		idx_buf	[header.polygons * 3];
	Vertex	vtx_buf	[header.vertices];
	TagName	tag_names	[header.tags];
	Tag		tag_buf		[header.tags];
};

UCM	ucm @ 0x00;


