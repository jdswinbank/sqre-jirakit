#!/usr/bin/env python

from __future__ import print_function

from jira import JIRA
import jirakit
import os
import argparse
import tabulate

debug = os.getenv("DM_SQUARE_DEBUG")
trace = False

# argument parsing and default options

parser = argparse.ArgumentParser(
    description='Generate LDM-240 style tables from the LSST DLP JIRA project',
    epilog='Part of jirakit: https://github.com/lsst-sqre/sqre-jirakit'
)

parser.add_argument('-s', '--server',
                    default='https://jira.lsstcorp.org/',
                    help='JIRA server URL')

parser.add_argument('-k', '--key',
                    action='store_true',
                    default=True,
                    help='Show the JIRA issue key in the table cell (default behaviour)')

parser.add_argument('-t', '--title',
                    action='store_true',
                    default=False,
                    help='Show the JIRA issue title in the table cell')

parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.5')

opt = parser.parse_args()

#

# WBS = 'customfield_10500'

jira_opts = {
    'server': opt.server
}

jira = JIRA(jira_opts)

project = jira.project('DLP')

cycles = jirakit.cycles()
if debug: print(cycles)

milestones = jira.search_issues('project = DLP and issuetype = Milestone order by WBS ASC')

cycles.insert(0, 'WBS')

table = [cycles]

for milestone in milestones:
    issue = jira.issue(milestone)
    #    if debug: print(milestone)

    # Get the release associated with this milestone
    if issue.fields.fixVersions:
        release = issue.fields.fixVersions[0]
        cyc = release.name
        milestonestr = milestone.key
        if issue.fields.customfield_10500:
            WBS = issue.fields.customfield_10500
        else:
            WBS = 'None'

        row = [WBS]

        for k in cycles:
            if k == cyc:

                if opt.key:
                    cell = milestonestr
                elif opt.title:
                    cell = milestone.fields.summary
                else:
                    print('This should not happen')
                
                # row.append(milestonestr)
                row.append(cell)
            else:
                row.append("-")
                table.append(row)
    else:
        print('No release assigned to', issue.key)


print(tabulate.tabulate(table))
