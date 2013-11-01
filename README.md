Stand-Alone Mediaplayer for the Raspberry Pi

* Web-based config tool
* Playback service with [omxplayer](


Includes
========
* Bootstrap 3 (17.9.2013)
* Branch Willi erstellt (24.09.2013)

Quick Start
===========
Create a project directory, setup virtualenv, clone the project and setup the dependencies:

	# Clone django-boilerplate into project directory
    $ git clone ...
    $ cd <YOUR_PROJECT_DIR>

	# Create and activate virtualenv, and install dependencies
	$ virtualenv env
	$ . env/bin/activate
    $ pip install -r dependencies.txt

    # Build bootstrap for the first time
    $ cd app/static/twitter-bootstrap
    $ make bootstrap



Schema Migrations
-----------------
Initial DB Setup:

    $ ./manage.py schemamigration main --initial
    $ ./manage.py syncdb
    $ ./manage.py migrate main


After changing a model we need to create the migration file, and then apply it to update the schema in the database:

    # Create migration file
    $ ./manage.py schemamigration main --auto

    # Apply migration
    $ ./manage.py migrate main


Tips & Tricks
=============
* Djangop Cheat Sheet: http://www.mercurytide.co.uk/media/resources/django-cheat-sheet-a4.pdf
* Fixtures:
** Create for specific model with `./manage.py dumpdata --format=json main.Heater > fixtures/heater.json`
** Load back into db with `./manage.py loaddata fixtures/heater.json`
