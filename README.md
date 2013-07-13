Project Mount
=============

A plugin for Sublime Text 2 which will allow you to connect remotely to servers via sshfs.

This plugin will only work on a Linux Operating System. 

Installation
============

Download and uncompress into your Sublime Text 2 packages directory.

Example path to your packages: ~/.config/sublime-text-2/Packages/

Instructions
============

Project Mount menu options can be found under the Project menu in Sublime Text 2.  The options are:

- Mount a project... - this will give you a list of all projects that are not mounted
- Umount a project... - this will give a list of the current project that are mounted
- Edit mount settings... - JSON settings file where you enter your project settings

When editing your mount settings you need to ensure that you have the following structure for each project:

{
	"Example Project 1":
	{
		"user": "your_username",
		"host": "www.your_website.com",
		"remote_dir": "/home/your_remote_dir/",
		"mount_point": "/home/your_username/Remote Projects/Your Remote Project Folder"
	}
}

The example above shows the JSON object of a project.  Within this project object we have a number of settings:

- user - this is your ssh username that is used to connect to the server
- host - the server you wish to remotely connect to (can be either an IP or DNS name)
- remote_dir - the directory on the remote server 
- mount_point - the directory on your local machine which will be your mount point

To add more projects simply copy an existing JSON project object and seperate with a comma (,).  Example:

{
	"Example Project 1":
	{
		"user": "your_username",
		"host": "www.your_website.com",
		"remote_dir": "/home/your_remote_dir/",
		"mount_point": "/home/your_username/Remote Projects/Your Remote Project Folder"
	},
	"Example Project 2":
	{
		"user": "your_username",
		"host": "192.168.1.1",
		"remote_dir": "/home/your_remote_dir/",
		"mount_point": "/home/your_username/Remote Projects/Your Remote Project Folder"
	}
}


