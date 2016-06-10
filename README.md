[logo]: https://udacity.com/favicon.ico "Udacity"
![Udacity][logo] Project 4: Tournament Results
====================================

# Project Overview

In this project, I was asked to develop a database scheme to store game matches
between players. Then, it uses code to query this data and determine the winners
of various games.

# Installation
* Run on local machine
   - Download the zipped folder
   - Extracts its contents to your computer
   - Install [Git](http://git-scm.com/downloads)
   - Install [Vagrant](http://vagrantup.com)
   - Install [VirtualBox](https://virtualbox.org)
   - Clone the [fsnd-project3 repository](https://github.com/jslewis90/fsnd-project3)
      * From the terminal, run `git clone PATH_TO_REPO destination_folder_name`
   - Launch the Vagrant VM
      * Open git
      * Navigate using the `cd` command to the destination folder.
      * Run `vagrant up` to start the VM. (It may take a while on the first run)
      * Run `vagrant ssh` to access the VM.
   - Run the code
      * Navigate using the `cd` command to the destination folder.
      * Run `psql` to access the database.
      * Run `\i tournament.sql` to set up the database.
      * Run `\q` to get back to the VM.
      * Run `python tournament_test.py` to run the Python code
      * When done, run `logout` to logout and `vagrant halt` to stop the VM.
