Djiki
=====
Djiki is a lightweight, portable Wiki engine based on Django.

Features:
    * Creole markup with minor extension for images (see below),
    * anonymous and registered edits,
    * automatic merges of parallel edits when possible.

Requirements
------------

    * google-diff-match-patch:
      http://code.google.com/p/google-diff-match-patch/

    * WikiCreole parser in Python:
      http://oink.sheep.art.pl/WikiCreole%20parser%20in%20python

    * sorl-thumbnail:
      *It is used in the example templates, but you may run djiki
      with any other thumbnailing module or without one at all.*
      https://github.com/sorl/sorl-thumbnail

Images
------

The standard Creole markup has been extended to handle resizing of
images. The standard syntax of ``{{Image_name.jpg|Image title}}`` is
still valid, however you may add size by typing
``{{Image_name.jpg|300x200|Image title}}`` or even omit the title:
``{{Image_name.jpg|300x200}}``.

Roadmap
-------

    * support for including images
    * older versions view, with diffs
    * simple reverts
    * ACLs: block anonymous edits, limit access to groups
    * more markup backends; MediaWiki is the main priority
    * page operations: rename, delete
    * translations
