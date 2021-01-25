# ##### BEGIN MIT LICENSE BLOCK #####
#
# MIT License
#
# Copyright (c) 2021 David Barnes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ##### END MIT LICENSE BLOCK #####

import bpy

from math import radians

#def lightmap_bulk(context, res_x, res_y, fix_rotation):

save_directory = 'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\data\\scenarios\\multi\\dam_defense\\auto_baked'
index_mapping_txt_path = 'C:\\Program Files (x86)\\Microsoft Games\Halo 2 Map Editor\\data\\scenarios\\multi\\dam_defense\\dam_defense.bitmap_mapping.txt'
bitmap_tag_edit_path = 'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\tags\\scenarios\\multi\\dam_defense\\dam_defense_dam_defense_lightmap_truecolor_bitmaps'

h2tool_path = 'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\'

'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\data\\scenarios\\multi\\dam_defense\\auto_baked'
'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\data\\scenarios\\multi\\halo\\coagulation\\auto_baked'
'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\data\\scenarios\\multi\\room_test\\auto_baked'



f=open(index_mapping_txt_path,"r")
lines=f.readlines()

obj_dict = {}

for line in lines:
    line_split = line.rstrip('\n').split('\t')
    obj_dict[line_split[0]] = line_split
f.close()

#res_x = 256
#res_y = 256
bake_res_scale = 16
post_bake_res_scale = 0.0625
use_denoise = True
run_h2codez_bitmap_edit = True
apply_gamma = 1.0
apply_view_transform = 'Filmic'
apply_look = 'Very High Contrast'
apply_exposure = -1

scene = bpy.context.scene
if use_denoise is True:
    scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '32'
    file_extension = '.exr'
    scene.view_settings.view_transform = 'Raw'
    scene.view_settings.look = 'None'
    scene.view_settings.gamma = 1.0
    scene.view_settings.exposure = 0
else:
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '16'
    file_extension = '.png'
object_list = list(scene.objects)
bake_from_obj = bpy.context.view_layer.objects.active


#scene_collection = bpy.context.view_layer.layer_collection
#bpy.context.view_layer.active_layer_collection = scene_collection
#bpy.ops.object.mode_set(mode='OBJECT')
#print('\Configuring default bake settings to be used for all meshes...')
#bake_settings = bpy.types.BakeSettings
#bake_settings.use_pass_diffuse = True
#bake_settings.use_selected_to_active = True
#bake_settings.use_pass_direct = True
#bake_settings.use_pass_indirect = True
#bake_settings.use_pass_color = False

bpy.ops.object.select_all(action='DESELECT')
name_list = []
print('Starting...\n')
for obj in bpy.data.collections['lightmap'].objects:
    obj.hide_render = True
