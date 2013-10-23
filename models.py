
class TagEdgeModel(Relationship):
    label = 'tag'

class FacetEdgeModel(Relationship):
    label = 'facet'

class FileEdgeModel(Relationship):
    label = 'file'

g.add_proxy('tagedges', TagEdgeModel)
g.add_proxy('facetedges',   FacetEdgeModel)
g.add_proxy('fileedges',    FileEdgeModel)
