#!/usr/bin/env python

import flask
import graphviz

import os
from contextlib import contextmanager
from io import BytesIO
from shutil import rmtree
from tempfile import mkdtemp
from urlparse import urljoin

from lsst.sqre.jira2dot import jira2dot, attr_func, rank_func
from lsst.sqre.jira2txt import jira2txt
from lsst.sqre.jirakit import build_query, cycles, get_issues, SERVER

app = flask.Flask(__name__)

DEFAULT_FMT="pdf"

# Supported formats. A request for anything else throws a 404.
FMTS = {"dot", "eps", "fig", "pdf", "svg", "png", "ps", "svg"}

@contextmanager
def tempdir():
    dirname = mkdtemp()
    try:
        yield dirname
    finally:
        rmtree(dirname, ignore_errors=True)

def build_server():
    @app.route('/wbs/<wbs>')
    def get_graph(wbs):
        return flask.redirect(flask.url_for("get_formatted_graph", wbs=wbs, fmt=DEFAULT_FMT))

    @app.route('/wbs/<fmt>/<wbs>')
    def get_formatted_graph(fmt, wbs):
        if fmt not in FMTS:
            flask.abort(404)
        dot = BytesIO()
        issues = get_issues(SERVER, build_query(("Milestone", "Meta-epic"), wbs))
        jira2dot(issues, file=dot, attr_func=attr_func, rank_func=rank_func, ranks=cycles())
        dot.seek(0)
        graph = graphviz.Source(dot.read(), format=fmt)
        with tempdir() as dirname:
            image = graph.render("graph", cleanup=True, directory=dirname)
            return flask.send_file(os.path.join(dirname, "graph%s%s" % (os.path.extsep, fmt)))

    @app.route('/wbs/csv/<wbs>')
    def get_csv(wbs):
        output = BytesIO()
        issues = get_issues(SERVER, build_query(("Milestone",), wbs))
        jira2txt(issues, output=output, csv=True, show_key=True, show_title=True,
                 url_base=urljoin(SERVER, "/browse/"))
        output.seek(0)
        return "<pre>%s</pre>" % output.read()

    @app.route('/wbs/tab/<wbs>')
    def get_tab(wbs):
        output = BytesIO()
        issues = get_issues(SERVER, build_query(("Milestone",), wbs))
        jira2txt(issues, output=output, csv=False)
        output.seek(0)
        return "<pre>%s</pre>" % output.read()

    return app
