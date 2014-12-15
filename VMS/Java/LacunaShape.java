//import org.math.array.*;
//import org.math.array.LinearAlgebra.*;
import java.awt.*;
import org.math.plot.*;
import Jama.*;
import ch.ethz.microct.aim.*;
import java.util.*;
// static import of all array methods : linear algebra and statistics
//import static org.math.array.LinearAlgebra.*;
//import static org.math.array.StatisticSample.*;
//import static org.math.array.*
/**
 * Copyright : BSD License
 * @author Kevin Mader
 * @category Lacuna Morphometry Analysis
 * @date 2009 09 06
 */

public class LacunaShape {

	double[][] X; // initial datas : lines = observations and columns = variables

	double[] meanX, stdevX;

	double[][] Z; // X centered reduced

	double[][] cov; // Z covariance matrix

	double[][] U; // projection matrix

	double[] info; // information matrix
	
	int prinCompJ; // which comp has the maximum variance explainations
	D3float com;
	D3float minbnd;
	D3float maxbnd;
	D3float wCom;
	D3float comVar;
	D3float prinComp;
	D3float secComp;
	public float mean;
	public double angCanPC;
	public float comVal;
	public float std;
	public boolean ischGuet;
	public float voxels;
	public float edgeVoxels;
	public float totalVoxels;
	public double prinScore;
	public double secScore;
	public double thirdScore;
	public float pxDistMean;
	public float pxDistStd;
	public float epxDistMean;
	public float epxDistStd;
	Vector positionList;
	Vector valueList;
	Vector oddEdgeList; 
	
	public String kVer="001_090906";
	
	public LacunaShape(VirtualAim vas) {
		ImportAIM(vas);
	}
	public LacunaShape(String filename) {
		VirtualAim vas=new VirtualAim(filename);
		ImportAIM(vas);
	}

	public LacunaShape(Vector _positions, Vector _values) {
		ischGuet=true;
		positionList=_positions;
		valueList=_values;
		oddEdgeList=new Vector();
	}
	public LacunaShape(Vector _positions, Vector _values, Vector _oddEdgeList) {
		ischGuet=true;
		positionList=_positions;
		valueList=_values;
		oddEdgeList=_oddEdgeList;
	}
	public LacunaShape() {
		//Pretty Boring
	}
	public boolean ImportAIM(VirtualAim vas) {
		ischGuet=vas.ischGuet;
		vas.GetPoints();
		positionList=vas.positionList;
		valueList=vas.valueList;
		return ischGuet;
	}
	
