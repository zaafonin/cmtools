import pdb; pdb.set_trace()

bl_info = {
    "name": "UCM Exporter",
    "author": "Zakhar Afonin",
    "version": (1, 0),
    "blender": (2, 83, 0),
    "location": "File > Export > UCM (.ucm)",
    "description": "Export UCM models",
    "category": "Import-Export",
}

import bpy
import bpy_extras
import bmesh
import os
import struct
from math import radians
from mathutils import Vector, Matrix


def gather_data_from_collection(collection):
    data = {
        'model_name': '',
        'num_frames': 0,
        'index_buffer': [],
        'vertex_buffers': [],
        'tag_names': [],
        'tag_position_arrays': [],
        'hitbox_spheres': [],
        'hitbox_boxes': [],
    }

    # Iterate over subcollections
    for subcollection in collection.children:
        if subcollection.name.startswith(collection.name + "_frame"):
            # Frame-specific collections
            frame_index = int(subcollection.name.split("_frame")[-1])
            data['num_frames'] = max(data['num_frames'], frame_index + 1)
            
            # Extract vertex buffers (meshes)
            for obj in subcollection.objects:
                if obj.type == 'MESH':
                    mesh = obj.data
                    print(mesh.vertices, len(mesh.vertices))
                    if frame_index >= len(data['vertex_buffers']):
                        data['vertex_buffers'].append([])
                    
                    # Assuming the mesh has UVs and normals
                    uv_layer = mesh.uv_layers.active.data if mesh.uv_layers else None
                    for poly in mesh.polygons:
                        for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                            loop = mesh.loops[loop_index]
                            vertex = mesh.vertices[loop.vertex_index]
                            normal = vertex.normal
                            uv = uv_layer[loop_index].uv if uv_layer else (0, 0)
                            
                            # Combine xyz, normal, and uv into a single tuple
                            vertex_data = (vertex.co.x, vertex.co.y, vertex.co.z, normal.x, normal.y, normal.z, uv[0], uv[1])
                            data['vertex_buffers'][frame_index].append(vertex_data)
                    
                    index_buffer = [i for i in range(len(data['vertex_buffers'][frame_index]))]
                    data['index_buffer'] = [index_buffer[i:i+3] for i in range(0, len(index_buffer), 3)]
                    
                    '''if data['vertex_buffers']:
                        # Use the first frame's vertex buffer as the basis for unique vertices
                        first_frame_vertices = data['vertex_buffers'][0]
                        unique_vertices = list(set(first_frame_vertices))
                        unique_vertex_map = {vertex: index for index, vertex in enumerate(unique_vertices)}

                        # Create an index buffer for the first frame based on the unique vertex map
                        index_buffer = [unique_vertex_map[vertex] for vertex in first_frame_vertices]
                        # Organize the index buffer in groups of three to represent polygons
                        data['index_buffer'] = [index_buffer[i:i+3] for i in range(0, len(index_buffer), 3)]

                        # For each frame, fill the corresponding buffer with original values indexed by the unique indices
                        for frame_idx in range(data['num_frames']):
                            if frame_idx >= len(data['vertex_buffers']):
                                data['vertex_buffers'].append([])
                            frame_vertices = data['vertex_buffers'][frame_idx]
                            frame_buffer = [frame_vertices[index] for index in index_buffer]
                            data['vertex_buffers'][frame_idx] = frame_buffer'''
            
            # Extract tags
            for obj in subcollection.objects:
                if obj.type == 'EMPTY' and obj.empty_display_type == 'PLAIN_AXES':
                    data['tag_names'].append(obj.name)
                    data['tag_position_arrays'].append([obj.matrix_world])

        elif subcollection.name == collection.name + "_hitbox":
            # Hitbox collection
            for obj in subcollection.objects:
                if obj.type == 'EMPTY':
                    if obj.empty_display_type == 'SPHERE':
                        data['hitbox_spheres'].append((obj.location, obj.empty_display_size))
                    elif obj.empty_display_type == 'CUBE':
                        data['hitbox_boxes'].append((obj.location, obj.dimensions, obj.rotation_euler.to_matrix().to_3x3()))


    return data


def mat3_to_tuple(mat):
    return tuple(mat[i // 3][i % 3] for i in range(0, 9))


def mat4_to_tuple(mat):
    return tuple(mat[i // 4][i % 4] for i in range(0, 16))


def write_ucm_file(filepath, model_name, num_frames, index_buffer, vertex_buffers, tag_names, tag_position_arrays, hitbox_spheres, hitbox_boxes):
    with open(filepath, 'wb') as f:
        # Write header
        f.write(b'UCM1')
        f.write(struct.pack('1I', 2)) # Version 2 = Crazy Machines
        f.write(model_name.encode('ascii').ljust(64, b'\x00'))
        
        # Write model metadata
        f.write(struct.pack('5I', num_frames, len(index_buffer), len(vertex_buffers[0]), len(tag_names), 0))
        
        # Write index buffer
        for tri in index_buffer:
            f.write(struct.pack('3I', *tri))
        
        # Write vertex buffers
        for frame_idx, vertex_buffer in enumerate(vertex_buffers):
            for vertex in vertex_buffer:
                f.write(struct.pack('8f', *vertex))
        
        # Write tag names
        for tag_name in tag_names:
            f.write(tag_name.encode('ascii').ljust(16, b'\x00'))
        
        # Write tag position arrays
        for frame_idx, tag_position_array in enumerate(tag_position_arrays):
            for tag_position in tag_position_array:
                f.write(struct.pack('16f', *mat4_to_tuple(tag_position.transposed())))
        
        # Write hitbox data
        f.write(struct.pack('2I', len(hitbox_spheres), len(hitbox_boxes)))
        
        # Write hitbox spheres
        for sphere in hitbox_spheres:
            f.write(struct.pack('3f', *sphere[0]))
            f.write(struct.pack('1f', sphere[1]))
        
        # Write hitbox cuboids
        for box in hitbox_boxes:
            f.write(struct.pack('3f', *box[0]))
            f.write(struct.pack('3f', *box[1]))
            f.write(struct.pack('9f', *mat3_to_tuple(box[2].transposed())))


class ExportUCMOperator(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "export_scene.ucm"
    bl_label = "Export UCM"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Create a UCM file. Use after selecting the collection created with the UCM importer."
    filename_ext = ".ucm"
    filter_glob: bpy.props.StringProperty(
        default="*.ucm",
        options={'HIDDEN'},
        maxlen=255,  # Max length of the filter in characters
    )
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        # Gather data from the selected collection
        data = gather_data_from_collection(context.collection)
        print(data)
        
        # Write the UCM file
        write_ucm_file(self.filepath, data['model_name'], data['num_frames'], data['index_buffer'], data['vertex_buffers'], data['tag_names'], data['tag_position_arrays'], data['hitbox_spheres'], data['hitbox_boxes'])
        
        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportUCMOperator.bl_idname, text="Earth Squad / Crazy Machines (.ucm)")


def register():
    bpy.utils.register_class(ExportUCMOperator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportUCMOperator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
