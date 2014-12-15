/**
This class represents an array of disk-resident images.
*/
import ch.ethz.microct.aim.*;
import java.util.*;

class VirtualAim {
	private int viewPlane;
	private int zsize;
	private int xsize,ysize;
	private int nSlices;
	public int width,height;
	public int imageType;
	private AimIO AimEngine;
	private AimHeader TheHeader;
	D3int dim;
	D3int pos;
	D3int offset;
	D3float elSize;
	public boolean asMeasure;
	public boolean isConnected;
	public float ShortScaleFactor= (float) (1000.0/32767.0);
	Vector<Float[]> positionList;
	Vector<Float> valueList;
	public boolean ischGuet;
	public float getSliceCalls;
	String dataName;
	public String sampleName;
	public String kVer="001_090906";
	/** Creates a new, empty virtual stack. */
	
	public VirtualAim(String path) {
		AimEngine= new AimIO();
		if (AimEngine.read(path,false)) {
			isConnected=true;
			ischGuet=true;
			
			TheHeader=AimEngine.getHeader();
			//IJ.log("AIM Header:"+TheHeader.toString());
			dataName=TheHeader.getDataType();
			sampleName=TheHeader.getSampleName();
			System.out.println("VirtualAim [short] v"+kVer+" : Sample: "+sampleName+" AIM has been read as "+dataName);
			dim=TheHeader.getDim();
			pos=TheHeader.getPos();
			offset=TheHeader.getOff();
			elSize=TheHeader.getEl_size_mm();
			imageType=0;
			if (dataName.compareTo("Char")==0) imageType=0;
			if (dataName.compareTo("Short")==0) imageType=1;
			if (dataName.compareTo("Spec")==0) imageType=2;
			if (dataName.compareTo("Float")==0) imageType=3;
			xsize=dim.x;
			ysize=dim.y;
			zsize=dim.z;
			pos.x-=offset.x;
			pos.y-=offset.y;
			pos.z-=offset.z;
			System.out.println("Dimensions: "+dim.x+", "+dim.y+", "+dim.z);
			System.out.println("Position: "+pos.x+", "+pos.y+", "+pos.z);
			System.out.println("Element Size: "+elSize.x+", "+elSize.y+", "+elSize.z);
			System.out.println("Image Type: "+imageType);
			viewPlane=AimIO.XY;
			height=getHeight();
			width=getWidth();
			nSlices=getSlices()-1;
			asMeasure=false;
			getSliceCalls=0;
		} else {
			System.out.println("VirtualAim : ERROR AIM could not be read!");
			ischGuet=false;
		}
		//IJ.log("VirtualStack: "+path);
	}
	public VirtualAim() {
		ischGuet=false;
	}
	public void GetPointsFromList(Vector pList) {
		Iterator itr=pList.iterator();
		positionList=null;
		positionList=pList;
		valueList=null;
		valueList=new Vector(pList.size());
		short[] gg=new short[1];
		int lastRead=-1;
		//for (int i=0;i<pList.size();i++) {
		while (itr.hasNext()) {
			Float[] curPt=(Float[]) itr.next();//pList.elementAt(i);
			int curX=(int) curPt[0].floatValue()-pos.x;
			int curY=(int) curPt[1].floatValue()-pos.y;
			int curZ=(int) curPt[2].floatValue()-pos.z;
			//Debugging Message Only
			//System.out.println("VirtualAim : Fetching - "+curX+","+curY+","+curZ);
			if (curZ!=lastRead) {
				gg=getShortArray(curZ);
				lastRead=curZ;
			}
			float arrNum=(curY)*getWidth()+curX;
			if ((arrNum<gg.length) && (arrNum>=0)) {
				valueList.add(new Float(gg[(int) arrNum]*ShortScaleFactor));
			} else {
				valueList.add(new Float(0));
				System.out.println("AIM Sizes DO NOT MATCH!!!");
				System.out.println("Map Pixel  ("+curPt[0].floatValue()+","+curPt[1].floatValue()+","+curPt[2].floatValue()+") in ("+pos.x+","+pos.y+","+pos.z+")");
				System.out.println("Search for ("+curX+","+curY+","+curZ+") in ("+getHeight()+","+getWidth()+","+getSlices()+")");
			}
		}
		
	}
	public void GetPoints() {
		GetPoints(0,-1,0);
	}
	