for obj in bpy.data.collections['lightmap'].objects:
    try:
        res_x = int(obj_dict[obj.name][2]) * float(bake_res_scale)
        res_y = int(obj_dict[obj.name][3]) * float(bake_res_scale)
        
        print(obj_dict[obj.name][2])
        print(obj_dict[obj.name][3])
    except:
        res_x = 32
        res_y = 32
    #obj_collection = bpy.context.view_layer.layer_collection.children[-1]
    #bpy.context.view_layer.active_layer_collection = obj_collection
    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_render = False
    print('\n\nCluster/Instance Object: ' + obj.name)
    #obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    uv1 = obj.data.uv_layers[1].name
    obj.data.uv_layers.active = obj.data.uv_layers[uv1]
    print('Remoiving materials from ' + obj.name)
    for material in obj.material_slots:
        for i in range(len(obj.material_slots)):
            obj.active_material_index = i
            bpy.ops.object.material_slot_remove()
    print('Finished removing all materials from ' + obj.name)
    bpy.ops.object.material_slot_add()
    print('\nSetting up materials for ' + obj.name)
    try:
         mat = bpy.data.materials[obj.name]
         obj.data.materials[0] = mat
    except:
        mat = bpy.data.materials.new(name=obj.name)
        obj.data.materials[0] = mat
    #obj.material_slots[0] = mat
    mat.use_nodes = True
    #tex_node = None
    #uv_node = None

            

    #if uv_node is None:
    #if True:
    uv_node = mat.node_tree.nodes.new('ShaderNodeUVMap')
        #
        #if tex_node is None:
    try:
        if bpy.data.images[obj.name] is not None:
            bpy.data.images.remove(bpy.data.images[obj.name])
    except:
        pass
    if use_denoise is True:
        lightmap_image = bpy.data.images.new(obj.name, res_x, res_y, alpha=True, float_buffer=True, stereo3d=False, is_data=False, tiled=False)
        #lightmap_image.alpha_mode = 'PREMUL'
        #lightmap_image.is_float = True
        lightmap_image.colorspace_settings.name = 'Raw'
    else:
        lightmap_image = bpy.data.images.new(obj.name, res_x, res_y, alpha=True, float_buffer=False, stereo3d=False, is_data=False, tiled=False)
        #lightmap_image.alpha_mode = 'PREMUL'
        #lightmap_image.is_float = True
        lightmap_image.colorspace_settings.name = 'sRGB'
    if lightmap_image is None:
        lightmap_image = bpy.data.images.new(obj.name, res_x, res_y)
    for node in mat.node_tree.nodes:
        #print(node.type)
        if node.type == 'TEX_IMAGE':
            if node.image == lightmap_image:
                mat.node_tree.nodes.remove(node)
            mat.node_tree.nodes.remove(node)
        elif node.type == 'UVMAP':
            mat.node_tree.nodes.remove(node)
        #if node.type ==       
    uv_node = mat.node_tree.nodes.new('ShaderNodeUVMap')
    tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_node.image = lightmap_image
    tex_node.select = True
    mat.node_tree.links.new(uv_node.outputs['UV'], tex_node.inputs['Vector'])

    uv_node.uv_map = uv1
    #for all_obj in bpy.data.collections['lightmap'].all_objects:
    #    print(all_obj.type)
    #    all_obj.hide_render = True
    #obj.hide_render = False
    mat.node_tree.nodes.active = tex_node
    print('Materials set up for ' + obj.name)
    
    
    bake_from_obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    if use_denoise is True:
        print('\nBeginning normal texture bake for object ' + obj.name + '!')
        bpy.ops.object.bake(type='NORMAL', save_mode='EXTERNAL')
        print('Normal texture baking complete for ' + obj.name + '!')
        print('\nSaving normal texture for ' + obj.name)
        normal_save_path = save_directory + '\\auto_baked_normal\\' + obj.name + file_extension
        lightmap_image.save_render(normal_save_path, scene = None)
        print('Image saved successfully to ' + normal_save_path)
        name_list.append(obj.name)
        
    
    print('\nBeginning diffuse texture bake for object ' + obj.name + '!')
    bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
    print('Diffuse texture baking complete for ' + obj.name + '!')
    print('\nSaving diffuse texture for ' + obj.name)
    color_save_path = save_directory + '\\auto_baked_color\\' + obj.name + file_extension
    lightmap_image.save_render(color_save_path, scene = None)
    print('Image saved successfully to ' + color_save_path)
    
    for node in mat.node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL':
            output_node = node
    mat.node_tree.links.new(tex_node.outputs['Color'], output_node.inputs['Surface'])
    #for other_obj in bpy.data.collections['lightmap'].all_objects:
    #    other_obj.hide_render = False
    #bpy.ops.object.select_all(action='DESELECT')
    #bpy.context.view_layer.objects.active = None
    obj.hide_render = True
    
#for obj in bpy.data.collections['lightmap'].objects:
#    obj.hide_render = False
for obj in bpy.data.collections['lightmap'].objects:
    obj.hide_render = False
bpy.context.view_layer.objects.active = bake_from_obj

