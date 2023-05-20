bl_info = {
    "name": "UCM Importer",
    "author": "Zakhar Afonin",
    "version": (1, 0),
    "blender": (2, 83, 0),
    "location": "File > Import > UCM (.ucm)",
    "description": "Import UCM models",
    "category": "Import-Export",
}

import bpy
import bpy_extras
import bmesh
import os
import struct
from math import radians
from mathutils import Vector, Matrix


# Helper function to parse UCM file
def read_ucm_file(filepath):
    with open(filepath, 'rb') as f:
        # Read header. Usually UCM1....
        magic_string = f.read(8)
        
        model_name = f.read(64).split(b'\x00')[0].decode('ascii')
        # Fallback for untitled models
        if not model_name:
            model_name = filepath.replace('\\', '/').split('/')[-1].replace('.UCM', '.ucm').split('.ucm')[0]
        num_frames, num_tris, num_vertices, num_tags, unknown_number = struct.unpack('5I', f.read(20))
        
        # Read index buffer
        index_buffer = [tuple(struct.unpack('3I', f.read(12))) for _ in range(num_tris)]

        # Read vertex buffers
        vertex_buffers = []
        for _ in range(num_frames):
            vertex_buffer = []
            for _ in range(num_vertices):
                vertex_data = struct.unpack('8f', f.read(32))
                vertex_buffer.append(vertex_data)
            vertex_buffers.append(vertex_buffer)

        # Read tag names
        tag_names = [f.read(16).split(b'\x00')[0].decode('ascii') for _ in range(num_tags)]

        # Read tag position arrays
        tag_position_arrays = []
        for _ in range(num_frames):
            tag_positions = [Matrix((*(struct.unpack('4f', f.read(16)) for _ in range(4)),)).transposed() for _ in range(num_tags)]
            tag_position_arrays.append(tag_positions)

        try:
            # Read hitbox structure
            num_spheres, num_cuboids = struct.unpack('2I', f.read(8))
        except struct.error:
            # No hitbox data: model from Earth Squad
            num_spheres, num_cuboids = 0, 0

        # Read hitbox spheres
        hitbox_spheres = []
        for _ in range(num_spheres):
            position = Vector(struct.unpack('3f', f.read(12)))
            radius = struct.unpack('1f', f.read(4))[0]
            hitbox_spheres.append((position, radius))

        # Read hitbox cuboids
        hitbox_boxes = []
        for _ in range(num_cuboids):
            position = Vector(struct.unpack('3f', f.read(12)))
            size = Vector(struct.unpack('3f', f.read(12)))
            rotation = Matrix((*(struct.unpack('3f', f.read(12)) for _ in range(3)),)).transposed()
            hitbox_boxes.append((position, size, rotation))

    return {
        'model_name': model_name,
        'num_frames': num_frames,
        'index_buffer': index_buffer,
        'vertex_buffers': vertex_buffers,
        'tag_names': tag_names,
        'tag_position_arrays': tag_position_arrays,
        'hitbox_spheres': hitbox_spheres,
        'hitbox_boxes': hitbox_boxes,
    }


def create_mesh_objects(parsed_ucm_data, frame_collections):
    mesh_objects = []
    
    index_buffer = parsed_ucm_data["index_buffer"]
    
    for frame_idx, vertex_buffer in enumerate(parsed_ucm_data["vertex_buffers"]):
        mesh_data = bpy.data.meshes.new(f"{parsed_ucm_data['model_name']}_frame{frame_idx}_")
        
        dd_xyzs = []
        dd_uvs = []
        dd_normals = []
        
        dd_tris = []
        
        for raw_tri in index_buffer:
            tri = []
            for index in raw_tri:
                raw_vertex = vertex_buffer[index]
                xyz = (raw_vertex[0], raw_vertex[1], raw_vertex[2])
                normal = (raw_vertex[3], raw_vertex[4], raw_vertex[5])
                uv = (raw_vertex[6], raw_vertex[7])
                
                try:
                    idx_xyz = dd_xyzs.index(xyz)
                except ValueError:
                    idx_xyz = len(dd_xyzs)
                    dd_xyzs.append(xyz)
                    
                try:
                    idx_uv = dd_xyzs.index(uv)
                except ValueError:
                    idx_uv = len(dd_uvs)
                    dd_uvs.append(uv)
                    
                try:
                    idx_normal = dd_normals.index(normal)
                except ValueError:
                    idx_normal = len(dd_normals)
                    dd_normals.append(normal)
                tri.append((idx_xyz, idx_uv, idx_normal))
            dd_tris.append(tri)
        
        face_indices = [tuple(trindex[0] for trindex in tri) for tri in dd_tris]
        mesh_data.from_pydata(dd_xyzs, [], face_indices)
        
        mesh_data.use_auto_smooth = True
        
        normals = [(0, 0, 0) for l in mesh_data.loops]
        
        uv_layer = mesh_data.uv_layers.new()
        uvs = mesh_data.uv_layers.active.data
        
        for poly in mesh_data.polygons:
            tri = dd_tris[face_indices.index(tuple(vert for vert in poly.vertices))]
            for i, loop_index in enumerate(poly.loop_indices):
                normals[loop_index] = dd_normals[tri[i][2]]
                uv = dd_uvs[tri[i][1]]
                uvs[loop_index].uv.x = uv[0]
                uvs[loop_index].uv.y = uv[1] * -1
        mesh_data.normals_split_custom_set(normals)

        # Update mesh
        mesh_data.update()

        # Create mesh object and link to the scene
        mesh_object = bpy.data.objects.new(f"{parsed_ucm_data['model_name']}_frame{frame_idx}_", mesh_data)
        frame_collections[frame_idx].objects.link(mesh_object)


