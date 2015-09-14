  * Each file has per-file metadata and links to tags
  * tags are:
    * hiearchical
    * in facets
    * facets are context

Simpler:

  * tags == folders
  * folders are nestable
  * some folders can't contain files
  * file can be in some folders in simultaneously

# Specification #

## Queries ##
### UI > Core ###
  * set current tag (!ro)
    * get used facets and facet tags
    * get available facets and facet tags
    * get used sub-tags
    * get available sub-tags
    * get files
  * set current file
    * get used tags
    * get available faces and facet tags (???)
### Core -> DB ###
  * GetNode(id): Node

## DB structure ##

### Nodes ###
  * `<all>`
    * _parms_: None
    * _constraints_: None
  * **Facet**: _must_ contain Tag
    * _parms_:
      * name:str
      * multiple:bool - multiple tags of this Facets can be applied to File
      * mandatory:bool=True
    * _constraints_: None
  * **Tag**:
    * _parms_:
      * name:str
      * ro:bool - True=can't contains File
    * _constraints_:
      * oncreate & ro: add 2+ edges of self->Tag
      * name: unique in its parent (Facet/Tag)
  * **File**:
    * _parms_:
      * size:int
      * md5:uint128
      * filename:str
    * _constraints_: None

### Edges ###
Compatibility matrix:
| F\T   | / | Facet | Tag | File |
|:------|:--|:------|:----|:-----|
| /     | - |  ?    | ?   | 1:M  |
| Facet | - |   -   | 1:M |  -   |
| Tag   | - |  M:M  | 1:M | -/M:M |
| File  | - |   -   |  -  | ?:?  |

  * / -> `<all>`: ...
  * / -> file: unsorted files.
    * _constraints_:
      * File name must be unique.
  * Facet -> Tag: the only edge to Tag; name = 'include'.
  * Tag -> Facet:
    * _parms_:
      * onlyfor:bool - facet appliable for this Folder but not for children
    * _constraints_: None
  * Tag -> Tag: nested tags if File can be as in parent as in child tag (e.g. DocType -> DocSubType).
  * Tag -> File:
    * _parms_: None
    * _constraints_:
      * File can't has as Tag as it's child/parent simultaneously
    * File can has any Tag from:
      * / childen Tags
      * sub-TagGroup from / to applied
  * File -> File: sequience and/or X-link
    * _constraints_:
      * File sequence/X-links can't contain loops (a File can't be twice in sequence/X-links chains)
      * => File can be in one sequence and one X-links group (?)

### Questions ###
  * Move TagGroup through hierarchy (up-down)
  * / = Tag | Facet?
  * Tag(file=bool) == Facet?
  * Super-node Class? (Tag/File etc)
  * Really srict hierarchy of tags?
  * Must depricate X-tags upper then defined level (like - music tags and documens ones)
  * Maybe - tags have "compatibility table"?
  * == a kind of "scheme"
  * what about "SubClassOf" and "ChildOf" parameters? (RTFM RDF/OWL)
  * => SemaWeb :-)
  * DB independen
  * Organizations - clients or not => tags can have tags/metadata too (!) => semaweb

## UI ##

# Ideas #
  * Node/Edge "processors" = _nodename_.py - parms handle, triggers etc.
  * folder parm: "OnlyFor": list of folders (with or without children) == Tag -> Facet
  * Other nodes: contact, task, address