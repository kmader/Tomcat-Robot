# Tomcat-Robot
The source code for the tomcat robot, gui, and related tools


## Intranet-based Documentation
Much of the documentation is available on the PSI Intranet
https://intranet.psi.ch/Tomcat/TomcatProjectIRobot


## Organization
---+ Python Scripts
---++ Overview
The python scripts serve as the interface to the [[TREpics][epics-based]] control of the [[TRRobot][physical robot]], The scripts just change variables and handle issues when they arise. In some cases variables are not responsive and in these case the program resets the channels, tries multiple times, and otherwise error traps the issue. Preventing such problems as Network disconnects, robot glitches, and the like from befalling a user. The program is also designed as a barrier between the user and direct control of everything enabling stage-locking when the robot is moving, execution of commands in only specific orders, and so forth. The program will also connect and exchange information with the database creating and deleting records as needed.
---++ Organization
The robot tool is built off of a UserGUI tool and an AlignmentGUI with various plug-ins. The UserGUI corresponds to the version of the program that is executed on the beamline when measuring samples the alignment tool uses the same interface but will instead only record alignment positions on the specified stage.
---++ Plug-Ins
---+++ Tray Setup
   * UserGUI_Tray: <br />
     <img src="%ATTACHURLPATH%/UserGUIRobot.png" alt="UserGUIRobot.png" width='812' height='649' />
The tray setup tool allows the users to select which samples are in which tray position. It allows the user to record the stage position for each sample and to choose which samples are too be run.
---+++ Script Editor
   * UserGUI_Script: <br />
     <img src="%ATTACHURLPATH%/UserGUIScript.png" alt="UserGUIScript.png" width='812' height='649' />
The script editor is the interface for creating a script based off of a tray created in Tray Setup. The button 'Recreate' generates the default script running each item from the tray once.
The commands that can be used the sequencer can be found [[TRSequencerCommands][here]]
---+++ User Information
This is where the user is able to enter their information such as a contact number and name and sample summary.
---+++ Stage Control
   * UserGUI_End Station 1: <br />
     <img src="%ATTACHURLPATH%/UserGUIES1.png" alt="UserGUIES1.png" width='643' height='536' />
Stage control allows for the basic movements of the x,y,z,xx,zz,roty stages for the purpose of sample alignment
---+++ Acquisition Settings
   * UserGUI_Scan: <br />
     <img src="%ATTACHURLPATH%/UserGUIScan.png" alt="UserGUIScan.png" width='643' height='569' />
This panel pulls that status settings from the sls, and beamline. The panel also allows for user selection of flats, darks, and exposures.
---+++ Sequencer 
The sequencer is the plug-in that is used to run scripts on a set of aligned named samples. The sequencer uses the same script that was created in the Script Editor Tool and allows the user to follow and control the command flow.
---++ Permissions
HL = Hutch Laptop, BC = Beamline Computer, OU= Outside
(adv) = Only for advanced users
| What | Read Permissions (Who may read) | Write Permissions (Who may write) |
| *Beamline* |
| Energy | HL, BC, OU | HL (adv), BC(adv)|
| Slits | HL, BC, OU | HL(adv), BC(adv) |
| ES1 Shutter | HL, BC, OU | HL, BC |
| *Stage* |
| X,Y,XX,ZZ | HL, BC, OU | HL, BC |
| Z | HL, BC, OU | HL |
| ROTY | HL, BC, OU | HL, BC |
| *Microscope* |
| FocusAxis | HL,BC,OU | HL(adv),BC(adv) |
| BaseStage | HL,BC,OU | HL(adv) |
| LensSelect | HL,BC,OU | HL(adv) |
| *Camera* |
| X,Y,Z | HL, BC, OU | |
| *Tomography* |
| Start | HL, BC, OU | HL, BC |
| Pause | HL, BC, OU | HL, BC |
| Parameters | HL, BC, OU | HL, BC |
| *Robot* |
| StartRobot | | HL |
| StopRobot | | HL, BC, OU |
| Unload/Load | | HL, BC |
| RobotStatus | HL, BC, OU | |
| StartScript | | HL, BC |
| StopScript | | HL, BC, OU |

---+++ Outside

---++ File Locations
The files are located in the CVS under
   * [[http://www.sls.psi.ch/cgi-bin/cvsweb.cgi/X/ROBOT/X02DA/Python/][/X/ROBOT/X02DA/Python/]]
   * [[http://www.sls.psi.ch/cgi-bin/cvsweb.cgi/X/ROBOT/X02DA/App/scripts/][/X/ROBOT/X02DA/App/scripts]]
They are located locally on the [[x02daop]] account and for development in
   * /sls/X02DA/data/e12050/ROBOT/X02DA/Python
| *Name* | *Location* | *Description* |
| *Automation Tools*|
| [[TRUserGUI][Tomcat UserGUI Tool]] | /work/sls/bin/X_ROBOT_X02DA_UserGUI.py | The primary beamline user tool |

| [[TRSequencer][Tomcat Robot Sequencer]] | /work/sls/bin/X_ROBOT_X02DA_cmdSequencer.py | A commandline version of the sequencer that is potentially more stable over extremely long runs |
| Tomcat Robot Script Library | /work/sls/bin/X_ROBOT_X02DA_robotScript.py | The class governing the robot scripting and sequencer. This is where all new commands should be defined as both the align tool and the sequencer use it, to validate and run commands repectively|
| Tomcat Robot Common Library | /work/sls/bin/X_ROBOT_X02DA_robotCommon.py |  A class that defines the robot and allows for robot communication using functions abstracting the epics channel manipulation, enabling many programs to be written without rewriting the robot interface. Also an epics channel library that checks and reconnects to channels and has some of the more commonly used operations built-in|
| *Varia Tools* |
| IOC Debug Mode | /sls/X02DA/data/e12050/ROBOT/X02DA/Python/IOCRobotModeSwitch.py | The code to replace variables in the template and subs files for the softIOC to ensure nothing is affected on the beamline |
| fakeIOC| /sls/X02DA/data/e12050/ROBOT/X02DA/Python/fakeIOC.py | The code takes a list generated on a softioc by typing (dbl "","RTYP VAL") and pasting into IOCVars.txt, and generates a fakeIOC.template file that can be used (zb iocsh fakeIOC.template) so programs can be tested off beamline (the variables do not behave exactly as robotCommon likes so it doesnt work perfectly, but much better than without |



-- Main.KevinMader - 09 Oct 2008








