Djiki
=====
Djiki is a lightweight, portable Wiki engine based on Django.

Features:
    * Creole markup,
    * anonymous and registered edits,
    * automatic merges of parallel edits when possible,
    * inclusion of images,
    * diff views between revisions,
    * reverts to any revision in the history,
    * automatic undos of any historical revision, if possible.

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

Usage
-----
 * Add 'djiki' and 'sorl.thumbnail' to your INSTALLED_APPS setting.
 * Run './manage.py syncdb' in your project.
 * Add the following to your URLconf::

     (r'wiki/', include('djiki.urls')),

 * Add the required setting DJIKI_IMAGES_PATH
 * Create a 'base.html' that Djiki expects to exist and acts as a base template
   for all the wiki pages. It must have a 'page' block. Alternatively, supply
   your own 'djiki/base.html' that overrides the supplied template.
 * Optionally include/add the provided CSS in media/css/styles.css to your page
   template.

Settings
--------

The following settings configure Djiki's behavior:

``DJIKI_IMAGES_PATH`` — path to images, relative to MEDIA_ROOT.

``DJIKI_ALLOW_ANONYMOUS_EDITS`` — whether unauthorized users are
able to edit pages. Defaults to True.

``DJIKI_SPACES_AS_UNDERSCORES`` — makes Djiki replace whitespaces in
URLs by underscores. It's a choice between having nice or exact URLs.
Depending on the settings, the adresses may look as
``http://djiki.org/wiki/Main_Page`` or ``http://djiki.org/wiki/Main%20Page``
This setting will also squash multiple spaces into one. It affects image
names in the same way, too. Defaults to True.

Images
------

The standard Creole markup has been extended to handle resizing of
images. The standard syntax of ``{{Image_name.jpg|Image title}}`` is
still valid, however you may add size by typing
``{{Image_name.jpg|300x200|Image title}}`` or even omit the title:
``{{Image_name.jpg|300x200}}``.

Roadmap
-------

    * ACLs: block anonymous edits, limit access to groups
    * more markup backends; MediaWiki is the main priority
    * page operations: rename, delete
    * translations
