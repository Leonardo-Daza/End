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
import bmesh
from math import radians
from math import degrees
from mathutils import Euler

def remove_whitespace(lineIn):
    lineOut = lineIn
    while (lineOut[0] == '\t'):
        lineOut = lineOut[1:]
    if (lineOut[-1] == '\n'):
        lineOut = lineOut[:-1]
    return lineOut
        
def unpack_floats(inString, dl):
    outData = list()
    separateString = inString.split(dl)
    
    for data in separateString:
        outData.append(float(data))
    return outData

def unpack_int_float(inString, dl):
    outData = list()
    separateString = inString.split(dl)
    outData.append(int(separateString[0]))
    outData.append(float(separateString[1]))
    return outData

def unpack_ints(inString, dl):
    outData = list()
    separateString = inString.split(dl)
    
    for data in separateString:
        outData.append(int(data))
    return outData

##########script start##########
def import_End3D(filePath, fileName):
    #####declare variables####
    _bc = 0 #bracket count, used to denote values within a value
    _rf = 6 #round float to decimal places
    _dl = '\t' #delimiter character
    _eq = '=' #equals character
    _ew = 'w' #equals character for weights

    _fileIn = open(filePath + fileName)
    #####read entire file#####
    print('Reding from: ' + fileName)
    _rawFile = _fileIn.readlines()
    _fileIn.close()
    _parsedFile = list()
    _parsedKeywords = list()
    _parsedRawValues = list()
    print('\tFinished reading ' + fileName)


    #####parse file#####
    print ('\tParsing ' + fileName)

    #remove whitespace at beginning and end of line
    for rawLine in _rawFile:
        parsedLine = remove_whitespace(rawLine)
        
    #separate keywords and values
        charCount = 0
        for parsedChar in parsedLine:
            if parsedChar == _eq:
                break
            charCount += 1
            
        keyword = parsedLine[:charCount]
        rawValue = parsedLine[charCount+1:]
        
        _parsedKeywords.append(keyword)
        _parsedRawValues.append(rawValue)

    #create list of lists of the data structure
    #data in list is listed as follows:
    #each list contains 3 items
    #item 1 is the id of {
    #item 2 is the id of }
    #item 3 is the count of how deep the bracket list is
    _dataStructure = list()
    _bc = 0
    for id, keyword in enumerate(_parsedKeywords):
        
        if keyword == '{':
            dataList = list()
            dataList.append(id)
            _dataStructure.append(dataList)
            _bc += 1
        elif keyword == '}':
            _bc -= 1
            for i in range(len(_dataStructure))[::-1]:
                if (len(_dataStructure[i]) < 2):
                    _dataStructure[i].append(id)
                    _dataStructure[i].append(_bc)
                    break

    #create mesh or bone; add modifier or constraint; or modify parameter
    dsID = 0 #data structure id
    # make collection to store meshes and armatures
    srcCollection = bpy.data.collections.new(fileName)
    bpy.context.scene.collection.children.link(srcCollection)

    _objModList = list()
        
    while(dsID < len(_dataStructure)):

        #find the last data structure list in the mesh/armature
        dsLastID = dsID #last id for this block of data
        for id in range(dsID+1, len(_dataStructure)):
            if _dataStructure[id][2] == 0:
                dsLastID = id - 1
                break
            if id == len(_dataStructure) -1:
                dsLastID = id
                break
        
        print('\t\tCreating ' + _parsedKeywords[_dataStructure[dsID][0]-1] + ' ' + _parsedRawValues[_dataStructure[dsID][0]-1])  
        
        ########################## if mesh ##########################
        if _parsedKeywords[_dataStructure[dsID][0]-1] == 'MESH':
            
            # make mesh
            mesh = bpy.data.meshes.new(_parsedRawValues[_dataStructure[dsID][0]-1])
            # make object from mesh
            obj = bpy.data.objects.new(_parsedRawValues[_dataStructure[dsID][0]-1], mesh)
            # add object to scene collection
            srcCollection.objects.link(obj)
            
            #update mesh values
            vertices = list()
            edges = []
            faces = list()
            normals = list()
            uvs = list()
            groups = list()
            weights = list()
            modifiers = list()
            idDsId = dsID
            id = _dataStructure[idDsId][0]
            while (id < _dataStructure[idDsId][1]):
                if _parsedKeywords[id] == 'pos':
                    obj.location = unpack_floats(_parsedRawValues[id], _dl)
                elif _parsedKeywords[id] == 'rot':
                    rRad = unpack_floats(_parsedRawValues[id], _dl)
                    for i in range(3):
                        obj.rotation_euler[i] = radians(rRad[i])
                elif _parsedKeywords[id] == 'scale':
                    obj.scale = unpack_floats(_parsedRawValues[id], _dl)
                #for lists of data, find data structure and get values in the range
                elif _parsedKeywords[id] == 'verts':
                    dsID += 1
                    id += 2
                    while (id < _dataStructure[dsID][1]):
                        vertices.append(unpack_floats(_parsedKeywords[id], _dl))
                        id += 1
                elif _parsedKeywords[id] == 'faces':
                    dsID += 1
                    id += 2
                    while (id < _dataStructure[dsID][1]):
                        faces.append(unpack_ints(_parsedKeywords[id], _dl))
                        id += 1
                elif _parsedKeywords[id] == 'normals':
                    dsID += 1
                    id += 2
                    while (id < _dataStructure[dsID][1]):
                        normals.append(unpack_floats(_parsedKeywords[id], _dl))
                        id += 1
                elif _parsedKeywords[id] == 'uvs':
                    dsID += 1
                    id += 2
                    while (id < _dataStructure[dsID][1]):
                        uvs.append(unpack_floats(_parsedKeywords[id], _dl))
                        id += 1
                elif _parsedKeywords[id] == 'groups':
                    dsID += 1
                    id += 2
                    while (id < _dataStructure[dsID][1]):
                        groups.append(_parsedKeywords[id])
                        id += 1
                elif _parsedKeywords[id] == 'weights':
                    dsID += 1
                    id += 2
                    while (id < _dataStructure[dsID][1]):
                        weights.append(_parsedKeywords[id])
                        id += 1
                elif _parsedKeywords[id] == 'modifiers':
                    dsID += 1
                    for modifierCount in range(dsID, dsLastID):
                        dsID += 1
                        #add modifier data
                        modifier = list()
                        modifier.append(_dataStructure[dsID][0] - 1)
                        id += 2
                        while (id < _dataStructure[dsID][1]):
                            modifier.append(id)
                            id += 1
                        modifiers.append(modifier)
                id += 1        
            #set the new vert and face data
            mesh.from_pydata(vertices, edges, faces)
            mesh.update()
            #TODO: test if normals are, in fact, imported properly
            obj.data.use_auto_smooth = True
            for vert in obj.data.vertices:
                obj.data.normals_split_custom_set_from_vertices(normals)
            
            #uvs
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode = 'EDIT')
            bm = bmesh.from_edit_mesh(obj.data)
            uvLayer = bm.loops.layers.uv.verify()
            loopCount = 0
            for uv in uvs:
                uvData = [uv[2],uv[3]]
                bm.faces.ensure_lookup_table()
                bm.faces[int(uv[0])].loops[loopCount][uvLayer].uv = uvData
                loopCount += 1
                loopCount %= 4
            bmesh.update_edit_mesh(obj.data)
            bpy.ops.object.mode_set(mode = 'OBJECT')                
            
            #groups
            for group in groups:
                obj.vertex_groups.new(name=group)
                
            #weights
            for id, weight in enumerate(weights):
                wValues = weight.split(_dl)
                for wValue in wValues:
                    idW = wValue.split(_ew)
                    idA = list()
                    idA.append(id)
                    obj.vertex_groups[int(idW[0])].add(idA, float(idW[1]), 'REPLACE')
            
            #add object and modifier list to be added
            #after all objects and armatures are added to the scene
            objMod = list()
            objMod.append(obj)
            objMod.append(modifiers)
            _objModList.append(objMod)
            
        ######################## if armature ########################
        if _parsedKeywords[_dataStructure[dsID][0]-1] == 'ARMATURE':
            
            armature = bpy.data.armatures.new(_parsedRawValues[_dataStructure[dsID][0]-1])
            arm_obj = bpy.data.objects.new(_parsedRawValues[_dataStructure[dsID][0]-1], armature)
            srcCollection.objects.link(arm_obj)
                    
            #set armature to edit mode to add bones
            view_layer = bpy.context.view_layer.objects.active = arm_obj
            bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
            edit_bones = arm_obj.data.edit_bones
            poseBones = arm_obj.pose.bones
            
            bones = list()
            bonesPoseData = list()
            poseBonesRotation = list()
            poseBonesRotationLocal = list()
            poseBonesConstraints = list()
            
            idDsID = dsID
            id = _dataStructure[idDsID][0]
            while (id < _dataStructure[idDsID][1]):
                if _parsedKeywords[id] == 'pos':
                    arm_obj.location = unpack_floats(_parsedRawValues[id], _dl)
                elif _parsedKeywords[id] == 'rot':
                    rRad = unpack_floats(_parsedRawValues[id], _dl)
                    for i in range(3):
                        arm_obj.rotation_euler[i] = radians(rRad[i])
                elif _parsedKeywords[id] == 'scale':
                    arm_obj.scale = unpack_floats(_parsedRawValues[id], _dl)
                #handle bones
                elif _parsedKeywords[id] == 'bones':
                    dsID += 1
                    for valueID in range(dsID, dsLastID):
                        if _parsedKeywords[_dataStructure[valueID][0] -1] == 'bname':
                            bones.append(valueID)
                            dsID = valueID
                            id = _dataStructure[valueID][1]
                id += 1
                
            for boneCount, boneID in enumerate(bones):
                bone = edit_bones.new(_parsedRawValues[_dataStructure[boneID][0] - 1])
                for lineID in range(_dataStructure[boneID][0], _dataStructure[boneID][1]):
                    if _parsedKeywords[lineID] == 'bname':
                        bone.name = _parsedRawValues[lineID]
                    elif _parsedKeywords[lineID] == 'head':
                        bone.head = unpack_floats(_parsedRawValues[lineID], _dl)
                    elif _parsedKeywords[lineID] == 'tail':
                        bone.tail = unpack_floats(_parsedRawValues[lineID], _dl)
                    elif _parsedKeywords[lineID] == 'head_radius':
                        edit_bones[bone.name].head_radius = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                    elif _parsedKeywords[lineID] == 'tail_radius':
                        edit_bones[bone.name].tail_radius = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                    elif _parsedKeywords[lineID] == 'roll':
                        edit_bones[bone.name].roll = radians(unpack_floats(_parsedRawValues[lineID], _dl)[0])
                    elif _parsedKeywords[lineID] == 'length':
                        edit_bones[bone.name].length = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                    elif _parsedKeywords[lineID] == 'envelope':
                        edit_bones[bone.name].envelope_distance = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                    elif _parsedKeywords[lineID] == 'layer':
                        bone.layers[int(_parsedRawValues[lineID])] = True
                    elif _parsedKeywords[lineID] == 'parent':
                        if _parsedRawValues[lineID] != 'None':
                            bone.parent = edit_bones[_parsedRawValues[lineID]]
                    elif _parsedKeywords[lineID] == 'connected':
                        bone.use_connect = bool(int(_parsedRawValues[lineID]))
                    elif _parsedKeywords[lineID] == 'local_location':
                        bone.use_local_location = bool(int(_parsedRawValues[lineID]))
                    elif _parsedKeywords[lineID] == 'inherit_rotation':
                        bone.use_inherit_rotation = bool(int(_parsedRawValues[lineID]))
                    elif _parsedKeywords[lineID] == 'inherit_scale':
                        bone.inherit_scale = _parsedRawValues[lineID]
                    elif _parsedKeywords[lineID] == 'envelope_distance':
                        bone.envelope_distance = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                    elif _parsedKeywords[lineID] == 'envelope_weight':
                        bone.envelope_weight = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                    elif _parsedKeywords[lineID] == 'envelope_multiply':
                        bone.use_envelope_multiply = bool(int(_parsedRawValues[lineID]))
                    elif _parsedKeywords[lineID] == 'rotation':
                        poseBonesRotation.append(unpack_floats(_parsedRawValues[lineID], _dl))
                    elif _parsedKeywords[lineID] == 'rotation_local':
                        poseBonesRotationLocal.append(unpack_floats(_parsedRawValues[lineID], _dl))
                    elif _parsedKeywords[lineID] == 'constraints':
                        constraintsData = list()
                        #the last bone constraint will need to be increased by 3 
                        #from the previous as there is no next to compare to
                        firstBone = bones[boneCount] + 3
                        if boneCount < len(bones) - 1:
                            firstBone = bones[boneCount+1]
                        #add constraint data
                        constraintData = list()
                        for cc in range(firstBone - (boneID+2)): #cc = constraintCount
                            if firstBone < dsLastID:
                                constraintData.append(_dataStructure[boneID+2+cc][0] - 1)
                                for clineID in range(_dataStructure[boneID+2+cc][0], _dataStructure[boneID+2+cc][1]):
                                    constraintData.append(clineID)
                        constraintsData.append(constraintData)
                            
                        poseBonesConstraints.append(constraintsData)

            #enter pose mode to edit pose values
            bpy.ops.object.mode_set(mode='POSE')
            
            for boneID, poseBone in enumerate(poseBones):
                poseBone.rotation_euler = poseBonesRotation[boneID]
                #poseBone.rotation_local = poseBonesRotationLocal[boneID]
                
                #add constraints
                for constraintData in poseBonesConstraints[boneID]:
                    if len(constraintData) > 0:
                        constraint = poseBone.constraints.new(_parsedRawValues[constraintData[0]])
                        for lineID in constraintData:
                            ########## if IK ##########
                            if constraint.type == 'IK':
                                if _parsedKeywords[lineID] == 'cname':
                                    constraint.name = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'target':
                                    constraint.target = bpy.data.objects[_parsedRawValues[lineID]]
                                elif  _parsedKeywords[lineID] == 'subtarget':
                                    constraint.subtarget = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'pole_target':
                                    constraint.pole_target = bpy.data.objects[_parsedRawValues[lineID]]
                                elif  _parsedKeywords[lineID] == 'pole_subtarget':
                                    constraint.pole_subtarget = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'pole_angle':
                                    constraint.pole_angle = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                                elif  _parsedKeywords[lineID] == 'iterations':
                                    constraint.iterations = int(_parsedRawValues[lineID])
                                elif  _parsedKeywords[lineID] == 'chain_length':
                                    constraint.chain_count = int(_parsedRawValues[lineID])
                                elif  _parsedKeywords[lineID] == 'use_tail':
                                    constraint.use_tail = bool(int(_parsedRawValues[lineID]))
                                elif  _parsedKeywords[lineID] == 'stretch':
                                    constraint.use_stretch = bool(int(_parsedRawValues[lineID]))
                                elif  _parsedKeywords[lineID] == 'weight_position':
                                    parsedValues = unpack_int_float(_parsedRawValues[lineID], _dl)
                                    constraint.use_location = parsedValues[0]
                                    constraint.weight = parsedValues[1]
                                elif  _parsedKeywords[lineID] == 'weight_rotation':
                                    parsedValues = unpack_int_float(_parsedRawValues[lineID], _dl)
                                    constraint.use_rotation = parsedValues[0]
                                    constraint.orient_weight = parsedValues[1]
                                elif  _parsedKeywords[lineID] == 'influence':
                                    constraint.influence = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                                    
                            ########## if COPY_ROTATION ##########
                            elif constraint.type == 'COPY_ROTATION':
                                if _parsedKeywords[lineID] == 'cname':
                                    constraint.name = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'target':
                                    constraint.target = bpy.data.objects[_parsedRawValues[lineID]]
                                elif  _parsedKeywords[lineID] == 'subtarget':
                                    constraint.subtarget = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'order':
                                    constraint.euler_order = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'axis':
                                    axis = unpack_ints(_parsedRawValues[lineID], _dl)
                                    constraint.use_x = axis[0]
                                    constraint.use_y = axis[1]
                                    constraint.use_z = axis[2]
                                elif  _parsedKeywords[lineID] == 'invert':
                                    invert = unpack_ints(_parsedRawValues[lineID], _dl)
                                    constraint.invert_x = invert[0]
                                    constraint.invert_y = invert[1]
                                    constraint.invert_z = invert[2]
                                elif  _parsedKeywords[lineID] == 'mix_mode':
                                    constraint.mix_mode = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'target_space':
                                    constraint.target_space = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'owner_space':
                                    constraint.owner_space = _parsedRawValues[lineID]
                                elif  _parsedKeywords[lineID] == 'influence':
                                    constraint.influence = unpack_floats(_parsedRawValues[lineID], _dl)[0]
            
            bpy.ops.object.mode_set(mode='OBJECT')
        print('\t\t\tFinished creating')  
        #go to the next data structure ID
        dsID = dsLastID + 1
        
    #add modifiers to objects after adding all objects and armatures to scene
    for objMod in _objModList:
        
        for modifiers in objMod[1]:
            if len(modifiers) > 0:
                modifier = objMod[0].modifiers.new(type = _parsedRawValues[modifiers[0]], name = _parsedRawValues[modifiers[2]])
                for lineID in modifiers:
                    ########## if MIRROR ##########
                    if modifier.type == 'MIRROR':
                        if _parsedKeywords[lineID] == 'axis':
                            axis = unpack_ints(_parsedRawValues[lineID], _dl)
                            modifier.use_axis[0] = axis[0]
                            modifier.use_axis[1] = axis[1]
                            modifier.use_axis[2] = axis[2]
                        elif _parsedKeywords[lineID] == 'bisect':
                            axis = unpack_ints(_parsedRawValues[lineID], _dl)
                            modifier.use_bisect_axis[0] = axis[0]
                            modifier.use_bisect_axis[1] = axis[1]
                            modifier.use_bisect_axis[2] = axis[2]
                        elif _parsedKeywords[lineID] == 'flip':
                            axis = unpack_ints(_parsedRawValues[lineID], _dl)
                            modifier.use_bisect_flip_axis[0] = axis[0]
                            modifier.use_bisect_flip_axis[1] = axis[1]
                            modifier.use_bisect_flip_axis[2] = axis[2]
                        #TODO: test if mirror object works
                        elif _parsedKeywords[lineID] == 'mirror_object':
                            if(_parsedRawValues[lineID] != 'None'):
                                modifier.mirror_object = _parsedRawValues[lineID]
                        elif _parsedKeywords[lineID] == 'clipping':
                            modifier.use_clip = bool(int(_parsedRawValues[lineID]))
                        elif _parsedKeywords[lineID] == 'merge':
                            parsedValues = unpack_int_float(_parsedRawValues[lineID], _dl)
                            modifier.use_mirror_merge = parsedValues[0]
                            modifier.merge_threshold = parsedValues[1]
                        elif _parsedKeywords[lineID] == 'bisect_distance':
                            modifier.bisect_threshold = unpack_floats(_parsedRawValues[lineID], _dl)[0]
                        elif _parsedKeywords[lineID] == 'mirror_u':
                            parsedValues = unpack_int_float(_parsedRawValues[lineID], _dl)
                            modifier.use_mirror_u = parsedValues[0]
                            modifier.mirror_offset_u = parsedValues[1]
                        elif _parsedKeywords[lineID] == 'mirror_v':
                            parsedValues = unpack_int_float(_parsedRawValues[lineID], _dl)
                            modifier.use_mirror_v = parsedValues[0]
                            modifier.mirror_offset_v = parsedValues[1]
                        elif _parsedKeywords[lineID] == 'offset':
                            parsedValues = unpack_floats(_parsedRawValues[lineID], _dl)
                            modifier.offset_u = parsedValues[0]
                            modifier.offset_v = parsedValues[1]
                        elif _parsedKeywords[lineID] == 'vertex_groups':
                            modifier.use_mirror_vertex_groups = bool(int(_parsedRawValues[lineID]))
                        elif _parsedKeywords[lineID] == 'flip_udim':
                            modifier.use_mirror_udim = bool(int(_parsedRawValues[lineID]))
                            
                    ########## if ARMATURE ##########
                    elif modifier.type == 'ARMATURE':
                        if _parsedKeywords[lineID] == 'object':
                            modifier.object = bpy.data.objects[_parsedRawValues[lineID]]
                        elif _parsedKeywords[lineID] == 'vertex_group':
                            modifier.vertex_group = _parsedRawValues[lineID]
                        elif _parsedKeywords[lineID] == 'preserve_volume':
                            modifier.use_deform_preserve_volume = bool(int(_parsedRawValues[lineID]))
                        elif _parsedKeywords[lineID] == 'multi_modifier':
                            modifier.use_multi_modifier = bool(int(_parsedRawValues[lineID]))
                        elif _parsedKeywords[lineID] == 'bind_to_vertex_groups':
                            modifier.use_vertex_groups = bool(int(_parsedRawValues[lineID]))
                        elif _parsedKeywords[lineID] == 'bind_to_bone_envelopes':
                            modifier.use_bone_envelopes = bool(int(_parsedRawValues[lineID]))

    print('\t\tFinished parsing ' + fileName)
    return {'FINISHED'}
    
