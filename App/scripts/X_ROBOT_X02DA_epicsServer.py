#! /usr/bin/env python

#-------------------------Import libraries---------------------------------------------------
import sys
import os
import time
#from X_ROBOT_X02DA_robotCommon import *
from optparse import OptionParser
#Copyright Jon Berg , turtlemeat.com

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from cPickle import dumps,loads
import urllib
#import pri

class EpicsServerHttpHandler(BaseHTTPRequestHandler):
    def decodepath(self):
        d = {}
        myCmd=self.path[1:]
        myArgs=myCmd.split('?')[1:]
        a=[]
        if len(myArgs)>0: a=myArgs[0].split('&')
        for s in a:
            if s.find('='):
                k,v = map(urllib.unquote, s.split('='))
                try:
                    d[k].append(v)
                except KeyError:
                    d[k] = [v]
        return d

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            print dir(self)
            
            myCmd=self.path[1:]
            myArgs=self.decodepath()
            if myCmd.startswith("GET_INFO"):
                self.wfile.write('EpicsWebServer Version:'+str(20090526))
                return
            if myCmd.startswith("GET_EPICS_PICKLE"):
                outDict={}
                for cArg in myArgs.keys():
                    outDict[cArg]='Gruezi'
                    
                self.wfile.write(urllib.quote(dumps(outDict)))
                return
            if myCmd.startswith("PUT_EPICS_PICKLE"):
                try:
                    for cItem in myArgs.keys():
                        print cItem+'='+str(myArgs[cItem][0])
                    self.wfile.write('GOOD')
                except:
                    self.wfile.write('FAILED'+str(myArgs))
                return
            elif myCmd.find(".htm")>-1:
                self.wfile.write(self.path+'<br> ich verstoh ned ganz <br> i cha ned ihne holfe')
                return
            
            elif myCmd.endswith(".esp"):   #our dynamic content
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write("hey, today is the" + str(time.localtime()[7]))
                self.wfile.write(" day in the year " + str(time.localtime()[0]))
                return
                
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
     

    def do_POST(self):
        return # post isnt supported yet
        global rootnode
        print self.headers.getheader('content-type')
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            print ctype
            print pdict
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
            
            self.end_headers()
            #upfilecontent = query.get('upfile')
            #print "filecontent", upfilecontent[0]
            self.wfile.write(str(self.rfile.read()));
            
            #self.wfile.write(upfilecontent[0]);
            
        except :
            pass

def main():
    try:
        server = HTTPServer(('', 7269), EpicsServerHttpHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

