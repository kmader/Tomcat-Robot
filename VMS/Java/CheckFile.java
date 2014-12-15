import java.io.*;
public class CheckFile {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		 File f = new File(args[0]);
		 if (f.exists()) {
			 System.out.println(args[0]+" is present, script will continue");
		 } else {
			 System.out.println(args[0]+" is missing, script will abort");
			 String execLine="";
			 if (args.length<2) {
					execLine="$ DELETE/ENTRY='JOB_NR'  \n";
				} else {
					//execLine="sue:kill_task.com "+args[2];
					execLine="$ DELETE/ENTRY="+args[1]+"  \n";
				}
			 	for (int i=2;i<args.length;i++) execLine+=execLine="$ DELETE "+args[1]+";*  \n";
				ExecTask killMe=new ExecTask(execLine);
		 }

	}

}
