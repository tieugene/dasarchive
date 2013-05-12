# foaf:phone (tel:+7-812-334-05-15|+7-812-3340515|+78123340515,  - rfc3966)

TODO:
	* list all attributes/predicates (maybe - via rdf_type + namespaces
	* 

SurfRDF advantages:
	* predefined ns' (file:///usr/share/doc/python-surfrdf-1.1.4/html/modules/namespace.html)
	* mapper
	* SPARQL (to rdflib too?)

Use for:
	* lansite
	* doxgen
	* PIM
Classes:
	* Document (doxgen)
	* Media (audio, picture, video)
	* Tasks (vcard)
	* REFs
	* Address?
	* Contact (vcard)
Used schemes:
	* w3c:
		* vcard: http://www.w3.org/2006/vcard/ns
		* Calendar: http://www.w3.org/2002/12/cal/
		* Media resources: http://www.w3.org/ns/ma-ont.rdf
		* Organization: http://www.w3.org/ns/org#
		* FOAF: http://xmlns.com/foaf/0.1/
		* Geo: http://www.w3.org/2003/01/geo/wgs84_pos#
		* ZIP: http://www.daml.org/2001/10/html/zipcode-ont
	* http://www.semanticdesktop.org/ontologies/:
		* Dublin Core (DC)
		* Nepomuk (calendar, contact, exif, file, id3, multimedia, message)
		* PIM (Personal Infomation Model)
		* TM (Task Model)
	* ordf:
		* BIBO = Namespace("http://purl.org/ontology/bibo/")	Bibliographica
		BIO = Namespace("http://purl.org/vocab/bio/0.1/")	
		CS = Namespace("http://purl.org/vocab/changeset/schema#")
		DBPPROP = Namespace("http://dbpedia.org/property/")
		DCES = Namespace("http://purl.org/dc/elements/1.1/")
		DC = Namespace("http://purl.org/dc/terms/")
		DCAM = Namespace("http://purl.org/dc/dcam/")
		DOAP = Namespace("http://usefulinc.com/ns/doap#")
		FRBR = Namespace("http://purl.org/vocab/frbr/core#")
		FRESNEL = Namespace("http://www.w3.org/2004/09/fresnel#")
		GND = Namespace("http://d-nb.info/gnd/")
		GR = Namespace("http://bibliographica.org/schema/graph#")
		* ICAL = Namespace("http://www.w3.org/2002/12/cal/ical#")
		* LIST = Namespace("http://www.w3.org/2000/10/swap/list#")
		LOG = Namespace("http://www.w3.org/2000/10/swap/log#")
		MOAT = Namespace("http://moat-project.org/ns#")
		OPMV = Namespace("http://purl.org/net/opmv/ns#")
		ORDF = Namespace("http://purl.org/NET/ordf/")
		ORE = Namespace("http://www.openarchives.org/ore/terms/")
		* OWL = Namespace("http://www.w3.org/2002/07/owl#")
		RDAGR2 = Namespace("http://RDVocab.info/ElementsGr2/")
		RDARELGR2 = Namespace("http://metadataregistry.org/uri/schema/RDARelationshipsGR2/")
		RDFG = Namespace("http://www.w3.org/2004/03/trix/rdfg-1/")
		* RELATIONSHIP = Namespace("http://purl.org/vocab/relationship/")
		REV = Namespace("http://purl.org/stuff/rev#")
		SCOVO = Namespace("http://purl.org/NET/scovo#")
		SIOC = Namespace("http://rdfs.org/sioc/ns#")
		SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
		* TIME = Namespace("http://www.w3.org/2006/time#")
		VOID = Namespace("http://rdfs.org/ns/void#")
		WOT = Namespace("http://xmlns.com/wot/0.1/")
		* UUID = Namespace("urn:uuid:")
	* misc:
		* iso3166: <http://www.daml.org/2001/09/countries/iso-3166-ont#>
		* http://www.daml.org/ontologies/