struct Header {
	char	ucm1		[0x08];
	char	model_name	[0x40];
	u32		num_frames;
	u32		num_tris;
	u32		num_vertices;
	u32		num_tags;
	u32		var;
} [[static]];

struct Tri {
	u32 v1 [[color("FF00AAFF")]];
	u32 v2 [[color("FF0044AA")]];
	u32 v3 [[color("FF000055")]];
} [[static]];

struct Vertex {
	float x		[[color("FFFF0000")]];
	float y		[[color("FF00FF00")]];
	float z		[[color("FF0000FF")]];
	float nx	[[color("FF440044")]];
	float ny	[[color("FF004444")]];
	float nz	[[color("FF000088")]];
	float u		[[color("FFFF00AA")]];
	float v		[[color("FFAA00FF")]];
} [[static]];

struct ModelFrame {
	Vertex	vtx_buf	[header.num_vertices];
} [[static]];

struct TagName {
	char	name	[0x10];
} [[static]];

struct Matrix4 {
	float	values	[4 * 3];
	float x [[color("FFFF0000")]];
	float y [[color("FF00FF00")]];
	float z [[color("FF0000FF")]];
	float	last;
} [[static]];

struct TagsFrame {
	Matrix4		tag_matrices	[header.num_tags];
} [[static]];

struct Sphere {
	float x [[color("FFFF0000")]];
	float y [[color("FF00FF00")]];
	float z [[color("FF0000FF")]];
	float radius;
} [[static]];

struct Box {
	float x [[color("FFFF0000")]];
	float y [[color("FF00FF00")]];
	float z	[[color("FF0000FF")]];
	float size_x [[color("FFAA0000")]];
	float size_y [[color("FF00AA00")]];
	float size_z [[color("FF0000AA")]];
	float rotation_matrix		[0x09];
} [[static]];

struct Hitbox {
	u32		num_spheres;
	u32		num_boxes;
	Sphere	spheres		[num_spheres];
	Box		boxes		[num_boxes];
};

Header		header 								@ 0x00;
// Main contents
Tri			idx_buf			[header.num_tris]	@$;
ModelFrame	frames			[header.num_frames]	@$;
// Tags
TagName		tag_names		[header.num_tags]	@$;
TagsFrame	tag_positions	[header.num_frames]	@$;
// Hitbox
Hitbox		hitbox								@$;
