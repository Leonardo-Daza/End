# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from math import radians
from math import degrees

def bracket_open(fileOut):
    fileOut.write('\n{')
    
def bracket_close(fileOut):
    fileOut.write('\n}')

#convert floats to string
#used for the purposes of exporting
#adds delimiter between each float, but not after the last float
#also works with ints and bools, sets bools to 0 or 1
def f_to_str(rf, dl, *infloats):
    stringOut = ''
    for infloat in infloats[:-1]:
        stringOut = stringOut + str(round(infloat, rf)) + dl
    stringOut = stringOut + str(round(infloats[-1], rf))
    return stringOut

def write_data(fileOut, stringOut):
    fileOut.write('\n')
    fileOut.write(stringOut)

def export_End3D(filePath, fileName):
    _rf = 6 #round float to decimal places
    _dl = '\t' #delimiter character
    _eq = '=' #equals character
    _ew = 'w' #equals character for weights
    _fileOut = open(r'' + filePath + fileName,'w')
    print('Writing to: ' + filePath + fileName)

    for obj in bpy.context.selected_objects:
        print('Parsing ' + obj.name)
        _fileOut.write('\n' + obj.type + '=' + obj.name)
        bracket_open(_fileOut)
        write_data(_fileOut, 'pos=' + f_to_str(_rf, _dl, obj.location.x, obj.location.y, obj.location.z))
        write_data(_fileOut, 'rot=' + f_to_str(_rf, _dl, degrees(obj.rotation_euler.x), degrees(obj.rotation_euler.y), degrees(obj.rotation_euler.z)))
        write_data(_fileOut, 'scale=' + f_to_str(_rf, _dl, obj.scale.x, obj.scale.y, obj.scale.z))
        
        ##########################export # mesh##########################
        if str(obj.type) == "MESH":
            #export vertices
            write_data(_fileOut, 'verts=')
            bracket_open(_fileOut)
            for vert in obj.data.vertices:
                write_data(_fileOut, f_to_str(_rf, _dl, vert.co.x, vert.co.y, vert.co.z))
            bracket_close(_fileOut)
            
            #export faces
            write_data(_fileOut, 'faces=')
            bracket_open(_fileOut)
            for face in obj.data.polygons:
                _fileOut.write('\n')
                for vertID in face.vertices[:-1]:
                    _fileOut.write(str(vertID) + _dl)
                _fileOut.write(str(face.vertices[-1]))
            bracket_close(_fileOut)
            
            #export normals
            write_data(_fileOut, 'normals=')
            bracket_open(_fileOut)
            for vert in obj.data.vertices:
                write_data(_fileOut, f_to_str(_rf, _dl, vert.normal.x, vert.normal.y, vert.normal.z))
            bracket_close(_fileOut)
            
            #export uvs
            #data saved as faceID, vertID, u, v
            write_data(_fileOut, 'uvs=')
            bracket_open(_fileOut)
            for face in obj.data.polygons:
                for vertID, loopID in zip(face.vertices, face.loop_indices):
                    uv = obj.data.uv_layers.active.data[loopID].uv #easier to read output line
                    write_data(_fileOut, f_to_str(_rf, _dl, face.index, vertID, uv.x, uv.y))
            bracket_close(_fileOut)
            
            #export groups
            write_data(_fileOut, 'groups=')
            bracket_open(_fileOut)
            for vGroup in obj.vertex_groups:
                write_data(_fileOut, vGroup.name)
            bracket_close(_fileOut)
            
            #export weights
            write_data(_fileOut, 'weights=')
            bracket_open(_fileOut)
            for vert in obj.data.vertices:
                _fileOut.write('\n')
                #for group in vert.groups[:-1]:
                    #if (group.weight != 0.0):
                        #_fileOut.write(str(group.group) + _ew + f_to_str(_rf, _dl, group.weight) + _dl )
                gID = 0
                while gID < (len(vert.groups)):
                    groupAdded = 0
                    if (vert.groups[gID].weight != 0.0):
                        _fileOut.write(str(vert.groups[gID].group) + _ew + f_to_str(_rf, _dl, vert.groups[gID].weight))
                        groupAdded = 1
                    if (gID+1) < (len(vert.groups)):
                        print('gID = ' + str(gID+1) + '\tlen(vert.groups) = ' +  str(len(vert.groups)))
                        if (vert.groups[gID+1].weight == 0.0):
                            gID += 1
                    gID += 1
                    if (groupAdded):
                        if gID < (len(vert.groups)):
                            _fileOut.write(_dl)
                        
            bracket_close(_fileOut)
            
            #export modifiers
            write_data(_fileOut, 'modifiers=' + str(len(obj.modifiers)))
            bracket_open(_fileOut)
            for modifier in obj.modifiers:
                write_data(_fileOut, 'type=' + modifier.type)
                bracket_open(_fileOut)
                write_data(_fileOut, 'name=' + (modifier.name))

                #if MIRROR
                if str(modifier.type) == 'MIRROR':
                    write_data(_fileOut, 'axis=' + f_to_str(_rf, _dl, modifier.use_axis[0], modifier.use_axis[1], modifier.use_axis[2]))
                    write_data(_fileOut, 'bisect=' + f_to_str(_rf, _dl, modifier.use_bisect_axis[0], modifier.use_bisect_axis[1], modifier.use_bisect_axis[2]))
                    write_data(_fileOut, 'flip=' + f_to_str(_rf, _dl, modifier.use_bisect_flip_axis[0], modifier.use_bisect_flip_axis[1], modifier.use_bisect_flip_axis[2]))
                    write_data(_fileOut, 'mirror_object=' + str(modifier.mirror_object))
                    write_data(_fileOut, 'clipping=' + str(int(modifier.use_clip)))
                    write_data(_fileOut, 'merge=' + f_to_str(_rf, _dl, modifier.use_mirror_merge, modifier.merge_threshold))
                    write_data(_fileOut, 'bisect_distance=' + f_to_str(_rf, _dl, modifier.bisect_threshold))
                    write_data(_fileOut, 'mirror_u=' + f_to_str(_rf, _dl, modifier.use_mirror_u, modifier.mirror_offset_u))
                    write_data(_fileOut, 'mirror_v=' + f_to_str(_rf, _dl, modifier.use_mirror_v, modifier.mirror_offset_v))
                    write_data(_fileOut, 'offset=' + f_to_str(_rf, _dl, modifier.offset_u, modifier.offset_v))
                    write_data(_fileOut, 'vertex_groups=' + f_to_str(_rf, _dl, modifier.use_mirror_vertex_groups))
                    write_data(_fileOut, 'flip_udim=' + f_to_str(_rf, _dl, modifier.use_mirror_udim))
                    
                #if ARMATURE
                elif str(modifier.type) == 'ARMATURE':
                    write_data(_fileOut, 'object=' + str(modifier.object.name))
                    write_data(_fileOut, 'vertex_group=' + str(modifier.vertex_group))
                    write_data(_fileOut, 'preserve_volume=' + f_to_str(_rf, _dl, modifier.use_deform_preserve_volume))
                    write_data(_fileOut, 'multi_modifier=' + f_to_str(_rf, _dl, modifier.use_multi_modifier))
                    write_data(_fileOut, 'bind_to_vertex_groups=' + f_to_str(_rf, _dl, modifier.use_vertex_groups))
                    write_data(_fileOut, 'bind_to_bone_envelopes=' + f_to_str(_rf, _dl, modifier.use_bone_envelopes))
                    
                bracket_close(_fileOut)
                
            bracket_close(_fileOut)
        
        ##########################export # bone##########################
        elif str(obj.type) == "ARMATURE":
            
            #setup for edit mode
            view_layer = bpy.context.view_layer.objects.active = obj
            edit_bones = obj.data.edit_bones
            #switch to edit mode
            bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
            
            #export bones
            write_data(_fileOut, 'bones=')
            bracket_open(_fileOut)
            for bone in obj.data.bones:
                
                write_data(_fileOut, 'bname=' + bone.name)
                bracket_open(_fileOut)
                
                #transform
                write_data(_fileOut, 'head=' + f_to_str(_rf, _dl, bone.head_local[0], bone.head_local[1], bone.head_local[2]))
                write_data(_fileOut, 'tail=' + f_to_str(_rf, _dl, bone.tail_local[0], bone.tail_local[1], bone.tail_local[2]))
                write_data(_fileOut, 'head_radius=' + f_to_str(_rf, _dl, edit_bones[bone.name].head_radius))
                write_data(_fileOut, 'tail_radius=' + f_to_str(_rf, _dl, edit_bones[bone.name].tail_radius))
                write_data(_fileOut, 'roll=' + f_to_str(_rf, _dl, degrees(edit_bones[bone.name].roll)))
                write_data(_fileOut, 'length=' + f_to_str(_rf, _dl, edit_bones[bone.name].length))
                write_data(_fileOut, 'envelope=' + f_to_str(_rf, _dl, edit_bones[bone.name].envelope_distance))
                
                #bendy bones not implemented

                #relations
                layerActive = 0
                layerChecked = 0
                for layer in bone.layers:
                    if layer == True:
                        layerActive = layerChecked
                        break
                    layerChecked += 1
                write_data(_fileOut, 'layer=' + f_to_str(_rf, _dl, layerActive))
                write_data(_fileOut, 'parent=' + str(getattr(bone.parent, "name", "None")))
                write_data(_fileOut, 'connected=' + f_to_str(_rf, _dl, bone.use_connect))
                write_data(_fileOut, 'local_location=' + f_to_str(_rf, _dl, bone.use_local_location))
                write_data(_fileOut, 'inherit_rotation=' + f_to_str(_rf, _dl, bone.use_inherit_rotation))
                write_data(_fileOut, 'inherit_scale=' + str(bone.inherit_scale))
                
                #deform
                write_data(_fileOut, 'envelope_distance=' + f_to_str(_rf, _dl, bone.envelope_distance))
                write_data(_fileOut, 'envelope_weight=' + f_to_str(_rf, _dl, bone.envelope_weight))
                write_data(_fileOut, 'envelope_multiply=' + f_to_str(_rf, _dl, bone.use_envelope_multiply))
                
                #pose data
                write_data(_fileOut, 'rotation=' + f_to_str(_rf, _dl, degrees(bone.matrix.to_euler()[0]), degrees(bone.matrix.to_euler()[1]), degrees(bone.matrix.to_euler()[2])))
                write_data(_fileOut, 'rotation_local=' + f_to_str(_rf, _dl, degrees(bone.matrix_local.to_euler()[0]), degrees(bone.matrix_local.to_euler()[1]), degrees(bone.matrix_local.to_euler()[2])))
                
                poseBone = obj.pose.bones[bone.name]
                write_data(_fileOut, 'rotation_pose=' + f_to_str(_rf, _dl, (poseBone.rotation_euler[0]), (poseBone.rotation_euler[1]), (poseBone.rotation_euler[2])))
                
                #constraints
                write_data(_fileOut, 'constraints=' + str(len(obj.pose.bones[bone.name].constraints)))
                bracket_open(_fileOut)
                for constraint in obj.pose.bones[bone.name].constraints:
                    write_data(_fileOut, 'type=' + constraint.type)
                    bracket_open(_fileOut)
                    write_data(_fileOut, 'cname=' + (constraint.name))
                    
                    #IK
                    if constraint.type == 'IK':
                        write_data(_fileOut, 'target=' + constraint.target.name)
                        write_data(_fileOut, 'subtarget=' + constraint.subtarget)
                        write_data(_fileOut, 'pole_target=' + constraint.pole_target.name)
                        write_data(_fileOut, 'pole_subtarget=' + constraint.pole_subtarget)
                        write_data(_fileOut, 'pole_angle=' + f_to_str(_rf, _dl, constraint.pole_angle))
                        write_data(_fileOut, 'iterations=' + f_to_str(_rf, _dl, constraint.iterations))
                        write_data(_fileOut, 'chain_length=' + f_to_str(_rf, _dl, constraint.chain_count))
                        write_data(_fileOut, 'use_tail=' + f_to_str(_rf, _dl, constraint.use_tail))
                        write_data(_fileOut, 'stretch=' + f_to_str(_rf, _dl, constraint.use_stretch))
                        write_data(_fileOut, 'weight_position=' + f_to_str(_rf, _dl, constraint.use_location, constraint.weight))
                        write_data(_fileOut, 'weight_rotation=' + f_to_str(_rf, _dl, constraint.use_rotation, constraint.orient_weight))
                        write_data(_fileOut, 'influence=' + f_to_str(_rf, _dl, constraint.influence))
                    
                    #Copy Rotation
                    if constraint.type == 'COPY_ROTATION':
                        write_data(_fileOut, 'target=' + constraint.target.name)
                        write_data(_fileOut, 'subtarget=' + constraint.subtarget)
                        write_data(_fileOut, 'order=' + constraint.euler_order)
                        write_data(_fileOut, 'axis=' + f_to_str(_rf, _dl, constraint.use_x, constraint.use_y,constraint.use_z))
                        write_data(_fileOut, 'invert=' + f_to_str(_rf, _dl, constraint.invert_x, constraint.invert_y,constraint.invert_z))
                        write_data(_fileOut, 'mix_mode=' + constraint.mix_mode)
                        write_data(_fileOut, 'target_space=' + constraint.target_space)
                        write_data(_fileOut, 'owner_space=' + constraint.owner_space)
                        write_data(_fileOut, 'influence=' + f_to_str(_rf, _dl, constraint.influence))
                    bracket_close(_fileOut)
                bracket_close(_fileOut)
                bracket_close(_fileOut)

            # exit edit mode
            bpy.ops.object.mode_set(mode='OBJECT') 
            bracket_close(_fileOut)
        
        #################################################################
        bracket_close(_fileOut)
        print('Finished parsing ' + obj.name)
        
    _fileOut.close()
    print('Finished writting ' + fileName)
    
    return {'FINISHED'}

