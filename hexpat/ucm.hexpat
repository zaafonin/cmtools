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

struct ModelFrame {
	Vertex	vtx_buf	[header.num_vertices];
} [[static]];

struct TagName {
	char	name	[0x10];
} [[static]];

struct Matrix4 {
	float	values	[4 * 3];
	float	x, y, z;
	float	last;
} [[static]];

struct TagFrame {
	Matrix4		transformation_matrices	[header.num_tags];
} [[static]];

struct Sphere {
	float	x, y, z;
	float	radius;
} [[static]];

struct Box {
	float	x, y, z;
	float	size_x, size_y, size_z;
	float	rotation_matrix	[0x09];
} [[static]];

Header		header 										@ 0x00;
u32			indices			[header.num_polygons * 3]	@$;
ModelFrame	frames			[header.num_frames]			@$;
TagName		tag_names		[header.num_tags]			@$;
TagFrame	tag_positions	[header.num_frames]			@$;
u32			num_spheres									@$;
u32			num_boxes									@$;
Sphere		spheres			[num_spheres]				@$;
Box		boxes				[num_boxes]					@$;
