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
public class LacunaShell {
	static Vector<Integer> AlreadyFound;
	static VirtualAim mapA;
	public static void main(String[] args) {
		boolean writeHeader=false;
		boolean maskPresent;
		String kVer="001_090906";
		String mapName="";
		String cDistName="";
		String mDistName="";
		String csvName="";
		System.out.println(" Kevin's Lacuna Shell Morphometric Analysis v"+kVer);
		if (args.length==4) {
			System.out.println("	with Mask and Canal Morphometric Analysis");
			cDistName=args[1];
			mDistName=args[2];
			csvName=args[3];
			maskPresent=true;
		} else {
			System.out.println(" 	with Canal Morphometric Analysis");
			cDistName=args[1];
			mDistName="";
			csvName=args[2];
			maskPresent=false;
		}
		System.out.println("Map Aim: "+mapName);
		System.out.println("Canal Distance Aim: "+cDistName);
		System.out.println("Mask Distance Aim: "+mDistName);
		System.out.println("Output CSV: "+csvName);
		TomcatDB myDB=new TomcatDB();
		String dbName="Blanks";
		try {
			dbName=myDB.VMSCleanName(csvName);
			myDB.UpdateRecord("LACSH-"+dbName,"Run Started @ "+new Date()+"\n",false,"H");
		} catch (Exception e) {
			System.out.println("TomcatDB Problem");
		}
		long start = System.currentTimeMillis();
    

    	

		mapA=new VirtualAim(args[0]);
		mapA.ShortScaleFactor=(float) 1.0; // For the map we want the values to be preserved and not skewed
		VirtualAim cDisA=new VirtualAim(cDistName);
		VirtualAim mDisA=new VirtualAim();
		if (maskPresent) mDisA=new VirtualAim(mDistName);
		
		String execLine="";
		Vector CurSliceValues;
		if ((mapA.ischGuet) && (cDisA.ischGuet))  {
			LacunaShape maskLacuna=new LacunaShape();
			try {
				String dbOutString="";
				dbOutString+="LacunaShell Version:"+kVer+"\n";
				dbOutString+="VirtualAim  Version:"+mapA.kVer+"\n";
				dbOutString+="LacunaShape Version:"+maskLacuna.kVer+"\n\n";
				dbOutString+="Data Loaded in "+((System.currentTimeMillis()-start)/(60*1000F))+" mins @ "+new Date()+"\n";
				dbOutString+="Sample Name: "+mapA.sampleName+"\n";
				myDB.UpdateRecord("LACSH-"+dbName,dbOutString,"C");
			} catch (Exception e) {
				System.out.println("TomcatDB Problem");
			}
			try {
				String headerStr="// Sample: "+mapA.sampleName+", Map: "+args[0]+", Canal Dist : "+cDistName+", Mask Dist: "+mDistName+"\n";
				headerStr+="// SCALE_X, SCALE_Y, SCALE_Z, POS_X, POS_Y, POS_Z , STD_X, STD_Y, STD_Z, ";
				headerStr+="PCA1_X, PCA1_Y, PCA1_Z,PCA1_S,PCA2_X, PCA2_Y, PCA2_Z, PCA2_S, PCA3_S, OBJ_RADIUS, OBJ_RADIUS_STD, EDGE_RADIUS, EDGE_RADIUS_STD, VOLUME, Volume_Edge , VOLUME_BOX, ";
				// Canal
				headerStr+="Canal_Grad_X, Canal_Grad_Y, Canal_Grad_Z, Canal_Angle, Canal_Distance_Mean, Canal_Distance_COV, Canal_Distance_STD, ";
				// Mask
				headerStr+="Mask_Grad_X, Mask_Grad_Y, Mask_Grad_Z, Mask_Angle, Mask_Distance_Mean, Mask_Distance_COV, Mask_Distance_STD\n";
				FileWriter out = new FileWriter(csvName,false);
				out.write(headerStr);
				out.flush();
				out.close();
			} catch (Exception e) {
				System.out.println("Writing Output File Problem");
			}
			// Restart running time
			start = System.currentTimeMillis();
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
					// Make the program grab the edge as well
					curPt+=curPt%2;
					mapA.GetPoints(curPt-2,curPt,cSlice);
					System.out.println("Extracting Distances ("+mapA.positionList.size()+") Lacuna :"+curPt);
					// Canal Code
					cDisA.GetPointsFromList(mapA.positionList);
					LacunaShape canLacuna=new LacunaShape(cDisA.positionList,cDisA.valueList,mapA.valueList);
					canLacuna.CalcStats();
					// Mask Distance Code
					maskLacuna=new LacunaShape();
					if (maskPresent) {
						mDisA.GetPointsFromList(mapA.positionList);
						maskLacuna=new LacunaShape(mDisA.positionList,mDisA.valueList,mapA.valueList);
						maskLacuna.CalcStats();
					}
					try {
						String outStr="";
						String maskString="";
						outStr+=(curPt/2)+mapA.elSize.x+", "+mapA.elSize.y+", "+mapA.elSize.z+", ";
						if (maskPresent) {
							maskString=maskLacuna.DistString();
						} else {
							maskString="0,0,0,0,0,0,0";
						}
						outStr+=canLacuna.ShapeString()+", "+canLacuna.DistString()+", "+maskString+"\n";
						FileWriter out = new FileWriter(csvName,true);
						out.append(outStr);
						out.flush();
						out.close();
						// No more abusive traffic
						//myDB.UpdateRecord("LACGZ-"+myDB.VMSCleanName(args[2]),", ("+curPt+", "+(mapA.getSliceCalls+disA.getSliceCalls)+")");
					} catch(Exception e) {
						e.printStackTrace();
					}
					
					canLacuna=null;
					mapA.positionList=null;
					mapA.valueList=null;
					cDisA.positionList=null;
					cDisA.valueList=null;
					if (maskPresent) {
						maskLacuna=null;
						mDisA.valueList=null;
						mDisA.positionList=null;
					}
					System.gc();
				}
				itr=null;
				CurSliceValues=null;
				float sliceCalls=mapA.getSliceCalls+cDisA.getSliceCalls;
				if (maskPresent) sliceCalls+=mDisA.getSliceCalls;
				if ((sliceCalls)>1e10) {
					//Time to clean up
					System.out.println("Flushing VirtualAims after ( "+sliceCalls+") calls");
					mapA=null;
					cDisA=null;
					if (maskPresent) mDisA=null;
					System.gc();
					mapA=new VirtualAim(args[0]);
					mapA.ShortScaleFactor=(float) 1.0; // For the map we want the values to be preserved and not skewed
					cDisA=new VirtualAim(cDistName);
					if (maskPresent) mDisA=new VirtualAim(mDistName);
				}
				System.gc();
			}
		} else {
			System.out.println("Files Not Present");
		}
		try {
			float eTime=(System.currentTimeMillis()-start)/(60*1000F);
			String outString="\n"+"Lacuna Found "+AlreadyFound.size()+", Lacuna/Minute="+(AlreadyFound.size()/eTime)+"\n";
			float sliceCalls=mapA.getSliceCalls+cDisA.getSliceCalls;
			if (maskPresent) sliceCalls+=mDisA.getSliceCalls;
			outString+="Slices Read "+(sliceCalls)+", Slices/Second="+((sliceCalls)/(eTime*60.0))+"\n";
			outString+="Run Finished in "+eTime+" mins @ "+new Date()+"\n";
			
			myDB.UpdateRecord("LACSH-"+dbName,outString,"N");
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
				if (!AlreadyFound.contains(nB+nB%2)) {
					System.out.println("New Object Found : ("+(nB+nB%2)+" - "+(nB+nB%2+1)+")");
					AlreadyFound.add(nB+nB%2);
					curSlice.add(nB+nB%2);
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
				if (!AlreadyFound.contains(nB+nB%2)) {
					System.out.println("New Object Found : ("+(nB+nB%2-1)+" - "+(nB+nB%2)+")");
					AlreadyFound.add(nB+nB%2);
					curSlice.add(nB+nB%2);
				}
				
			}
		}
		return curSlice;
	}
}

		





	