from __future__ import print_function

import sys
import logging
import textwrap

from jira import JIRA

def jira2dot(server, query, file=sys.stdout, link_types=("Blocks",), attr_func=None, rank_func=None,
             ranks=None, diag_name="Diagram"):
    """Generate a GraphViz dot file displaying the relationships between JIRA issues.

    Arguments:
      server ---------------- URL for the JIRA server
      query ----------------- SQL query to pass to JIRA to limit issues
      file ------------------ Python file-like object to write output to
      link_types ------------ Sequence of link types to include in the graph
      attr_func ------------- Callback function that takes a jira.Issue object and returns a sequence
                              of GraphViz attribute key/value pairs (e.g. "shape=box")
      rank_func ------------- Callback function that takes a jira.Issue object and returns a string
                              that the issue should be sorted by - typically a release version or cycle.
      rank ------------------ An ordered sequence of rank strings to sort issues by (only affects issues
                              for which rank_func returns a result other than None)
      diag_name ------------- Name for the top-level graph node.
    """
    file.write('digraph "{0}" {{\n'.format(diag_name))
    file.write('  node [fontname="monospace", shape="box"]')
    jira = JIRA(dict(server=server))
    by_key = {}
    by_rank = {}

    for item in jira.search_issues(query, maxResults=1000):
        issue = jira.issue(item)
        by_key[issue.key] = issue

        # Populate a dict indexed by caller-defined rank.
        if rank_func is not None:
            rank = rank_func(issue)
            if rank:
                by_rank.setdefault(str(rank), []).append(issue)
                logging.debug("Set rank {0} for issue {1}".format(rank, issue.key))

        # Get any custom attributes from the caller.
        if attr_func is None:
            attr = ["shape=box"]
        else:
            attr = list(attr_func(issue))

        # Get the owner (WBS or Team) for the issue
        issuetype = issue.fields.issuetype.name
        if issuetype == "Milestone" or issuetype == "Meta-epic" or issuetype == "Epic":
            owner = issue.fields.customfield_10500  # WBS
        else:
            owner = issue.fields.customfield_10502.value  # Team

        # Generate a fancy label containing the issue key, the owner (WBS or Team), and summary.
        summary = issue.fields.summary.replace("&", "&amp;")
        label = """
        label=
            <<table border="0">
                <tr><td><b>{0}</b></td><td><b>{1}</b></td></tr>
                <tr><td colspan="2">{2}</td></tr>
            </table>>
        """.format(issue.key, owner, "<br/>".join(textwrap.wrap(summary, width=25)))
        attr.append(label)

        # Use the issue description as the tooltip (mouseover text)
        if issue.fields.description:
            tooltip = 'tooltip="{0}"'.format(issue.fields.description.replace('"', "'"))
        else:
            tooltip = 'tooltip="{0}"'.format(summary)
        attr.append(tooltip)

        # Write the node's attributes.
        attr.append('URL="{0}"'.format(issue.permalink()))
        file.write('  "{0}" [{1}]\n'.format(issue.key, ", ".join(attr)))

    # Setup ranks (caller-defined, but probably indicate a release or cycle)
    if ranks:
        file.write('  node [fontname="monospace", shape=none]\n')
        file.write('  {0}\n'.format(" -> ".join('"{0}"'.format(r) for r in ranks)))
        for rank in ranks:
            items = [rank] + [i.key for i in by_rank.get(str(rank), [])]
            file.write('  {{ rank=same; {0} }}\n'.format("; ".join('"{0}"'.format(item) for item in items)))

    # Declare issue links
    for issue in by_key.values():
        for link in issue.fields.issuelinks:
            if link.type.name in link_types:
                if hasattr(link, "outwardIssue"):
                    if link.outwardIssue.key in by_key:
                        file.write('  "{0.key}" -> "{1.key}"\n'.format(issue, link.outwardIssue))
                    else:
                        logging.debug(
                            "Skipping external link {0.key} -> {1.key}".format(issue, link.outwardIssue)
                        )
                else:
                    logging.debug("Skipping inward link {0.key} -> {1.key}".format(link.inwardIssue, issue))

    file.write("}\n")
