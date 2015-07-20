# sqre-jirakit
JIRA manipulation tools using the python jira module

Installation instructions
=========================

Assuming you have a python environment and git installed:

    pip install git+https://github.com/lsst-sqre/sqre-jirakit.git

This code should work under both Python 2.7+ and Python 3.3+.

Scripts
=======

sq-ldm-240
----------

Generates an 'LDM-240' type table. Type -h for options.

To turn the output into a csv (eg. for excel import or Github view):

     sq-ldm-240 -k | cut -c2- | perl -ne 's/\|/,/g; print' > ldm-240.csv

dlp-graph
---------

Generate a [Graphviz](http://www.graphviz.org) `dot` format output describing
a graph of the DLP project. Type `-h` for options. For example:

     dlp-graph | dot -T svg > graph.svg

dlp-web
-------

Serve PDFs of the graphs generated by `dlp-graph`, above, on the web. No
options at present; simply run `dlp-web`. Point your browser at your IP
address on port 8080 and append `/wbs/` followed by the WBS you are interested
in to the URL. Note that `*` acts as a wildcard. For example, try:

- [http://127.0.0.1:8080/wbs/02C.04.04](http://127.0.0.1:8080/wbs/02C.04.04)
- [http://127.0.0.1:8080/wbs/02C.04.*](http://127.0.0.1:8080/wbs/02C.04.*)

Known Bugs etc
==============

Issues with jira python module
------------------------------

- https://github.com/pycontribs/jira/issues/66

Until this bug is fixed, this won't work on projects requiring authentication

- undeclared iPython dependency for jirashell
