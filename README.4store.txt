= 4store =
== install db ==
sudo 4s-backend-setup demo
== run ==
start:
sudo 4s-backend demo
== load data ==
http://4store.org/trac/wiki/ImportData
== stop ==
stop:
pkill -f '^4s-backend demo$'
== remove db ==
sudo 4s-backend-destroy demo (?)

= sparql http =
http://4store.org/trac/wiki/SparqlServer