def export_EndAnim(filePath, fileName):
    _rf = 6 #round float to decimal places
    _dl = '\t' #delimiter character
    _eq = '=' #equals character
    _fileOut = open(r'' + filePath + fileName,'w')
    print('Writing to: ' + filePath + fileName)
    
    for obj in bpy.context.selected_objects:
        if str(obj.type) == "ARMATURE":
            if obj.animation_data is not None:
                write_data(_fileOut, 'ARMATURE=' + obj.name)
                bracket_open(_fileOut)
                write_data(_fileOut, 'fps=' + str(bpy.context.scene.render.fps))
                write_data(_fileOut, 'fpsbase=' + str(bpy.context.scene.render.fps_base))
                
                for action in bpy.data.actions:
                    if action is not None:
                        obj.animation_data.action = action
                        #make sure that there are keyframes before adding action
                        if len(action.fcurves) > 0 and len(action.fcurves[0].keyframe_points) > 0:
                            write_data(_fileOut, 'action=' + action.name)
                            bracket_open(_fileOut)
                            frameStart, frameEnd = [int(x) for x in action.frame_range]
                            write_data(_fileOut, 'start=' + f_to_str(_rf, _dl, frameStart))
                            write_data(_fileOut, 'end=' + f_to_str(_rf, _dl, frameEnd))
                            
                            #get keyframes
                            keyframes = list()
                            for kfp in action.fcurves[0].keyframe_points:
                                keyframes.append(int(kfp.co[0]))

                            #write all keyframes in the same line
                            keyframeData = ''
                            for keyframe in keyframes[:-1]:
                                keyframeData = keyframeData + f_to_str(_rf, _dl, keyframe) + _dl
                            keyframeData = keyframeData + f_to_str(_rf, _dl, keyframes[-1])
                            write_data(_fileOut, 'keyframes=' + keyframeData)
                            
                            for keyframe in keyframes:
                                bpy.context.scene.frame_set(keyframe)
                                write_data(_fileOut, 'keyframe=' + f_to_str(_rf, _dl, keyframe))
                                bracket_open(_fileOut)
                                
                                #write bone data
                                for bone in obj.pose.bones:
                                    write_data(_fileOut, 'bone=' + bone.name)
                                    bracket_open(_fileOut)
                                    #y and z are flipped for bone position
                                    write_data(_fileOut, 'pos=' + f_to_str(_rf, _dl, bone.location[0], -bone.location[2], bone.location[1]))
                                    write_data(_fileOut, 'rot=' + f_to_str(_rf, _dl, (bone.rotation_euler[0]), (bone.rotation_euler[1]), (bone.rotation_euler[2])))
                                    write_data(_fileOut, 'sca=' + f_to_str(_rf, _dl, bone.scale[0], bone.scale[1], bone.scale[2]))
                                    bracket_close(_fileOut)
                                bracket_close(_fileOut)
                            bracket_close(_fileOut)
                bracket_close(_fileOut)
    _fileOut.close()
    print('Finished writting ' + fileName)
    return {'FINISHED'}
