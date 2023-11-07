cd tmp
rm *.csv
/bin/python3 /home/funny_ppt/src/infrast-scheduler/main.py >res.out
rm ../b.zip
zip ../b.zip *.csv