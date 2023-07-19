bl_info = {
    "name": "Blender to SAF",
    "description": "Convert Blender Animation into PRE-SAF Animations.",
    "author": "DooMMetaL",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Panel > Blender-to-SAF",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "https://github.com/dragoonsouls/Blender-Anim-To-TLoD/README.md"
                "blender_to_saf/blender_to_saf",
    "tracker_url": "https://github.com/dragoonsouls/Blender-Anim-To-TLoD/issues",
    "support": "COMMUNITY",
    "category": "Animation",
}


import bpy
import os
import math


class BLEND2SAF_PT_blend2saf(bpy.types.Panel):
    bl_label = "Convert to SAF"
    bl_idname = "BLEND2SAF_PT_blend2saf"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender-to-SAF"
    
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column()
        
        col.label(text="Blender to SAF - PANEL")
        col.operator("convertsaf.convert_saf",icon='ARMATURE_DATA')


class CONVERTSAF_OT_convert_saf(bpy.types.Operator):
    """Convert Blender Animation into Pre-SAF Format"""
    bl_label = "Convert SAF"
    bl_idname = "convertsaf.convert_saf"
    
    def execute(self, context):
        path_model_file = bpy.path.abspath(bpy.context.blend_data.filepath)
        bpy.ops.object.select_all(action='DESELECT')
        scene_complete = bpy.data.scenes["Scene"]
        start_frame_anim = scene_complete.frame_start
        end_frame_anim = scene_complete.frame_end + 1
        clear_blend_file = path_model_file.replace(".blend", "")
        file_path_current_object = f'{clear_blend_file}\\SAF_CONVERT\\'
        try:
            os.makedirs(file_path_current_object, exist_ok=True)
        except OSError:
            error_folder = f'Can\'t create the folder, permission denied'
            print(error_folder)
        object_level = []
        for obj in bpy.context.scene.objects:
            frame_level = []
            if obj.type == 'MESH':
                for current_frame in range(start_frame_anim, end_frame_anim):
                    next_frame = scene_complete.frame_set(current_frame)
                    # LOCATIONS AND ROTATIONS ARE FLOAT
                    loc_x = obj.location[0] * 1000 # LOC X
                    loc_y = obj.location[1] * 1000 # LOC Y
                    loc_z = obj.location[2] * 1000 # LOC Z
                    rot_x = math.degrees(obj.rotation_euler[0] * round((4096/360), 12)) # ROT X
                    rot_y = math.degrees(obj.rotation_euler[1] * round((4096/360), 12)) # ROT Y
                    rot_z = math.degrees(obj.rotation_euler[2] * round((4096/360), 12)) # ROT Z
                    round_loc_x = int(round(loc_x, ndigits=1))
                    round_loc_y = int(round(loc_y, ndigits=1))
                    round_loc_z = int(round(loc_z, ndigits=1))
                    round_rot_x = int(round(rot_x, ndigits=1))
                    round_rot_y = int(round(rot_y, ndigits=1))
                    round_rot_z = int(round(rot_z, ndigits=1))
                    all_transforms = round_rot_x, round_rot_y, round_rot_z, round_loc_x, round_loc_y, round_loc_z
                    frame_level.append(all_transforms)
            object_level.append(frame_level)
        saf_pre_converted = []
        for new_current_frame in range(start_frame_anim, end_frame_anim):
            for num_obj in range(0, len(object_level)):
                object_to_look = object_level[num_obj] # GETTING INTO THE ARRAY OF THE DESIRED OBJECT
                frame_to_look = object_to_look[new_current_frame] # GETTING THE ARRAY IN THIS CURRENT FRAME
                saf_pre_converted.append(frame_to_look)
        
        saf_to_bytes = []
        for saf_raw in saf_pre_converted:
            for saf_r in saf_raw:
                integers_to_bytes = saf_r.to_bytes(length=2, byteorder='little', signed=True)
                saf_to_bytes.append(integers_to_bytes)
        joined_bytes = b''.join(saf_to_bytes)
        
        with open(file_path_current_object + f'Converted.saf', 'wb') as write_saf:
            length_block_calc = (scene_complete.frame_end + 1) * 2
            saf_header = b'\x0C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            saf_num_obj = len(object_level).to_bytes(length=2, byteorder='little', signed=False)
            saf_number_transforms = length_block_calc.to_bytes(length=2, byteorder='little', signed=False)
            saf_header_complete = saf_header + saf_num_obj + saf_number_transforms
            non_list_bytes = bytes(joined_bytes)
            final_bytes = saf_header_complete + non_list_bytes
            write_saf.write(final_bytes)
        
        return {'FINISHED'}


classes = (BLEND2SAF_PT_blend2saf, CONVERTSAF_OT_convert_saf)

register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()