	public void GetPoints(int minValue,int maxValue,int startSlice) {
		switch (this.imageType) {
			case 0:
				System.out.println("Byte Not Implemented Yet");
				break;
			case 1:
				System.out.println("Getting Points from Short Array From "+minValue+"->"+maxValue);
				GetShortPoints((short) minValue,(short) maxValue,startSlice);
				break;
			case 2:
				System.out.println("Getting Points from Integer Array From "+minValue+"->"+maxValue);
				GetIntPoints(minValue,maxValue,startSlice);
				break;
			case 3:
				System.out.println("Float Not Implemented Yet");
				break;
		}
	}
	
	public void GetIntPoints(int minValue,int maxValue,int startSlice) {
		int[] gg;
		int rCount=0;
		int bCount=0;
		float vSum=0;
		
		D3float npos;
		int defArraySize=Math.min((int) (dim.x*dim.y*dim.z*0.9),2000);
		positionList=new Vector(defArraySize);
		valueList=new Vector(defArraySize);
		for (int i=startSlice;i<getSlices();i++) {
			rCount=0;
			bCount=0;
			gg=getIntArray(i);
			for (int b: gg) {
				if (b>minValue) {
					if ((b<=maxValue) | (maxValue<minValue)) {
						npos=getrXYZ(rCount,i);
						Float[] cPos=new Float[3];
						cPos[0]=new Float(npos.x);
						cPos[1]=new Float(npos.y);
						cPos[2]=new Float(npos.z);
						//System.out.println("Cur Pt Get :"+cPos[0]+":"+cPos[1]+":"+cPos[2]);
						positionList.add(cPos);
						valueList.add(new Float(((float) b)));
						bCount++;
					}
				}
				rCount++;
			}
			if (bCount==0) {
				System.out.println("Empty Slice!");
				break;
			} //else 	System.out.println("Busy slice with  :"+bCount);
			gg=null;	
		}
		positionList.trimToSize();
		valueList.trimToSize();
	}
	
	public void GetShortPoints(short minValue,short maxValue,int startSlice) {
		short[] gg;
		int rCount=0;
		float bCount=0;
		float vSum=0;
		D3float npos;
		int defArraySize=Math.min((int) (dim.x*dim.y*dim.z*0.9),2000);
		positionList=new Vector(defArraySize);
		valueList=new Vector(defArraySize);
		for (int i=startSlice;i<getSlices();i++) {
			rCount=0;
			bCount=0;
			gg=getShortArray(i);
			for (short b: gg) {
				if (b>minValue) {
					if ((b<=maxValue) | (maxValue<minValue)) {
						npos=getrXYZ(rCount,i);
						Float[] cPos=new Float[3];
						cPos[0]=new Float(npos.x);
						cPos[1]=new Float(npos.y);
						cPos[2]=new Float(npos.z);
						positionList.add(cPos);
						vSum=(float) b;
						vSum*=ShortScaleFactor;
						valueList.add(new Float(vSum));
						bCount++;
					}
				}
				rCount++;
				
			}
			if (bCount==0) {
				System.out.println("Empty Slice!");
				break;
			}
			gg=null;	
		}
		positionList.trimToSize();
		valueList.trimToSize();
	}
	