# Helper function to create tags
def create_tags(parsed_ucm_data, frame_collections):
    tag_objects = []

    print(parsed_ucm_data["tag_position_arrays"])
    for tag_idx, tag_name in enumerate(parsed_ucm_data["tag_names"]):
        for frame_idx, tag_position_array in enumerate(parsed_ucm_data["tag_position_arrays"]):
            tag_matrix = tag_position_array[tag_idx]

            # Create Blender empty of type "Arrows"
            tag_object = bpy.data.objects.new(f"{parsed_ucm_data['model_name']}_frame{frame_idx}_{tag_name}", None)
            tag_object.empty_display_type = 'ARROWS'
            tag_object.empty_display_size = 0.15
            tag_object.show_name = True

            # Set the position and rotation from the tag's Matrix4
            tag_object.matrix_world = tag_matrix

            # Link the tag object to the corresponding frame collection
            frame_collections[frame_idx].objects.link(tag_object)


# Helper function to create hitboxes
def create_hitboxes(parsed_ucm_data, hitbox_collection):
    # Create sphere hitboxes
    for sphere in parsed_ucm_data["hitbox_spheres"]:
        xyz, radius = sphere

        # Create a Blender empty of type "Sphere"
        sphere_object = bpy.data.objects.new(f"{parsed_ucm_data['model_name']}_hitbox_sphere", None)
        sphere_object.empty_display_type = 'SPHERE'
        sphere_object.empty_display_size = radius
        sphere_object.location = xyz

        # Link the sphere object to the hitbox collection
        hitbox_collection.objects.link(sphere_object)

    # Create box hitboxes
    for box in parsed_ucm_data["hitbox_boxes"]:
        xyz, size, rotation_matrix = box
        width, height, depth = size.to_tuple()
        
        # Create a Blender empty of type "Cube"
        box_object = bpy.data.objects.new(f"{parsed_ucm_data['model_name']}_hitbox_box", None)
        box_object.empty_display_type = 'CUBE'
        box_object.location = xyz
        box_object.rotation_euler = rotation_matrix.to_euler()

        # Scale the box object based on the width, height, and depth
        box_object.scale = size

        # Link the box object to the hitbox collection
        hitbox_collection.objects.link(box_object)


class ImportUCMOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import_scene.ucm"
    bl_label = "Import UCM"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Load a UCM file. Supports full mesh animations, CM1 tags and hitboxes."
    filename_ext = ".ucm"
    filter_glob: bpy.props.StringProperty(
        default="*.ucm",
        options={'HIDDEN'},
        maxlen=255,  # Max length of the filter in characters
    )
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        # Read and parse the UCM file
        parsed_ucm_data = read_ucm_file(self.filepath)
        print(parsed_ucm_data)
        
        # Create collections and add objects
        # Base Collection
        base_collection = bpy.data.collections.new(name=parsed_ucm_data["model_name"])
        bpy.context.scene.collection.children.link(base_collection)
        
        # Frame Collections
        frame_collections = []
        for frame_idx in range(parsed_ucm_data["num_frames"]):
            frame_collection = bpy.data.collections.new(name=f"{parsed_ucm_data['model_name']}_frame{frame_idx}")
            base_collection.children.link(frame_collection)
            frame_collections.append(frame_collection)
            
        # Create mesh objects
        create_mesh_objects(parsed_ucm_data, frame_collections)

        # Create tags
        create_tags(parsed_ucm_data, frame_collections)

        # Hitbox Collection
        hitbox_collection = bpy.data.collections.new(name=f"{parsed_ucm_data['model_name']}_hitbox")
        base_collection.children.link(hitbox_collection)
        
        # Create hitboxes
        create_hitboxes(parsed_ucm_data, hitbox_collection)

        # Create the "origin" empty for easy transformations
        origin_object = bpy.data.objects.new(f"{parsed_ucm_data['model_name']}_origin", None)
        origin_object.empty_display_type = 'PLAIN_AXES'
        origin_object.empty_display_size = 0.5
        
        # Make the origin parent all other imported objects
        for object in base_collection.all_objects:
            object.parent = origin_object
            
        base_collection.objects.link(origin_object)
                
        # Flip and rotate the model by transforming the origin
        origin_object.scale = Vector((-1, 1, 1))
        origin_object.rotation_euler[0] = radians(90)
        origin_object.rotation_euler[2] = radians(180)
        
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportUCMOperator.bl_idname, text="Earth Squad / Crazy Machines (.ucm)")


def register():
    bpy.utils.register_class(ImportUCMOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportUCMOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()