	public void CalcStats() {

		float vSum=0;
		com=new D3float();
		wCom=new D3float();
		minbnd=new D3float();
		minbnd.x=100000;
		minbnd.y=100000;
		minbnd.z=100000;
		maxbnd=new D3float();
		Float tempCval;
		float x,y,z,cVal;
		
		for (int i=0;i<positionList.size();i++) {
			Float[] cPoint=(Float[]) positionList.elementAt(i);
			x=cPoint[0].floatValue();
			y=cPoint[1].floatValue();
			z=cPoint[2].floatValue();
			tempCval=(Float) valueList.elementAt(i);
			cVal=tempCval.floatValue();
			//System.out.println("("+npos.x+", "+npos.y+", "+npos.z+")="+b);
			com.x+=x;
			com.y+=y;
			com.z+=z;
			wCom.x+=cVal*x;
			wCom.y+=cVal*y;
			wCom.z+=cVal*z;
			vSum+=cVal;
			
			if (x<minbnd.x) minbnd.x=x;
			if (y<minbnd.y) minbnd.y=y;
			if (z<minbnd.z) minbnd.z=z;
			if (x>maxbnd.x) maxbnd.x=x;
			if (y>maxbnd.y) maxbnd.y=y;
			if (z>maxbnd.z) maxbnd.z=z;
				
		}
		
		voxels=positionList.size();
		mean=vSum/voxels;
		
		com.x/=voxels;
		com.y/=voxels;
		com.z/=voxels;
		// wCom is weighted center of mass, weighted by distance map
		wCom.x/=vSum;
		wCom.y/=vSum;
		wCom.z/=vSum;
		// We are more interested in direction of the canal
		// so subtracting real COV and then normalizing
		wCom.x+=-com.x;
		wCom.y+=-com.y;
		wCom.z+=-com.z;
		
		double wComSum=vMag(wCom);
		if (wComSum>0) {
			wCom.x/=wComSum;
			wCom.y/=wComSum;
			wCom.z/=wComSum;
		}		
		
		totalVoxels=(float) (maxbnd.x-minbnd.x+1)*(maxbnd.y-minbnd.y+1)*(maxbnd.z-minbnd.z+1);
		
		CalcVar();
	}
	private void CalcVar() {
		
		float vSum=0;
		
		comVar=new D3float();
		comVal=mean;
		float x,y,z,cVal,pxDistTemp,epxCount;
		Float tempCval,tempEdgeVal;
		int edgeVal;
		pxDistMean=0;
		pxDistStd=0;
		epxDistMean=0;
		epxDistStd=0;
		epxCount=0;
		pxDistTemp=0;
		for (int i=0;i<positionList.size();i++) {
			Float[] cPoint=(Float[]) positionList.elementAt(i);
			x=cPoint[0].floatValue();
			y=cPoint[1].floatValue();
			z=cPoint[2].floatValue();
			tempCval=(Float) valueList.elementAt(i);
			cVal=tempCval.floatValue();
			//System.out.println("("+npos.x+", "+npos.y+", "+npos.z+")="+b);
			comVar.x+=Math.pow(com.x-x,2);
			comVar.y+=Math.pow(com.y-y,2);
			comVar.z+=Math.pow(com.z-z,2);
			
			pxDistTemp=(float) Math.sqrt(Math.pow(com.x-x,2)+Math.pow(com.y-y,2)+Math.pow(com.z-z,2));
			pxDistMean+=pxDistTemp;
			pxDistStd+=(float) Math.pow(pxDistTemp,2);
			// Just the predetermined edge pixels
			if (oddEdgeList.size()==positionList.size()) {
				tempEdgeVal=(Float) valueList.elementAt(i);
				edgeVal=(int) tempCval.floatValue();
				
				if (edgeVal%2 >= 1) {
					epxDistMean+=pxDistTemp;
					epxDistStd+=(float) Math.pow(pxDistTemp,2);
					epxCount+=1;
				}
			}
			if ((Math.round(com.x)==Math.round(x)) && (Math.round(com.y)==Math.round(y)) && (Math.round(com.z)==Math.round(z))) comVal=cVal;
			vSum+=Math.pow(cVal-mean,2);

		}
		comVar.x=(float) Math.sqrt(comVar.x/positionList.size());
		comVar.y=(float) Math.sqrt(comVar.y/positionList.size());
		comVar.z=(float) Math.sqrt(comVar.z/positionList.size());
		std=(float) Math.sqrt(vSum/positionList.size());
		pxDistMean/=positionList.size();
		pxDistStd=(float) Math.sqrt(pxDistStd/positionList.size()-Math.pow(pxDistMean,2));
		if (epxCount>0) {
			epxDistMean/=epxCount;
			epxDistStd=(float) Math.sqrt(epxDistStd/epxCount-Math.pow(epxDistMean,2));
			edgeVoxels=epxCount;
		} else {
			epxDistMean=0;
			epxDistStd=0;
			edgeVoxels=0;
		}
		//System.out.println("COMvar : ("+comVar.x+", "+comVar.y+", "+comVar.z+"), Std: "+std+", Voxels: "+voxels);
		//System.out.println("Mean Distance: "+mean+", Dist@COV: "+comVal);
		//System.out.println("Lacuna Voxels: "+voxels+", Total Voxels: "+totalVoxels+", Blockiness:"+((float) 100.0*voxels/totalVoxels));
		
		//System.out.println("Point List")
		
		CalcLacunParams();
	}
	private void CalcLacunParams() {
		if (voxels>5) { // Need at least 5 voxels to run PCA
			PCA();
			//TestL.print();
			double[] lacDir=getComp();
			prinScore=getScore();
			prinComp=new D3float();//(lacDir[0],lacDir[1],lacDir[2]);
			prinComp.x=(float) lacDir[0];
			prinComp.y=(float) lacDir[1];
			prinComp.z=(float) lacDir[2];
			System.out.println("PC1 : ("+prinComp.x+", "+prinComp.y+", "+prinComp.z+")");
			lacDir=getComp(1);
			secScore=getScore(1);
			secComp=new D3float();//(lacDir[0],lacDir[1],lacDir[2]);
			secComp.x=(float) lacDir[0];
			secComp.y=(float) lacDir[1];
			secComp.z=(float) lacDir[2];
			System.out.println("PCA Successful! First Comp - "+prinScore);
			thirdScore=getScore(0);
		} else {
			prinScore=0;
			System.out.println("PCA Skipped too few voxels:"+voxels+"! First Comp - "+prinScore);
			prinComp=new D3float();//(lacDir[0],lacDir[1],lacDir[2]);
			prinComp.x=(float) 0;
			prinComp.y=(float) 0;
			prinComp.z=(float) 0;
			System.out.println("PC1 : ("+prinComp.x+", "+prinComp.y+", "+prinComp.z+")");
			secScore=0;
			thirdScore=0;
			secComp=new D3float();//(lacDir[0],lacDir[1],lacDir[2]);
			secComp.x=(float) 0;
			secComp.y=(float) 0;
			secComp.z=(float) 0;
		}
		CalcAngles();
		//TestL.view();
		
	}
	private void CalcAngles() {
		angCanPC=vAngleToPC(wCom,prinComp);
		
		System.out.println("Deviation of Lacuna PA from Canal Gradient :"+angCanPC);
		System.out.println("Deviation of Lacuna 2PA from Canal Gradient :"+vAngleToPC(wCom,secComp));
	}
	public void PCA(double[][] _X) {
		X = _X;
		PCA();
	}
	public void PCA() {
		X=new double[positionList.size()][3];
		for (int i=0;i<positionList.size();i++) {
			Float[] cPoint=(Float[]) positionList.elementAt(i);
			X[i][0]=cPoint[0].floatValue();
			X[i][1]=cPoint[1].floatValue();
			X[i][2]=cPoint[2].floatValue();
		}
		
		stdevX = stddeviation(X);
		meanX = mean(X);

		Z = center_reduce(X);

		cov = covariance(Z);

		EigenvalueDecomposition e = new EigenvalueDecomposition(new Matrix(cov));
		//U =e.getV().getArray();
		U = e.getV().transpose().getArray();
		info = e.getRealEigenvalues(); // covariance matrix is symetric, so only real eigenvalues...
		double maxComp=info[0];
		for (int i=0;i<info.length;i++) {
			if (info[i]>=maxComp) 
			{
				prinCompJ=i;
				maxComp=info[i];
			} 
		}
		
	}
	public double vAngleToPC(D3float p1,D3float pc) {
		D3float npc=new D3float();
		npc.x=-pc.x;
		npc.y=-pc.y;
		npc.z=-pc.z;
		return Math.min(vAngle(p1,pc),vAngle(p1,npc));
	}
	public double vAngle(D3float p1,D3float p2) {
		double sVal=p1.x*p2.x+p1.y*p2.y+p1.z*p2.z;
		sVal/=(vMag(p1)*vMag(p2));
		return Math.toDegrees(Math.acos(sVal));
		
	}
	public double vMag(D3float p1) {
		return Math.sqrt(Math.pow(p1.x,2)+Math.pow(p1.y,2)+Math.pow(p1.z,2));
	}
	public double getScore() {
		return getScore(prinCompJ);
	}
	public double getScore(int compNum) {
		double infoSum=0;
		for (int i=0;i<info.length;i++) infoSum+=info[i];
		return info[compNum];// /infoSum;
		// We dont want no stinkin normalized scores
	}
	public double[] getComp() {
		return getComp(prinCompJ);
	}
	public double[] getComp(int compNum) {
		return U[compNum];
		//return inv_center_reduce(U[compNum]);
	}
	public static double stddeviation(double[] v) {
        return Math.sqrt(variance(v));
    }

