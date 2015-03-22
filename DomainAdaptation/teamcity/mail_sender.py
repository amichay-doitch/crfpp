#!/usr/bin/env python

import os
import subprocess
import smtplib
from smtplib import SMTPRecipientsRefused
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText   
import xml.etree.cElementTree as eTree
from utils import logger
import jinja2

_logger = logger.getLogger()
_logger.setLevel(logger.VERBOSE)


TITLES = {
            'nightly': 'Nightly - DFY', 
            'push' : 'Push Test - DFY'
            }


class HtmlMailSender(object):
    def __init__(self, root, test, since=24):
        """
        arguments:
        root - path DFY repository
        test - nightly or push
        since - how many hours of last git activity to get
        
        test=nightly:
            sends an email to the addresses in mail.xml under 'EmailAddress' --> 'nightly'
        test=push:
            sends an email only to the developer that pushed.
        
        the mail contains the tests statuses, their log files, and git history 'since' hours back.
        """
        
        self._since = None      # git info since when (in hours)
        self._get_since(since)
        
        self._root = root
        self._test = test
        self._title = TITLES[test]
        self._html = ""

        # TESTS - RESULTS:
        self._tests_summarize_list = []
        # GIT:      
        self._git_list = []

        self._create_body()
        self._create_jinja()
        self._send()        
                
    def _create_jinja(self):
        root_jinja = os.path.join(self._root, "regression", "teamcity", "email")
        templateLoader = jinja2.FileSystemLoader(searchpath=root_jinja)

        templateEnv = jinja2.Environment(loader=templateLoader)

        TEMPLATE_FILE = "email.html"

        template = templateEnv.get_template( TEMPLATE_FILE )

        templateVars = { "repo_location": self._root,
                         "summary": self._tests_summarize_list,
                         "hours": self._since,
                         "infos": self._git_list }

        self._html = template.render( templateVars )
        
    def _create_body(self):
        self._create_tests_summarize_list()
        self._create_git_info() 

    def _create_git_info(self):
        output = self._get_git_info()
        self._parse_git_info(output)
        
    def _get_git_info(self):
        cmd = ["git",
               "log",
               "--since={0} hours ago".format(self._since),
               "--pretty=format:commit::%h;;date::%cd;;owner::%an;;owner_mail::%ae;;subject::%s",
               "--name-only"]
        os.chdir(self._root)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output = p.communicate()[0]
        return output  
        
    def _parse_git_info(self, output):
        def parse_first_line(line):
            to_return = []
            d = {}
            for tup in line.split(";;"):
                tup = tup.split("::")
                d[tup[0]] = tup[1]
            d["owner"]  = '''<a href="mailto:{0}">{1}</a>'''.format(d["owner_mail"], d["owner"])
            for key in ["commit", "date", "owner", "subject"]:
                to_return.append(d[key])
            return to_return
            
        output = output.split("\n")
        commit = []
        files = []
        for line in output:
            if line:
                if line.startswith("commit"):
                    if commit:
                        commit.append("<br>".join(files))
                        self._git_list.append(commit)
                        commit = []
                        files = []
                    try:
                        commit = parse_first_line(line)
                    except:
                        commit = ["Error Retrieving info"]*4
                else:
                    files.append(line)
        commit.append("<br>".join(files))
        self._git_list.append(commit)
        return self._git_list

    def _create_tests_summarize_list(self):
        regression = os.path.join(self._root, 'regression')
        for root, dirs, files in os.walk(regression):
            for file in files:
                if file == "steps.status":
                    self._update_tests_summarize_list(os.path.join(root, file))

    def _update_tests_summarize_list(self, steps_status):
        d = dict()
        f = open(steps_status, 'r')
        for line in f.readlines():
            line = line.strip().split("%%")
            d[line[0]] = line[1]
        log_file = self._steps_file2log_path(steps_status)
        test_name = self._file_to_test_name(steps_status)
        status = d['fubstatus'] if 'fubstatus' in d else "No status found"
        data = [
                test_name, 
                status, 
                '''<a href="{0}">{1}</a>'''.format(self._path2isamba(log_file), "details")
                ]
        self._tests_summarize_list.append(data) 
   
    def _file_to_test_name(self, path):
        relative_to_root = path.replace(self._root, "")
        splited_path_relative_to_regression = [l for l in relative_to_root.split(os.sep) if l][1:]        
        i = splited_path_relative_to_regression.index('regression')
        return "/".join(splited_path_relative_to_regression[0:i])

    def _steps_file2log_path(self, path):
        steps = os.path.dirname(path)
        regression = os.path.dirname(steps)
        log = os.path.join(regression, 'regression.log')
        if not os.path.isfile(log):
            _logger.warn("Log file not found ")
            return ""
        else:
            return log

    def _path2isamba(self, path):
        if not path:
            return ""
        PREF = r"file://\\isamba.iil.intel.com"
        return "".join((PREF, path))  

    def _send(self):
        me = "dfy_gen@intel.com"
        msg = MIMEMultipart('html')
        msg['Subject'] = self._title
        msg['From'] = me
        send_me = MIMEText(self._html, 'html')
        msg.attach(send_me)
        smtp = smtplib.SMTP('localhost')
        address = self._get_address()
        for mail in address:
            try:
                smtp.sendmail(me, mail, msg.as_string())
            except SMTPRecipientsRefused as srr:
                _logger.exception("Recipient {0} didn't receive the message\nDetails: {1} ".format(mail, str(srr)))
            except Exception as e:
                _logger.exception("Exception occured\nRecipient {0} didn't receive the message\nDetails: {1} ".format(mail, str(e)))
        smtp.quit()
            
    def _get_address(self):
        if self._test == 'nightly':
            return self._get_address_for_nightly()

        elif self._test == 'push':
            cmd = ['git', 'log', '-1', '--pretty=format:%ae']
            os.chdir(self._root)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            addresses = [p.communicate()[0]]
            return addresses

    def _get_address_for_nightly(self):
        addresses = []
        xml_mail = os.path.join(self._root, 'regression', 'teamcity', 'email', 'mail.xml')
        doc = eTree.parse(xml_mail)
        for nightly_elem in doc.iter("nightly"):
            for elem in nightly_elem.iter("address"):
                addresses.append(elem.get("value"))
        return addresses
                
    def _get_since(self, since):
        if type(since) == int:
            self._since = since
            return
        else:
            try:
                self._since = int(since)
                return
            except:
                pass
        self._since = 24
    
  
if __name__ == "__main__":
    from optparse import OptionParser

    def get_options():
        parser = OptionParser(usage="%prog [options]")
        parser.add_option("-d", "--dfy", help="path to DFY")
        parser.add_option("-s", "--since", help="How many hours of last git activity to get", default=24)
        parser.add_option("-t", "--test", help="Which test, nightly or push", choices=TITLES.keys())
        

        (options, args) = parser.parse_args()

        if not hasattr(options, "dfy") or not options.dfy or not os.path.isdir(options.dfy):
            raise ValueError("--dfy was not defined or not exist")
        if not hasattr(options, "test") or not options.test or options.test not in TITLES:
            raise ValueError("--test was not given, or invalid")

        return options

    try:
        options = get_options()
        HtmlMailSender(options.dfy, options.test, options.since)
    except Exception as e:
        _logger.exception(e)
