# This code generates a proto file that can be used from webots
# based on parameters that are selected in soft_gripper_calibration.py
# Author: Lars Hof
# Date January 2024

import os
from math import pi

#Assuming the mass is equally distributed over the slices this is the mass in each slice 
# this can be improved upon by measuring each part individually 
mass = 0.00207

#Anchors and translations used to connect the parts of the gripper. 
# These are derived from the original proto created by Yulyan
anchors = [[-0.0191, -0.0085, 0],
            [-0.0043, -0.0009, 0],
            [-0.0042, -0.0016, 0],
            [-0.0042, -0.0013, 0],
            [-0.0042, -0.0014, 0],
            [-0.0042, -0.0012, 0],
            [-0.0042, -0.0016, 0]]

translations = [[-0.0236, -0.0073, -0.0006],
                [-0.0087, -0.0002999999999999999, 0],
                [-0.0087, -0.0005, 0],
                [-0.0087, -0.0006, 0],
                [-0.0084, -0.0009, 0],
                [-0.0092, -0.001, 0],
                [-0.009, -0.0034, 0]]

#Gets the names of the cad file and motor based on the finger and slice
def get_names(finger, slice):
    cad_file = '"../CAD/CAD softgripper_slice'+str(slice+2)+'.obj"'
    motor_name = '"finger'+str(finger)+'_rot_z_'+str(slice+1)+'"'
    return cad_file, motor_name

#Writes the header to the proto file
def header_proto(file,particle_index):
    file.write('''#VRML_SIM R2023b utf8
        PROTO SoftGripper'''+'_particle_'+str(particle_index)+''' [
        field SFVec3f translationFinger1 0 0 0
        field SFRotation rotationFinger1 0 0 1 0
        field SFVec3f translationFinger2 0 0 0
        field SFRotation rotationFinger2 0 0 1 0
        field SFVec3f scale 1 1 1
        field SFString name "SoftGripper'''+'_particle_'+str(particle_index)+'''"
        field SFString model ""
        field SFString description ""
        field SFString contactMaterial "soft"
        field MFNode immersionProperties [ ]
        field SFBool locked FALSE
        field SFFloat radarCrossSection 0
        field MFColor recognitionColors [ ]
        field SFFloat translationStep 0.01
        field SFFloat rotationStep 0.261799387
        field SFVec3f linearVelocity 0 0 0
        field SFVec3f angularVelocity 0 0 0
        field SFBool selfCollision TRUE
        ]
        {
        Solid {
        translation 0 0 0
        children [
        \n''')

#Creates a finger in a proto file
def create_finger(file, finger, slices, calibration_type, spring_constants_hinge, damping_constants_hinge, spring_constant_joint, damping_constant_joint, extra_mass):
    file.write('''
        DEF ''' + "Finger" + str(finger) + ''' Solid {
        translation IS ''' + "translationFinger" + str(finger) + '''
        rotation IS ''' + "rotationFinger" + str(finger) + '''
        scale IS scale
        selfCollision IS selfCollision
    

        children [
        DEF Part1 CadShape {
        url [
        "../CAD/CAD softgripper_slice1.obj"
        ]
        }\n''')

    for slice in range(slices):
        cad_file, motor_name = get_names(finger, slice)
        file.write('''
            Hinge2Joint {
            jointParameters DEF Finger''' + str(finger) + '''_Joint''' + str(slice+1) + ''' HingeJointParameters {
            axis 0 0 1
            anchor ''' + str(anchors[slice][0]) + ''' ''' + str(anchors[slice][1]) + ''' ''' + str(anchors[slice][2]) + '''
            springConstant ''' + str(spring_constants_hinge[slice]) + '''
            dampingConstant ''' + str(damping_constants_hinge[slice]) + '''
            }
            jointParameters2 JointParameters {
            axis 0 1 0
            springConstant ''' + str(spring_constant_joint[slice]) + '''
            dampingConstant ''' + str(spring_constant_joint[slice]) + '''
            }
            device [
            RotationalMotor {
            name ''' + str(motor_name) + '''
            }
            PositionSensor{
                
            }
            ]
            endPoint DEF Finger''' + str(finger) + '''_Rigid''' + str(slice+1) + ''' Solid {
            translation ''' + str(translations[slice][0]) + ''' ''' + str(translations[slice][1]) + ''' ''' + str(translations[slice][2]) + '''
            rotation 0 1 0 0
            contactMaterial "soft"
            children [
            CadShape {
            url [
            ''' + str(cad_file) + '''
            ]
            }\n''')

    for slice in range(1,slices+1):
        cad_file, motor_name = get_names(finger, (slices-slice))
        if slice == 1 and calibration_type == "spring":
            file.write('''
                ]
                boundingObject Mesh {
                url [
                ''' + str(cad_file) + '''
                ]
                }
                physics Physics {
                mass  '''+ str(mass + extra_mass) + '''
                }

                }
                }
                \n''')
        else:
            file.write('''
                ]
                boundingObject Mesh {
                url [
                ''' + str(cad_file) + '''
                ]
                }
                physics Physics {
                mass  '''+ str(mass) + '''
                }
                }
                }
                \n''')
    file.write(''']''')

    file.write('''
        name ''' + '"finger' + str(finger) + '"' + '''
        model IS model
        description IS description
        contactMaterial IS contactMaterial
        immersionProperties IS immersionProperties
            
        boundingObject Mesh {
        url [
        "../CAD/CAD softgripper_slice1.obj"
        ]
        }

        physics Physics {
        mass '''+ str(mass) + '''
        }

        locked IS locked
        radarCrossSection IS radarCrossSection
        recognitionColors IS recognitionColors
        translationStep IS translationStep
        rotationStep IS rotationStep
        linearVelocity IS linearVelocity
        angularVelocity IS angularVelocity
        }\n''') 

#Finishes the proto file
def finish_proto(file):
    file.write('''
        ]
	    name IS name
        physics Physics {
        mass '''+ str(mass) + '''
        }
        }
        }''')

#Main file that ensures all the parts of the gripper are written to the proto file
def main(proto_file, calibration_type, spring_constants_hinge, damping_constants_hinge, spring_constants_joint, damping_constants_joint, slices, extra_mass, particle_index):
    file = open(str(proto_file), "w")
    header_proto(file,particle_index)

    for finger in [1,2]:
        create_finger(file, finger, slices, calibration_type, spring_constants_hinge, damping_constants_hinge, spring_constants_joint, damping_constants_joint, extra_mass)
    
    finish_proto(file)

    file.close()
