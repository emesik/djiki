Djiki
=====
Djiki is a lightweight, portable Wiki engine based on Django.

Features:
    * Creole markup,
    * anonymous and registered edits,
    * automatic merges of parallel edits when possible.

Requirements
------------

    * google-diff-match-patch:
      http://code.google.com/p/google-diff-match-patch/

    * WikiCreole parser in Python:
      http://oink.sheep.art.pl/WikiCreole%20parser%20in%20python

    * sorl-thumbnail:
      *It is used in the example project, but you may run djiki
      with any other thumbnailing module or without one at all.*
      https://github.com/sorl/sorl-thumbnail

Roadmap
-------

    * support for including images
    * older versions view, with diffs
    * simple reverts
    * ACLs: block anonymous edits, limit access to groups
    * more markup backends; MediaWiki is the main priority
    * page operations: rename, delete
    * translations