	public short[] getShortArray(int n) {
		int wid=getWidth();
		int het=getHeight();
		getSliceCalls++;
		short[] bpixels;
		if (n<getSlices()) {
			bpixels=this.AimEngine.getShortPlane(this.viewPlane,n,wid,het);
		} else {
			System.out.println("!!AIM Read Violation : Attempted to Read Slice "+n+" of "+getSlices());
			bpixels=new short[1];
			bpixels[0]=0;
		}	
		return bpixels;
	}
	public int[] getIntArray(int n) {
		int wid=getWidth();
		int het=getHeight();
		getSliceCalls++;
		int[] bpixels;
		if (n<getSlices()) {
			bpixels=this.AimEngine.getIntPlane(this.viewPlane,n,wid,het);
		} else {
			System.out.println("!!AIM Read Violation : Attempted to Read Slice "+n+" of "+getSlices());
			bpixels=new int[1];
			bpixels[0]=0;
		}
		return bpixels;
	}		
	public void getArray(int n) {
		int wid=getWidth();
		int het=getHeight();
		//ImagePlus imp = new Opener().openImage(path, names[n-1]);
		float fpixels[]={};
		switch (this.imageType) {
			case 0:
				byte[] bpixels=this.AimEngine.getBytePlane(this.viewPlane,n,wid,het);
				//return bpixels;
			case 1:
				short[] spixels=this.AimEngine.getShortPlane(this.viewPlane,n,wid,het);
				//return spixels;
			case 2:
				int[] ipixels=this.AimEngine.getIntPlane(this.viewPlane,n,wid,het);
				//return ipixels;
			case 3:
				fpixels=this.AimEngine.getFloatPlane(this.viewPlane,n,wid,het);
				//return fpixels;
		}
		//return null;
	}
	private float[] byteToFloat(byte[] bpixels) {
		float[] fpixels=new float[bpixels.length];
		for (int i=0;i<bpixels.length;i++) {
			//System.out.println("Pixel: "+i);
			fpixels[i]=(float) bpixels[i];
		
		}
		return fpixels;
	}
	private float[] shortToFloat(short[] bpixels) {
		float[] fpixels=new float[bpixels.length];
		for (int i=0;i<bpixels.length;i++) {
			fpixels[i]=(float) bpixels[i];
		
		}
		return fpixels;
	}

	public D3float getrXYZ(int pixVal,int slicen) {
		D3float oPos=new D3float();
		D3int iPos=getXYZ(pixVal,slicen);
		if (asMeasure) {
			oPos.x=((float) iPos.x+(float) pos.x)*elSize.x;
			oPos.y=((float) iPos.y+(float) pos.y)*elSize.y;
			oPos.z=((float) iPos.z+(float) pos.z)*elSize.z;
		} else {
			oPos.x=((float) iPos.x+(float) pos.x);
			oPos.y=((float) iPos.y+(float) pos.y);
			oPos.z=((float) iPos.z+(float) pos.z);
		}
		return oPos;
	}
	public D3int getXYZ(int pixVal,int slicen) {
		int x,y,z;
		D3int oPos=new D3int();
		oPos.x=pixVal % getWidth();
		oPos.y=(pixVal-oPos.x) / getWidth();
		oPos.z=slicen;
		return oPos;
	}
	public int getWidth() {
		switch (viewPlane) {
		case AimIO.XY:
		case AimIO.XZ:
		case AimIO.O_XY:
		case AimIO.O_XZ:
			return xsize;
		case AimIO.YX:
		case AimIO.YZ:
		case AimIO.O_YX:
		case AimIO.O_YZ:
			return ysize;
		case AimIO.ZX:
		case AimIO.ZY:
		case AimIO.O_ZX:
		case AimIO.O_ZY:
			return zsize;
		}
		return 0;
	}
	public int getHeight() {
		switch (viewPlane) {
		case AimIO.YX:
		case AimIO.ZX:
		case AimIO.O_YX:
		case AimIO.O_ZX:
			return xsize;
		case AimIO.XY:
		case AimIO.ZY:
		case AimIO.O_XY:
		case AimIO.O_ZY:
			return ysize;
		case AimIO.XZ:
		case AimIO.YZ:
		case AimIO.O_XZ:
		case AimIO.O_YZ:
			return zsize;
		}
		return 0;
	}
	public int getSlices() {
		switch (viewPlane) {
		case AimIO.YX:
		case AimIO.XY:
		case AimIO.O_YX:
		case AimIO.O_XY:
			return zsize;
		case AimIO.YZ:
		case AimIO.ZY:
		case AimIO.O_YZ:
		case AimIO.O_ZY:
			return xsize;
		case AimIO.XZ:
		case AimIO.ZX:
		case AimIO.O_XZ:
		case AimIO.O_ZX:
			return ysize;
		}
		return 0;
	}
	public static void main(String[] args) {
		System.out.println("VirtualAim, manual mode");
		System.out.println("Loading "+args[0]+" ...");
		VirtualAim VA=new VirtualAim(args[0]);
	}
}