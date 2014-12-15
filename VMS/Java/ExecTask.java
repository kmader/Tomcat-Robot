import java.awt.image.*;
import java.awt.image.ColorModel.*;
import java.io.*;
import java.net.*;
import java.security.Principal;
import java.util.*;
import java.io.IOException;
import java.io.PrintStream;
import java.net.InetAddress;
import java.lang.Math;
import java.awt.event.*;
class ExecTask {
	public ExecTask(String cmds) {
		String submitterFilename = "EvalService_KMNT.com";
		File submitterFile = new File(submitterFilename);
		FileOutputStream fos;
		String submitCommand = "$! Submitter file created by kmoment.java\n";
		submitCommand += "$! " + new Date() + "\n";
		submitCommand += "$! =============================================================================\n";
		submitCommand += "$! \n";
		submitCommand += "$! \n";
		submitCommand += "$! Execute commands from file.\n";
		submitCommand += "$! --------------------\n";
		submitCommand += cmds;
		submitCommand += "$! \n";
		submitCommand += "$! \n";
		submitCommand += "$! Delete this procedure.\n";
		submitCommand += "$! ----------------------\n";
		submitCommand += "$ PROC = F$ENVIRONMENT(\"PROCEDURE\")\n";
		submitCommand += "$ PROC = F$SEARCH(PROC)\n";
		submitCommand += "$ DELETE \'PROC\'\n";
		submitCommand += "$! \n";
		submitCommand += "$! \n";
		submitCommand += "$ EXIT";
		
		try {
			fos = new FileOutputStream(submitterFile);
			fos.write(submitCommand.getBytes());
			fos.flush();
			fos.close();
			String line="";
			String retVal="";
			Runtime rt = Runtime.getRuntime();
			Process p = rt.exec(submitterFilename);
			BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));
			BufferedReader stdError = new BufferedReader(new InputStreamReader(p.getErrorStream()));
			while ((line = stdInput.readLine()) != null) {
				retVal += line;
				System.out.println(line);
			}
			stdInput.close();
			while ((line = stdError.readLine()) != null) {
				retVal += line;
				System.err.println(line);
			}
			stdError.close();
			int exitCode = p.exitValue();
		} catch (Exception e) {
			System.out.println("Error Executing Task");
			e.printStackTrace();
		}
	}
}