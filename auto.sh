if cd /var/www/html/autosf; then
	logfile="autoserver.log";
	stamp=`date '+%Y-%m-%d %H:%M:%S'`;
	echo "[date] $stamp" >>$logfile;
	python auto_con.py sync click>>$logfile 2>&1
	find /home/xling/Downloads/sfreport/ -mtime 1 -name "report*.xls" |xargs -r rm
	#python auto_con.py clonecheck clonecheck all >>$logfile 2>&1
	#php autoimport.php case >>$logfile 2>&1
fi