def import_EndAnim(filePath, fileName):
    #####declare variables####
    _bc = 0 #bracket count, used to denote values within a value
    _rf = 6 #round float to decimal places
    _dl = '\t' #delimiter character
    _eq = '=' #equals character

    _fileIn = open(filePath + fileName)
    #####read entire file#####
    print('Reding from: ' + fileName)
    _rawFile = _fileIn.readlines()
    _fileIn.close()
    _parsedFile = list()
    _parsedKeywords = list()
    _parsedRawValues = list()
    print('\tFinished reading ' + fileName)
    
    #####parse file#####
    print ('\tParsing ' + fileName)
    
    #remove whitespace at beginning and end of line
    for rawLine in _rawFile:
        parsedLine = remove_whitespace(rawLine)
        
    #separate keywords and values
        charCount = 0
        for parsedChar in parsedLine:
            if parsedChar == _eq:
                break
            charCount += 1
            
        keyword = parsedLine[:charCount]
        rawValue = parsedLine[charCount+1:]
        
        _parsedKeywords.append(keyword)
        _parsedRawValues.append(rawValue)

    #create list of lists of the data structure
    #data in list is listed as follows:
    #each list contains 3 items
    #item 1 is the id of {
    #item 2 is the id of }
    #item 3 is the count of how deep the bracket list is
    _dataStructure = list()
    _bc = 0
    for id, keyword in enumerate(_parsedKeywords):
        
        if keyword == '{':
            dataList = list()
            dataList.append(id)
            _dataStructure.append(dataList)
            _bc += 1
        elif keyword == '}':
            _bc -= 1
            for i in range(len(_dataStructure))[::-1]:
                if (len(_dataStructure[i]) < 2):
                    _dataStructure[i].append(id)
                    _dataStructure[i].append(_bc)
                    break
    #select object, add animations, add keyframes
    dsID = 0 #data structure id
    
    while(dsID < len(_dataStructure)):

        #find the last data structure list in the mesh/armature
        dsLastID = dsID #last id for this block of data
        for id in range(dsID+1, len(_dataStructure)):
            if _dataStructure[id][2] == 0:
                dsLastID = id - 1
                break
            if id == len(_dataStructure) -1:
                dsLastID = id
                break
        
        print('\t\tSelected ' + _parsedKeywords[_dataStructure[dsID][0]-1] + ' ' + _parsedRawValues[_dataStructure[dsID][0]-1])
        
        ######################## if armature ########################
        if _parsedKeywords[_dataStructure[dsID][0]-1] == 'ARMATURE':
            
            armature = bpy.data.armatures[_parsedRawValues[_dataStructure[dsID][0]-1]]
            print('\t\t\tarmature name = ' + armature.name)
            
            #enter object mode and deselect all objects
            #select select armature and set to pose mode
            bpy.ops.object.mode_set(mode='OBJECT')
            for sObj in bpy.context.selected_objects:
                sObj.select_set(False)
            
            scene = bpy.context.scene
            obj = scene.objects.get(armature.name)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='POSE')
            armatureDSID = dsID
            poseArmature = bpy.data.objects[armature.name]
            id = _dataStructure[armatureDSID][0]
            
            if(len(bpy.data.actions) == 0):
                obj.animation_data_create()
                print('\t\t\t\tNew animation data created')
            
            while (id < _dataStructure[armatureDSID][1]):
                if _parsedKeywords[id] == 'fps':
                    bpy.context.scene.render.fps = int(_parsedRawValues[id])
                elif _parsedKeywords[id] == 'fpsbase':
                    bpy.context.scene.render.fps_base = float(_parsedRawValues[id])
                elif _parsedKeywords[id] == 'action':
                    bpy.ops.object.mode_set(mode='POSE')
                    dsID += 1
                    action = bpy.types.Action
                    action.name = _parsedRawValues[id]
                    actionExists = 0
                    for a in bpy.data.actions:
                        if a.name == action.name:
                            actionExists = 1
                    if actionExists:
                        print('\t\t\t\tCannot add action: ' + action.name + ' as it already exists')
                        id = _dataStructure[dsID][1] #skip to the end of the data block
                    else:
                        bpy.data.actions.new(action.name)
                        obj.animation_data.action = bpy.data.actions[action.name]
                        print('\t\t\t\tAdding action:\t' + action.name)
                        actionDsID = dsID
                        id += 2
                        while (id < _dataStructure[actionDsID][1]):
                            if _parsedKeywords[id] == 'start':
                                fstart = int(_parsedRawValues[id])
                                if fstart < scene.frame_start:
                                    scene.frame_start = fstart
                            elif _parsedKeywords[id] == 'end':
                                fend = int(_parsedRawValues[id])
                                if fend > scene.frame_end:
                                    scene.frame_end = fend
                            elif _parsedKeywords[id] == 'keyframes':
                                #do nothing as keyframes are read only
                                print('\t\t\t\t\tkeyframes = ' + _parsedRawValues[id])
                            elif _parsedKeywords[id] == 'keyframe':
                                keyframe = int(_parsedRawValues[id])
                                bpy.context.scene.frame_set(keyframe)
                                print('\t\t\t\t\t\tKeyframe: ' + str(keyframe))
                                dsID += 1
                                keyframeDsID = dsID
                                id += 2
                                while( id < _dataStructure[keyframeDsID][1]):
                                    if _parsedKeywords[id] == 'bone':
                                        bone = armature.bones[_parsedRawValues[id]]
                                        poseBone = poseArmature.pose.bones[bone.name]
                                        print('\t\t\t\t\t\t\tBone: ' + bone.name)
                                        dsID += 1
                                        #set auto keying
                                        scene.tool_settings.use_keyframe_insert_auto
                                        scene.tool_settings.auto_keying_mode
                                        poseBone.rotation_mode = 'XYZ'
                                        boneDsID = dsID
                                        id += 2
                                        while (id < _dataStructure[boneDsID][1]):
                                            if _parsedKeywords[id] == 'pos':
                                                poseBone.location = unpack_floats(_parsedRawValues[id], _dl)
                                                #y and z are flipped for bone position
                                                actualZ = -poseBone.location.y
                                                poseBone.location.y = poseBone.location.z
                                                poseBone.location.z = actualZ
                                                poseBone.keyframe_insert(data_path="location" ,frame = keyframe)
                                                print('\t\t\t\t\t\t\t\tSet pos: ' + str(poseBone.location))
                                            elif _parsedKeywords[id] == 'rot':
                                                poseBone.rotation_euler = unpack_floats(_parsedRawValues[id], _dl)
                                                poseBone.keyframe_insert(data_path="rotation_euler" ,frame = keyframe)
                                                print('\t\t\t\t\t\t\t\tSet rot: ' + str(poseBone.rotation_euler))
                                            elif _parsedKeywords[id] == 'sca':
                                                poseBone.scale = unpack_floats(_parsedRawValues[id], _dl)
                                                poseBone.keyframe_insert(data_path="scale" ,frame = keyframe)
                                                print('\t\t\t\t\t\t\t\tSet sca: ' + str(poseBone.scale))
                                            id += 1
                                    id += 1
                            id += 1
                    #return to object mode after posing keyframes
                    bpy.ops.object.mode_set(mode='OBJECT')
                id += 1
        #############################################################
        #go to the next data structure ID
        dsID = dsLastID + 1
    print ('\t\tFinished parsing ' + fileName)
    return {'FINISHED'}
