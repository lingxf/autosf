if cd /home/xling/work/report; then
	logfile="autoserver.log";
	stamp=`date '+%Y-%m-%d %H:%M:%S'`;
	echo "[date] $stamp" >>$logfile;
	python auto_con.py sync click>>$logfile 2>&1
	find /home/xling/Downloads/sfreport/ -mtime 1 -name "report*.xls" |xargs rm
	sleep 180
	find /home/xling/Downloads/sfreport/ -type f -mmin -30|xargs -r -I ff scp -p ff cedump-sh:Downloads/sfreport
	#python auto_con.py clonecheck clonecheck all >>$logfile 2>&1
	#php autoimport.php case >>$logfile 2>&1
fi