    public static double variance(double[] v) {
        double var;
        int degrees = (v.length - 1);
        int m = v.length;
        double c;
        double s;
        c = 0;
        s = 0;
        for (int k = 0; k < m; k++)
            s += v[k];
        s = s / m;
        for (int k = 0; k < m; k++)
            c += (v[k] - s) * (v[k] - s);
        var = c / degrees;
        return var;
    }

    public static double[] stddeviation(double[][] v) {
        double[] var = variance(v);
        for (int i = 0; i < var.length; i++)
            var[i] = Math.sqrt(var[i]);
        return var;
    }

    public static double[] variance(double[][] v) {
        int m = v.length;
        int n = v[0].length;
        double[] var = new double[n];
        int degrees = (m - 1);
        double c;
        double s;
        for (int j = 0; j < n; j++) {
            c = 0;
            s = 0;
            for (int k = 0; k < m; k++)
                s += v[k][j];
            s = s / m;
            for (int k = 0; k < m; k++)
                c += (v[k][j] - s) * (v[k][j] - s);
            var[j] = c / degrees;
        }
        return var;
    }
    public static double[] mean(double[][] v) {
        int m = v.length;
        int n = v[0].length;
        double[] mean = new double[n];
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                mean[j] += v[i][j];
        for (int j = 0; j < n; j++)
            mean[j] /= (double) m;
        return mean;
    }
	 public static double[][] covariance(double[][] v) {
	        int m = v.length;
	        int n = v[0].length;
	        double[][] covMat = new double[n][n];
	        int degrees = (m - 1);
	        double c;
	        double s1;
	        double s2;
	        for (int i = 0; i < n; i++) {
	            for (int j = 0; j < n; j++) {
	                c = 0;
	                s1 = 0;
	                s2 = 0;
	                for (int k = 0; k < m; k++) {
	                    s1 += v[k][i];
	                    s2 += v[k][j];
	                }
	                s1 = s1 / m;
	                s2 = s2 / m;
	                for (int k = 0; k < m; k++)
	                    c += (v[k][i] - s1) * (v[k][j] - s2);
	                covMat[i][j] = c / degrees;
	            }
	        }
	        return covMat;
	    }
	// normalization of x relatively to X mean and standard deviation
	public double[][] center_reduce(double[][] x) {
		double[][] y = new double[x.length][x[0].length];
		for (int i = 0; i < y.length; i++)
			for (int j = 0; j < y[i].length; j++)
				y[i][j] = (x[i][j] - meanX[j]);// / stdevX[j]; Ignore STD
		return y;
	}

