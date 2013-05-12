# -*- coding: utf-8 -*-
# Neo4j test file
__author__ = 'sdvinfo@gmail.com'


import os
#from neo4j import GraphDatabase
#from py2neo import neo4j, rest
from neo4jrestclient import client
import codecs, sys
outf = codecs.getwriter('utf-8')(sys.stdout, errors='replace')
sys.stdout = outf

db=None
uri = "http://localhost:7474/db/data/"

#class Graph(object):
#    def __init__(self):
#        uri = "http://localhost:7474/db/data/"
#        try:
#            db = neo4j.GraphDatabaseService(uri)
#            print graph_db.neo4j_version
#            return db
#        except rest.NoResponse:
#            print "Cannot connect to host"
#        except rest.ResourceNotFound:
#            print "Database service not found"

class Person(object):
    def __init__(self,name,lname,mname,gender,ptype):
        self.name=name
        self.lname=lname
        self.mname=mname
        self.gender=gender
        self.ptype=ptype

    # def setProperties(self,birth_date=None,birth_place=None,email=None,inn=None,snils=None,enp=None):
    #     self.birth_date=birth_date
    #     self.birth_place=birth_place
    #     self.email=email
    #     self.inn=inn
    #     self.snils=snils
    #     self.enp=enp
        # ptype=None
        # name=None
        # lname=None
        # mname=None
        # gender=None
        # birth_date=None
        # birth_place=None
        # email=None
        # inn=None
        # snils=None
        # enp=None

class Employee(Person):
    # id=None
    # specialty=None
    # length_of_work=None
    # experience=None
    # pc_knowlegement=None
    # sociability=None

    def __init__(self,name,lname,mname,gender,specialty=None):
        #super(Person,self).__init__(self,name,lname,mname,gender,'Employee')
        Person.__init__(self,name,lname,mname,gender,'Employee')
        self.specialty=specialty

        # self.id=id
        # self.name = name
        # self.mname=super.mname
        # self.lname=super.lname
        # self.gender=super.gender
        # self.ptype='Employee'
        # self.birth_date=super.birth_date
        # self.birth_place=super.birth_place
        # self.email=super.email
        # self.inn=super.inn
        # self.snils=super.snils
        # self.enp=super.enp

    # def setProperties(self,birth_date=None,birth_place=None,email=None,inn=None,snils=None,enp=None,length_of_work=None,experience=None,pc_knowlegement=None,sociability=None):
    #     super(Employee,self).setProperties(birth_date,birth_place,email,inn,snils,enp)
    #     self.length_of_work=length_of_work
    #     self.experience=experience
    #     self.pc_knowlegement=pc_knowlegement
    #     self.sociability=sociability


    def addEmployee(self):
        pass


def addNode(db,name,age):
    with db.transaction:
    # Create a node
        n = db.node(name=name, age=age)
    return n


def main():
    db=None
    print('')

    while 1:
        print u'''
        Для теста системы введите:
        1 - Для соединения с БД
        2 - Ввод информации о сотруднике
        3 - Ввод связи между двумя нодами
        4 - Вывод списка нод графа
        5 - Выход
        '''
        print('')
        x = raw_input("Enter a choice: ")
        if x=='1':
            try:
                db = client.GraphDatabase(uri)
                print('\nConnected\n')
                print 'Version: ',db.VERSION
                print 'Nodes: ',db.nodes
            except:
                print('Could not connect to DataBase')
        elif x=='2':
            print 'Version: ',db.VERSION
            lname = raw_input(u'Фамилия: ')
            name = raw_input(u'Имя: ')
            mname = raw_input(u'Отчество: ')
            gender = raw_input(u'Пол: ')
            specialty = raw_input(u'Специальность: ')
            doctor = Employee(name=name,mname=mname,lname=lname,gender=gender,specialty=specialty)
            n = db.nodes.create(name=doctor.name,mname=doctor.mname,lname=doctor.lname,gender=doctor.gender,ptype=doctor.ptype,specialty=doctor.specialty)
            print u'Создан узел графа: ',n.lname,' ',n.name
            print 'id: ',n.id,' URL: ',n.url
            cort=n.properties
            for x in cort:
                print cort[x]
        elif x=='3':
            n1 = raw_input(u'ID первого узла: ')
            n2 = raw_input(u'ID второго узла: ')
            relname = raw_input(u'Тип связи (слово): ')
            print relname
            rel = db.relationships.create(n1,str(relname),n2)
            #rel = n1.relname(n2)
            print u'Создана связь: ',rel.start,' -> ',rel.end,' TYPE of REL: ',rel.type
        elif x=='4':
            print u'Выбор всех узлов:'
            q = 'START n=node(*), r=relationship(*) RETURN n, r;'
            result = db.query(q, returns=(client.Node, client.Relationship))

            for i in result:
                #db.nodes.get(i)
                print u'Узел: ',i[0].properties['firstname'],' id: ',i[0].id
                print u'Свойства узла: START:',i[1].start,' -> END:',i[1].end,' TYPE: ',i[1].type
                #print
                #print u'Связь: ', i
        elif x=='5':

            break



if __name__ == "__main__":
    os.system('clear')
    main()
