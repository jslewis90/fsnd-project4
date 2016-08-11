[logo]: https://udacity.com/favicon.ico "Udacity"
![Udacity][logo] Project 5: Item Catalog
====================================

# Project Overview

In this project, I was asked to develop an item catalog with CRUD functionality.
It was also required to add oauth to authenticate users, and give them appropriate
permissions to create, edit and delete items and categories in the database.

# Installation
* Run on local machine
   - Download the zipped folder
   - Extracts its contents to your computer
   - Install [Git](http://git-scm.com/downloads)
   - Install [Vagrant](http://vagrantup.com)
   - Install [VirtualBox](https://virtualbox.org)
   - Clone the [fsnd-project4 repository](https://github.com/jslewis90/fsnd-project4)
      * From the terminal, run `git clone PATH_TO_REPO destination_folder_name`
   - Launch the Vagrant VM
      * Open git
      * Navigate using the `cd` command to the destination folder.
      * Run `vagrant up` to start the VM. (It may take a while on the first run)
      * Run `vagrant ssh` to access the VM.
   - Run the code
      * Navigate to the catalog folder using the `cd /vagrant/catalog`.
      * Run `python lotsofitems.py` to get a fresh copy of the database.
      * Run `python catalogProject.py` to run the project.
      * You can then view the project in your web browser of choice at http://localhost:5000/
      * When done, run `logout` to logout and `vagrant halt` to stop the VM.
