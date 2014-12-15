#caput X02DA-ES1-ROBO:LL-STATPAR.SCAN "Passive"
#camon X02DA-ES1-ROBO:LL-CROW & 
for iter in `seq 0 100`
do
	
	for i in `seq 0 9`;
	do
		
		for j in `seq 0 5`;
		do
			echo "Test $iter $j,$i"
			caput X02DA-ES1-ROBO:SM-READY 1
			sleep 1
			#caput X02DA-ES1-ROBO:LL-HRW_CON.PROC 1
			#sleep 1
			caput X02DA-ES1-ROBO:LL-SETR $j
			sleep 1
			caput X02DA-ES1-ROBO:LL-SETS $i
						
			#for kiter in `seq 0 20`;
			#do
			#for k in `seq 0 5`;
			#do
				#echo "Test $iter $k,$i"
			#	caput X02DA-ES1-ROBO:LL-SETR $k
			#	sleep 0.25
				#caget X02DA-ES1-ROBO:LL-CROW &
			#done
			#done
			#sleep 5
			sleep 1
			caput X02DA-ES1-ROBO:SM-READY 0
			sleep 2
			
		done
	done
done
