import sublime 
import sublime_plugin
import subprocess
import json
import os
import re

class MountCommand(sublime_plugin.TextCommand):

    settings = ""

    mounted_project_list = []
    unmounted_project_list = []

    # Not real constants like other programming languages such as PHP 
    # but due to the version of python that is bundled with sublime 
    # text 2.  In any case we signal our intent to use them as constants.
    CONST_MOUNT = "mount"
    CONST_UNMOUNT = "unmount"
    
    def run(self, edit, action):
        if (sublime.platform() != "linux"):
            sublime.error_message("This plugin supports Linux only.")
            return False

        self.load_plugin_settings()
        self.show_project_input(action)

    def show_project_input(self, action):
        if (action == self.CONST_MOUNT):
            self.view.window().show_quick_panel(self.unmounted_project_list, self.mount)
        elif (action == self.CONST_UNMOUNT):
            self.view.window().show_quick_panel(self.mounted_project_list, self.unmount)
        else:
            return False

    def load_plugin_settings(self):
        self.settings = ProjectSettings()
        self.build_menu_lists()

    def reset_project_lists(self):
        self.mounted_project_list = []
        self.unmounted_project_list = []

    def build_menu_lists(self):
        mounted_project_count = 0
        unmounted_project_count = 0
        self.reset_project_lists()
        for project_name in self.settings.get_project_settings():
            if (self.is_project_mounted(project_name) == True):
                self.add_to_mounted_list(mounted_project_count, project_name)
                mounted_project_count = mounted_project_count + 1
            else:
                self.add_to_unmounted_list(unmounted_project_count, project_name)
                unmounted_project_count = unmounted_project_count + 1

    def add_to_mounted_list(self, index, project_name):
        self.mounted_project_list.append([])
        self.mounted_project_list[index].append(project_name)

    def add_to_unmounted_list(self, index, project_name):
        self.unmounted_project_list.append([])
        self.unmounted_project_list[index].append(project_name)

    def get_project(self, project_id, action):
        if (action == self.CONST_MOUNT):
            return self.unmounted_project_list[project_id][0]
        else:
            return self.mounted_project_list[project_id][0]

    def is_project_mounted(self, project):
        mount_point_path = self.settings.get_project_setting(project, "mount_point")
        if (os.path.ismount(mount_point_path)):
            return True
        else:
            return False

    def mount(self, project, action = "mount"):
        project_id = int(project)
        # -1 is returned if the user excapes the quick panel so just return
        if (project_id == -1):
            return

        project_selected = self.get_project(project_id, action)

        if (self.settings.check_project_exists(project_selected) == True):
            command = ""
            if (action != None and (action == self.CONST_MOUNT or action == self.CONST_UNMOUNT)):
                command = self.get_mount_command(project_selected, action)
            else:
                return

            result = self.run_command(command)
            self.show_result(result, action)
            return

        sublime.error_message("Please check that your settings for " + project_selected + " exist and are correct")
        return

    def is_ip_address(self, host):
        ip_pattern = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
        if (re.match(ip_pattern, host)):
            return True        
        else:
            return False

    def enclose_ip_address(self, ip):
        return "[%s]" % ip

    def unmount(self, project):
        self.mount(project, self.CONST_UNMOUNT)

    def get_mount_command(self, project, action):
        if (self.settings.verify_settings(project) == True):
            command = ""
            if (action == self.CONST_MOUNT):
                host = self.settings.get_project_setting(project, "host")
                if (self.is_ip_address(host)):
                    host = self.enclose_ip_address(host)

                command = "sshfs %s@%s:'%s' '%s'" % (self.settings.get_project_setting(project, "user"), 
                                                    host, 
                                                    self.settings.get_project_setting(project, "remote_dir"),
                                                    self.settings.get_project_setting(project, "mount_point"))
            elif (action == self.CONST_UNMOUNT):
                command = "fusermount -u '%s'" % self.settings.get_project_setting(project, "mount_point")
            else:
                return False

            return command
        else:
           sublime.error_message("Please check that your settings for " + project + " exist and are correct")
           return False

    def run_command(self, command):
        if (command != False):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            return iter(process.stdout.readline, b'')

    def show_result(self, result, action):
        output = ""
        for line in result:
            output = output + line

        if (output == None or output == ""):
            if (action == self.CONST_MOUNT):
                output_end = "mounted"
            else:
                output_end = "unmounted"

            output = "You have successfully " + output_end

        sublime.message_dialog(output)


class ProjectSettings():
   
    settings = ""

    CONST_PLUGIN_PATH = sublime.packages_path() + "/Project Mount/"
    CONST_SETTINGS_FILENAME = "ProjectMount.sublime-settings"

    def __init__(self):
        self.settings = json.loads(open(self.get_settings_file()).read())

    def get_settings_file(self):
        return self.CONST_PLUGIN_PATH + self.CONST_SETTINGS_FILENAME

    def get_project_setting(self, project, setting):
        return self.settings.get(project).get(setting)

    def get_project_settings(self):
        return self.settings

    def setting_is_none(self, settings):
        if (isinstance(settings, list)):
            for setting in settings:
                if (setting == None or setting == ""):
                    return True

        return False

    def check_project_exists(self, project):
        if (project in self.settings):
            return True
        
        return False

    def verify_settings(self, project):
        settings = [self.get_project_setting(project, "user"), 
                    self.get_project_setting(project, "host"),
                    self.get_project_setting(project, "remote_dir"), 
                    self.get_project_setting(project, "mount_point")]

        if (self.setting_is_none(settings)):
            return False

        return True

    # To-do: diplay log message to the console 
    def log_status(self, message):
        print message

class SettingsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        project_settings = ProjectSettings()
        self.view.window().open_file(project_settings.get_settings_file())