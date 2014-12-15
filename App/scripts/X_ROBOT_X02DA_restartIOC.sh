#!/bin/sh
# $RCSfile: X_ROBOT_X02DA_restartIOC.sh,v $
# $Source: /cvs/X/ROBOT/X02DA/App/scripts/X_ROBOT_X02DA_restartIOC.sh,v $
# $Author: celcer_t $
# $Revision: 1.2 $
# $Name:  $
# $Date: 2012/01/25 14:00:14 $
#
# Responsible:  A. Isenegger
# Description:  This file contains the command to restart the soft-IOC with 
#               the project name X02DA-PC-ROBO.
# Notes:        

#-------------------------------------------------------------------------------

#   echo kill > /dev/tcp/x02da-softioc/50002
    echo exit > /dev/tcp/x02da-softioc/50002

# --- End of $RCSfile: X_ROBOT_X02DA_restartIOC.sh,v $ -------------------------