	// de-normalization of y relatively to X mean and standard deviation
	public double[] inv_center_reduce(double[] y) {
		return inv_center_reduce(new double[][] { y })[0];
	}

	// de-normalization of y relatively to X mean and standard deviation
	public double[][] inv_center_reduce(double[][] y) {
		double[][] x = new double[y.length][y[0].length];
		for (int i = 0; i < x.length; i++)
			for (int j = 0; j < x[i].length; j++)
				//x[i][j] = (y[i][j] * stdevX[j]) + meanX[j];
				x[i][j] = (y[i][j]) + meanX[j];
		return x;
	}

	public void view() {
		// Plot
		Plot3DPanel plot = new Plot3DPanel();

		// initial Datas plot
		plot.addScatterPlot("datas", X);

		// line plot of principal directions
		double[] tempLineX,tempLineY,tempLineZ;
		double[] normU;
		
		normU=inv_center_reduce(U[prinCompJ]);
		tempLineX=new double[2];
		tempLineY=new double[2];
		tempLineZ=new double[2];
		tempLineX[0]=meanX[0];
		tempLineX[1]=normU[0];
		tempLineY[0]=meanX[1];
		tempLineY[1]=normU[1];
		tempLineZ[0]=meanX[2];
		tempLineZ[1]=normU[2];
		
		plot.addLinePlot("Big %", tempLineX,tempLineY,tempLineZ);
		//plot.addLinePlot(Math.rint(info[1] * 100 / sum(info)) + " %", meanX, inv_center_reduce(U[1]));

		// display in JFrame
		new FrameView(plot);
	}
	public String DistString() {
		String outStr;
		// center of distance-mass
		outStr=wCom.x+","+wCom.y+","+wCom.z;
		// Distance Metrics
		outStr+=","+angCanPC+", "+mean+","+comVal+","+std;
		
		return outStr;
	}
	public String ShapeString() {
		String outStr;
		// center of volume
		outStr=com.x+", "+com.y+","+com.z;
		// variance
		outStr+=", "+comVar.x+","+comVar.y+", "+comVar.z;
		// PCA1
		outStr+=", "+prinComp.x+","+prinComp.y+","+prinComp.z+","+prinScore;
		// PCA2 - 3
		outStr+=", "+secComp.x+","+secComp.y+", "+secComp.z+","+secScore+","+thirdScore;
		// Radius, Radius STD, Edge Radius, Edge Radius Std
		outStr+=","+pxDistMean+","+pxDistStd+","+epxDistMean+","+epxDistStd;
		// Volume, Box Volume
		outStr+=","+voxels+","+edgeVoxels+","+totalVoxels;
		return outStr;
	}
	public String toString() {
		return ShapeString()+","+DistString()+"\n";
	}
	public void print() {
		// Command line display of results 
		//System.out.println("le data\n" +  DoubleArray.toString(X));
		System.out.println("MIN : ("+minbnd.x+", "+minbnd.y+", "+minbnd.z+")");
		System.out.println("COM : ("+com.x+", "+com.y+", "+com.z+")");
		System.out.println("wCOM : ("+wCom.x+", "+wCom.y+", "+wCom.z+")");
		System.out.println("MAX : ("+maxbnd.x+", "+maxbnd.y+", "+maxbnd.z+")");
		System.out.println("Mean Length "+meanX.length);
		System.out.println("Mean U0 "+inv_center_reduce(U[0]).length);
		System.out.println("InfoLen "+info.length);
		double infoT=info[0]+info[1]+info[2];
		for (int i=0;i<3;i++) {
			System.out.println("Projection Vectors "+info[i]+" : "+U[i][0]+", "+U[i][1]+", "+U[i][2]);
		}
		//System.out.println("projection vectors\n" +  DoubleArray.toString(transpose(U)));
		//System.out.println("information per projection vector\n" + DoubleArray.toString(info));
		
	}

