#! /usr/bin/env python
# this function takes the list of python variables and makes a subs file to use
f=open('iocVars.txt','r')
fOut=open('fakeIOC.template','w')
cLine=f.readline().strip()
while len(cLine)>0:
	cSatz=cLine.split(',')
	fOut.write('record('+cSatz[1][1:len(cSatz[1])-1]+', "'+cSatz[0]+'") {\n')
	fOut.write('field (VAL,'+cSatz[2]+')\n')
	fOut.write('field (DESC, "FakeIOC")\n}\n')
	cLine=f.readline().strip()
fOut.close() 
