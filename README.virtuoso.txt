sudo yum install virtuoso-opensource-doc virtuoso-opensource-utils virtuoso-opensource-conductor virtuoso-opensource-apps
(apps весит 92M, doc - 69M)
man /usr/share/doc/virtuoso/README
cd /var/lib/virtuoso/db
sudo virtuoso-t -f
http://localhost:8890/conductor/
log in as dba:dba
System Admin > Packages:
	Addressbook
	Calendar
	Demo
	SPAEQL demo
	Wiki
	doc	http://localhost:8890/doc/html/
	tutorial	http://localhost:8890/tutorial/
