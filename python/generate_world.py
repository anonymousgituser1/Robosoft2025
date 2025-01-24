# This code generates a world file that can be used from webots
# based on parameters that are selected in soft_gripper_calibration.py
# Author: Lars Hof
# Date January 2024

from math import pi

position = [0.542, 0.221, 0.15161]
size_grey = 0.024
size_blue = 0.07
camera_distance = 0.20
height_dif = 0.06
light_distance = 0.05

#Array of different camera positions for different experiments.
    #Index 1 corresponds to passive experiments gripping side upwards and downwards
    #Index 2 correspond to passive experiment sideways
camera_position = { "upwards"   :   str(position[0]-camera_distance)+' '+ str(position[1]+size_blue/2+size_grey) + ' ' + str(position[2]-height_dif/2),
                    "downwards" :   str(position[0]-camera_distance)+' '+ str(position[1]+size_blue/2+size_grey) + ' ' + str(position[2]-height_dif/6*5),
                    "sideways"  :   str(position[0]-camera_distance)+' '+ str(position[1]+size_blue/2+size_grey) + ' ' + str(position[2])
}

light_position = { "upwards"   :   str(position[0]-light_distance)+' '+ str(position[1]+size_blue/2+size_grey) + ' ' + str(0),
                    "downwards" :   str(position[0]-light_distance)+' '+ str(position[1]+size_blue/2+size_grey) + ' ' + str(0),
                    "sideways"  :   str(position[0]-light_distance)+' '+ str(position[1]+size_blue/2+size_grey) + ' ' + str(0)
}



#Array of different rotation positions for different experiments.
    #Index 1 corresponds to passive experiments gripping side upwards and sideways
    #Index 2 correspond to passive experiment gripping side downwards
rotation = {    "upwards"   :   "0 0 -0.9999999999999999 1.5707953071795862",
                "downwards" :   "0.7071066717789584 -0.7071068905930504 -1.229829809714868e-06 3.14159",
                "sideways"  :   "0 0 -0.9999999999999999 1.5707953071795862"
} 

#Write the header to the world file
def header_world_info(file, controller, experiment, timestep, pressure,mass,particle_index):
    file.write('''#VRML_SIM R2023b utf8

        EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/objects/backgrounds/protos/TexturedBackground.proto"
        EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"
        EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/objects/floors/protos/RectangleArena.proto"
        EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/robots/universal_robots/protos/UR3e.proto"
        EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/objects/solids/protos/SolidBox.proto"
        EXTERNPROTO "../protos/SoftGripper'''+'_particle_'+str(particle_index)+'''.proto"

        WorldInfo {
            basicTimeStep ''' + str(timestep) + '''
        }
        Viewpoint {
        orientation -0.20703596007392364 -0.03611434338673006 0.9776665410240929 3.520736132379194
        position 1.1623241000432232 0.4225638912295447 0.3860349442881799
        }
        TexturedBackground {
        }
        TexturedBackgroundLight {
        }
        RectangleArena {
        rotation 0 1 0 0
        floorSize 5 5
        }
        DEF ur3e UR3e {
        rotation 0 1 0 0
        controller "'''+str(controller)+'''"
        controllerArgs [
        "--experiment",
        "''' + str(experiment) +'''"
        "--pressure",
        "''' + str(pressure) +'''"
        "--particle_index",
        "''' + str(particle_index) +'''"
         "--mass",
        "''' + str(mass) +'''"
        ]
        toolSlot [
            SoftGripper'''+'_particle_'+str(particle_index)+''' {
            translationFinger1 0.04 0.012 0
            rotationFinger1 ''' + str(rotation[experiment]) +'''
            translationFinger2 -0.04 0.012 0
            rotationFinger2 0.7071066717789584 -0.7071068905930504 -1.229829809714868e-06 3.14159
            }
        ]
        }

        SpotLight {
            ambientIntensity 1
            beamWidth 1.570796
            color 255 255 255
            cutOffAngle 1.570796
            direction 0 0 1
            intensity 1
            location '''+ str(light_position[experiment]) +'''
            on TRUE
            radius 100
            castShadows FALSE
        } 

        \n''')

#Writes the supervisor to the world file. This is different between active and passive 
# experiments because the supervisor also acts as the scale in this experiment
def supervisor(file, experiment, supervisor_controller, experiment_type,mass,particle_index):
    if experiment_type == "active":
        file.write('''DEF Supervisor Robot {
            name "box_A"
            controller "''' + str(supervisor_controller) + '''"
            controllerArgs [
            "--particle_index",
            "''' + str(particle_index) +'''"
            ]
            translation 0.542 0.295 0.046
            contactMaterial "hard"
            supervisor TRUE
            children [
                    DEF BOX_SHAPE Shape {
                    appearance PBRAppearance {
                        baseColor 1 0 0
                        roughness 0.5
                        metalness 0.5
                        }
                        geometry Box {
                            size 0.05 0.09 0.093
                        }
                    }
                
                        TouchSensor {
                            translation 0 0 0.0465
                            contactMaterial "hard"
                            children [
                                DEF BUMPER Shape {
                                appearance PBRAppearance {
                                    baseColor 1 0.647059 0
                                    roughness 1
                                    metalness 0
                                }
                                geometry Box {
                                    size 0.02 0.092 0.00005
                                }
                                }
                            ]
                            name "force"
                            boundingObject USE BUMPER
                            physics Physics {
                                mass 10
                            }
                            type "force-3d"
                            }
        
                ]
                boundingObject USE BOX_SHAPE
                physics Physics {
                    mass 10
                }
                }
                \n''') 
        
    else:
        file.write('''
        DEF Supervisor Robot {
        name "''' + str('supervisor3') + '''"
        controller "''' + str(supervisor_controller) + '''"
        controllerArgs [
        "--particle_index",
        "''' + str(particle_index) +'''"
        "--mass",
        "''' + str(mass) +'''"
        ]
        supervisor TRUE
        children [
            DEF CAMERA Camera {
                translation '''+ str(camera_position[experiment]) +'''
                rotation 1 0 0 0
                name "camera1"
                width 2160
                height 1080
            }
        ]
        }\n''') 

#Main file that ensures all the relevant parts are written to the world file in correct order
def main(world_file, controller, supervisor_controller, experiment, timestep, experiment_type, mass, particle_index, pressure=None):
    file = open(world_file, "w")
    header_world_info(file, controller, experiment, timestep, pressure ,mass,particle_index) 
    supervisor(file, experiment, supervisor_controller, experiment_type,mass,particle_index)
    file.close()