if use_denoise is True:
    print('\nStarting Denoising...')
    origin_scene = bpy.context.scene
    denoise_scene = bpy.data.scenes.new(name='Denoise_Scene')
    bpy.context.window.scene = denoise_scene
    denoise_scene.render.image_settings.file_format = 'PNG'
    denoise_scene.render.image_settings.color_mode = 'RGBA'
    denoise_scene.render.image_settings.color_depth = '16'
    denoise_scene.view_settings.view_transform = apply_view_transform
    denoise_scene.view_settings.look = apply_look
    denoise_scene.view_settings.gamma = apply_gamma
    denoise_scene.view_settings.exposure = apply_exposure

    denoise_scene.use_nodes = True
    comp_tree = denoise_scene.node_tree
    for node in comp_tree.nodes:
        comp_tree.nodes.remove(node)
    
    
    color_image_node = comp_tree.nodes.new(type='CompositorNodeImage')

    normal_image_node = comp_tree.nodes.new(type='CompositorNodeImage')

    denoise_node = comp_tree.nodes.new(type='CompositorNodeDenoise')
    #gamma_node = comp_tree.nodes.new(type='CompositorNodeGamma')
    #gamma_node.inputs['Gamma'].default_value = gamma
    
    scale_node = comp_tree.nodes.new(type='CompositorNodeTransform')
    scale_node.filter_type = 'BICUBIC'
    scale_node.inputs[4].default_value = float(post_bake_res_scale)
    
    composite_node = comp_tree.nodes.new(type='CompositorNodeComposite')
    #file_output_node = comp_tree.nodes.new(type='CompositorNodeOutputFile')

    
    comp_tree.links.new(color_image_node.outputs['Image'], denoise_node.inputs['Image'])
    comp_tree.links.new(normal_image_node.outputs['Image'], denoise_node.inputs['Normal'])
    comp_tree.links.new(denoise_node.outputs['Image'], scale_node.inputs['Image'])
    comp_tree.links.new(scale_node.outputs['Image'], composite_node.inputs['Image'])

    for obj_name in name_list:
        try:
            denoise_scene.render.resolution_x = float(obj_dict[obj_name][2]) * bake_res_scale * float(post_bake_res_scale)
            denoise_scene.render.resolution_y = float(obj_dict[obj_name][3]) * bake_res_scale * float(post_bake_res_scale)
            print(denoise_scene.render.resolution_x)
            print(denoise_scene.render.resolution_y)
        except:
            print('except')
            denoise_scene.render.resolution_x = 32
            denoise_scene.render.resolution_y = 32
        denoise_save_path =  save_directory + '\\denoised\\' + obj_name + '.png'
        
        color_image_path = save_directory + '\\' + 'auto_baked_color\\' + obj_name + file_extension
        color_image_node.image = bpy.data.images.load(color_image_path)
        color_image_node.image.use_half_precision = False

        normal_image_path = save_directory + '\\' + 'auto_baked_normal\\' + obj_name + file_extension
        normal_image_node.image = bpy.data.images.load(normal_image_path)
        normal_image_node.image.use_half_precision = False
        print('\nDenoising and compositing for ' + obj_name)
        bpy.ops.render.render()
        print('Saving denoised image under ' + denoise_save_path)
        bpy.data.images['Render Result'].save_render(denoise_save_path, scene = None)

    bpy.context.window.scene = origin_scene
    bpy.data.scenes.remove(denoise_scene) 
    
print('Finished Denosing')

if run_h2codez_bitmap_edit is True:
    from os import system

    def cmd_run(com):
        com_run_str = 'cmd /c '
        system(com_run_str + '"' + com + '"')

    def h2tool_run(com):
        print(h2tool_path)
        print(com)
        cmd_run('"' + h2tool_path + 'h2tool.exe" ' + com)

    if use_denoise is True:
        replacement_image_path = save_directory + '\\denoised\\'
    else:
        replacement_image_path = save_directory + '\\auto_baked_color\\'

    for name in name_list:
        try:
            h2tool_run('edit-bitmap' + ' ' +
            '"' + bitmap_tag_edit_path + '" ' +
            obj_dict[name][1] + ' ' +
            '"' + replacement_image_path +
            name +
            '.PNG' + '"')
        except:
            pass

print('Finished!')
