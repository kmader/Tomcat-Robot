#! /bin/sh
javac -classpath ./:./JAR/JAIMPACK.JAR:./JAR/jmatharray.jar:./JAR/jmathplot.jar -sourcepath ./ -target 1.5 *.java
java -classpath ./:JAIMPACK.JAR:jmatharray.jar:jmathplot.jar LacunaShape
# java -classpath ./:JAIMPACK.JAR:jmatharray.jar:jmathplot.jar TomcatDB SEARCH peteypablo raiseup -1 LACSH
java -classpath ./:JAIMPACK.JAR:jmatharray.jar:jmathplot.jar TomcatDB VIEW peteypablo raiseup -1 71587