	public static void main(String[] args) {
		//VirtualAim VA=VirtualAim(filename);
		//VA.GetPoints();
		//LacunaShape myLacuna=new LacunaShape(VA.positionList,VA.valueList);
		Vector<Float[]> positionList=new Vector();
		Vector<Float> valueList=new Vector();
		float xstretch=25;
		float ystretch=25;
		float zstretch=25;
		for (float x=5;x<15;x++) {
			for (float y=5;y<15;y++) {
				for (float z=5;z<15;z++) {
					if (Math.sqrt(Math.pow(x-10,2)/xstretch+Math.pow(y-10,2)/ystretch+Math.pow(z-10,2)/zstretch)<=1) {
						Float[] cPos=new Float[3];
						cPos[0]=new Float(x);
						cPos[1]=new Float(y);
						cPos[2]=new Float(z);
						positionList.add(cPos);
						valueList.add(new Float(Math.sqrt(Math.pow(x,2)+Math.pow(y,2)+Math.pow(z,2))));
					}	
				}
			}
		}
		//LacunaShape myLacuna=new LacunaShape(args[0]);
		LacunaShape myLacuna=new LacunaShape(positionList,valueList);
		myLacuna.CalcStats();
		myLacuna.print();
		System.out.println("Stats:"+myLacuna);
		
	}

}