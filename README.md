# Tomcat-Robot
The source code for the tomcat robot, gui, and related tools
## Python Scripts


## Intranet-based Documentation
Much of the documentation is available on the PSI Intranet
https://intranet.psi.ch/Tomcat/TomcatProjectIRobot

## Organization
### Staubli VAL3 Code
- https://github.com/kmader/Tomcat-Robot/tree/master/VAL3
### EPICS Code
The root directory all files with prefix
- X_ROBOT_X02DA for the channels themselves
- X02DA-PC-ROBO for the soft-ioc responsible for the robot

### Python Scripts
#### Overview
The python scripts serve as the interface to the epics-based control of the physical robot, The scripts just change variables and handle issues when they arise. In some cases variables are not responsive and in these case the program resets the channels, tries multiple times, and otherwise error traps the issue. Preventing such problems as Network disconnects, robot glitches, and the like from befalling a user. The program is also designed as a barrier between the user and direct control of everything enabling stage-locking when the robot is moving, execution of commands in only specific orders, and so forth. The program will also connect and exchange information with the database creating and deleting records as needed.
The scripts are all located in the directory [https://github.com/kmader/Tomcat-Robot/tree/master/App/scripts]. 

#### Layout
The robot tool is built off of a UserGUI tool and an AlignmentGUI with various plug-ins. The UserGUI corresponds to the version of the program that is executed on the beamline when measuring samples the alignment tool uses the same interface but will instead only record alignment positions on the specified stage.





