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
public class LacunaPreview {
	static VirtualAim mapA;
	public static void main(String[] args) {
		boolean writeHeader=false;
		System.out.println("Kevin's Single Lacuna Preview");
		System.out.println("Takes AIM as short as input, values expected to be distances");
		System.out.println("Lacuna Aim: "+args[0]);
		//System.out.println("Output CSV: "+args[2]);
		//TomcatDB myDB=new TomcatDB();
		
		mapA=new VirtualAim(args[0]);
		mapA.ShortScaleFactor=(float) 1.0; // For the map we want the values to be preserved and not skewed
		
		String execLine="";
		Vector CurSliceValues;
		if ((mapA.ischGuet))  {
			mapA.GetPoints();
			LacunaShape myLacuna=new LacunaShape(mapA.positionList,mapA.valueList);
			myLacuna.CalcStats();
			String headStr="//"+args[0]+" sX, sY, sZ, COMx, COMy, COMz , COMvx, COMvy, COMvz, Wx, Wy, Wz,pca1X, pca1Y, pca1Z,pca1score,pca2X, pca2Y, pca2Z,pca2score, angCanal to PC1, mean, comVal, std, voxct, totalVox\n";
			String outStr=mapA.elSize.x+", "+mapA.elSize.y+", "+mapA.elSize.z+", "+myLacuna;
			System.out.println(headStr);
			System.out.println(outStr);
			myLacuna.view();
			
			myLacuna=null;
			mapA.positionList=null;        
      		mapA.valueList=null;
			System.gc();
		} else {
			System.out.println("Files Not Present");
		}
		
	}
}




	