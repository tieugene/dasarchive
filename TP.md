Resriction: 1-level tags

# 1. UI #

  * Tags: path, tree, graph
  * Files; ...
  * Filter: path w/ dropdowns, tree with checkboxes/radios

# 2. Modes #

## 2.1. CRUD tags ##

### Create ###

  * Tag: facet (uniq name through sibling facets)
  * Facet: tag (the same)

### Update ###

  * Tag, Facet: rename (uniq)
  * Tag, facet: move
  * Tag, Facet: merge

### Delete ###

## 2.2. CRUD files ##

  * Add file (enable root)
  * Add tag (enable children facets)
  * Add tag recursively
  * Change tag
  * Del tag (del all childen)

## 2.3. Filter ##

  * Add tag
  * Add tag recursively
  * Change tag
  * Del tag

# 3. API #

## 3.1. Data struct ##

  * Graph:
    * get\_node(id):Node
  * Node:
    * name:str
    * get\_parent():Node
    * get\_children():Node
    * add\_child(Node)
    * del\_child(Node)
    * get\_name()
    * set\_name(str)
  * Facet(Node):
    * multiple:bool=False
    * mandatory:bool=False
  * Tag(Node)

# 4. Storage #

  * Neo4j
  * SQL