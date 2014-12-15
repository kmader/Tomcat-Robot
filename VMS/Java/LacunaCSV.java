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
public class LacunaCSV {
	static Vector<Integer> AlreadyFound;
	static VirtualAim mapA;
	
	public static void main(String[] args) {
		boolean writeHeader=false;
		String kVer="001_090906";
		System.out.println(" Kevin's Lacuna Morphometric Analysis with CSV Export v"+kVer);
		System.out.println("Map Aim: "+args[0]);
		System.out.println("Distance Aim: "+args[1]);
		System.out.println("Output CSV: "+args[2]);
		System.out.println("Raw Name: "+args[3]);
		
		TomcatDB myDB=new TomcatDB();
		
		try {
			myDB.UpdateRecord("LACSV-"+myDB.VMSCleanName(args[2]),"Run Started @ "+new Date()+"\n",false,"H");
		} catch (Exception e) {
			System.out.println("TomcatDB Problem");
		}
		long start = System.currentTimeMillis();
    

    	

		mapA=new VirtualAim(args[0]);
		mapA.ShortScaleFactor=(float) 1.0; // For the map we want the values to be preserved and not skewed
		VirtualAim disA=new VirtualAim(args[1]);
		
		
		String execLine="";
		Vector CurSliceValues;
		if ((mapA.ischGuet) && (disA.ischGuet))  {
			LacunaShape myLacuna=new LacunaShape();
			try {
				String dbOutString="";
				dbOutString+="LacunaCSV   Version:"+kVer+"\n";
				dbOutString+="VirtualAim  Version:"+mapA.kVer+"\n";
				dbOutString+="LacunaShape Version:"+myLacuna.kVer+"\n\n";
				dbOutString+="Data Loaded in "+((System.currentTimeMillis()-start)/(60*1000F))+" mins @ "+new Date()+"\n";
				dbOutString+="Sample Name: "+mapA.sampleName+"\n";
				myDB.UpdateRecord("LACSV-"+myDB.VMSCleanName(args[2]),dbOutString,"C");
			} catch (Exception e) {
				System.out.println("TomcatDB Problem");
			}
			AlreadyFound=new Vector(5000);
			for (int cSlice=0;cSlice<mapA.getSlices();cSlice++) {
				if (mapA.imageType==1) 
				{
					CurSliceValues=ScanShortSlice(cSlice);
				} else if (mapA.imageType==2) 
				{
					CurSliceValues=ScanIntSlice(cSlice);
				} else {
					System.out.println("Map of type : "+mapA.dataName+" , "+mapA.imageType+" not supported!");
					CurSliceValues=new Vector();
				}
				Iterator itr=CurSliceValues.iterator();
				while(itr.hasNext()) {
					Integer curPtI=(Integer) itr.next();
					int curPt=curPtI.intValue();
					//System.out.println("Extracting Distances Lacuna :"+curPt);
					mapA.GetPoints(curPt-1,curPt,cSlice);
					System.out.println("Extracting Distances ("+mapA.positionList.size()+") Lacuna :"+curPt);
					disA.GetPointsFromList(mapA.positionList);
					myLacuna=new LacunaShape(disA.positionList,disA.valueList);
					myLacuna.CalcStats();
					try {
						String outStr="";
						String headerStr="//"+args[0]+" sX, sY, sZ, COMx, COMy, COMz , COMvx, COMvy, COMvz, Wx, Wy, Wz,pca1X, pca1Y, pca1Z,pca1score,pca2X, pca2Y, pca2Z,pca2score, angCanal to PC1, mean, comVal, std, voxct, totalVox\n";
						
						if (writeHeader) outStr+=headerStr;
						outStr+=mapA.elSize.x+", "+mapA.elSize.y+", "+mapA.elSize.z+", ";
						outStr+=myLacuna;
						FileWriter out = new FileWriter(args[2],true);
						out.append(outStr);
						out.flush();
						out.close();
						// Wite CSV Output
						out = new FileWriter(args[3]+"-"+curPt+"_LACSV.csv",false);
						float x,y,z,cDist;
						for (int i=0;i<disA.positionList.size();i++) {
							Float[] cPoint=(Float[]) disA.positionList.elementAt(i);
							x=cPoint[0].floatValue();
							y=cPoint[1].floatValue();
							z=cPoint[2].floatValue();
							cDist=(Float) disA.valueList.elementAt(i);
							out.write(x+","+y+","+z+","+cDist+"\n");
						}
						out.flush();
						out.close();
						// No more abusive traffic
						//myDB.UpdateRecord("LACGZ-"+myDB.VMSCleanName(args[2]),", ("+curPt+", "+(mapA.getSliceCalls+disA.getSliceCalls)+")");
					} catch(Exception e) {
						e.printStackTrace();
					}
					myLacuna=null;
					mapA.positionList=null;
					disA.positionList=null;
					mapA.valueList=null;
					disA.valueList=null;
					System.gc();
				}
				itr=null;
				CurSliceValues=null;
				if ((mapA.getSliceCalls+disA.getSliceCalls)>1e10) {
					//Time to clean up
					System.out.println("Flushing VirtualAims after ( "+mapA.getSliceCalls+", "+disA.getSliceCalls+") calls");
					mapA=null;
					disA=null;
					System.gc();
					mapA=new VirtualAim(args[0]);
					mapA.ShortScaleFactor=(float) 1.0; // For the map we want the values to be preserved and not skewed
					disA=new VirtualAim(args[1]);
				}
				System.gc();
			}
		} else {
			System.out.println("Files Not Present");
		}
		try {
			float eTime=(System.currentTimeMillis()-start)/(60*1000F);
			String outString="\n"+"Lacuna Found "+AlreadyFound.size()+", Lacuna/Minute="+(AlreadyFound.size()/eTime)+"\n";
			outString+="Slices Read "+(mapA.getSliceCalls+disA.getSliceCalls)+", Slices/Second="+((mapA.getSliceCalls+disA.getSliceCalls)/(eTime*60.0))+"\n";
			outString+="Run Finished in "+eTime+" mins @ "+new Date()+"\n";
			
			myDB.UpdateRecord("LACSV-"+myDB.VMSCleanName(args[2]),outString,"N");
		} catch (Exception e) {
			System.out.println("TomcatDB Problem");
		}
		
	}
	public static Vector ScanShortSlice(int sliceNumber) {
		short[] gg=mapA.getShortArray(sliceNumber);
		Vector<Integer> curSlice=new Vector();
		for (short b: gg) {
			if (b>0) {
				Integer nB=new Integer((int) b);
				if (!AlreadyFound.contains(nB)) {
					System.out.println("New Object Found :"+nB);
					AlreadyFound.add(nB);
					curSlice.add(nB);
				}
				
			}
		}
		return curSlice;
	}
	public static Vector ScanIntSlice(int sliceNumber) {
		int[] gg=mapA.getIntArray(sliceNumber);
		Vector<Integer> curSlice=new Vector();
		for (int b: gg) {
			if (b>0) {
				Integer nB=new Integer(b);
				if (!AlreadyFound.contains(nB)) {
					System.out.println("New Object Found :"+nB);
					AlreadyFound.add(nB);
					curSlice.add(nB);
				}
				
			}
		}
		return curSlice;
	}
}

		





	