//package ij.plugin;
//import java.awt.*;
//import java.awt.image.*;
//import java.awt.image.ColorModel.*;
import java.io.*;
import java.net.*;
import java.security.Principal;
import java.util.*;
import java.io.IOException;
import java.io.PrintStream;
import java.net.InetAddress;
import java.lang.Math;
import java.awt.event.*;

// Used as a replacement for the moment function as it allows much more control over data
// and communication with webservices (potentially?)
/** Opens an aim file through JAimPack as a stack. */
// This is now designed to use shorts instead of floats potentially speeding things up a bit
public class LacunaMorpho {
	public static void main(String[] args) {
		boolean writeHeader=false;
		System.out.println(" Kevin's Lacuna Morphometric Analysis v0.01");
		System.out.println("Input Aim: "+args[0]);
		System.out.println("Output CSV: "+args[1]);
		VirtualAim vas=new VirtualAim(args[0]);
		LacunaShape myLacuna=new LacunaShape(vas);
		TomcatDB myDB=new TomcatDB();
		String execLine="";
		if (vas.ischGuet) {
			myLacuna.CalcStats();
			try {
				String outStr="";
				String headerStr="//"+args[0]+" sX, sY, sZ, COMx, COMy, COMz , COMvx, COMvy, COMvz, Wx, Wy, Wz,pca1X, pca1Y, pca1Z,pca1score,pca2X, pca2Y, pca2Z,pca2score, angCanal to PC1, mean, comVal, std, voxct, totalVox\n";
				
				if (writeHeader) outStr+=headerStr;
				outStr+=vas.elSize.x+", "+vas.elSize.y+", "+vas.elSize.z+", ";
				outStr+=myLacuna;
				FileWriter out = new FileWriter(args[1],true);
				out.append(outStr);
				out.flush();
				out.close();
				
				myDB.UpdateRecord("LACUN-"+myDB.VMSCleanName(args[1]),args[0]+"\n"+outStr);
			} catch(Exception e) {
				e.printStackTrace();
			}
		} else {
			try {
				//System.out.println("$ delete/entry="+args[2]+" sys$eval");
				if (args.length<3) {
					execLine="$ DELETE/ENTRY='JOB_NR'  \n";
				} else {
					//execLine="sue:kill_task.com "+args[2];
					execLine="$ DELETE/ENTRY="+args[2]+"  \n";
				}
				ExecTask killMe=new ExecTask(execLine);
				myDB.UpdateRecord("LACSS-"+myDB.VMSCleanName(args[1]),"Stopping!!!\n");
				//Runtime.getRuntime().exec("delete/entry="+args[2]); // If file cant be read kill it all
			} catch(Exception e) {
				System.out.println(execLine);
				System.out.println("Tried to kill task, but didnt work");
				e.printStackTrace();
			}
		}
		
	}
}

		





	