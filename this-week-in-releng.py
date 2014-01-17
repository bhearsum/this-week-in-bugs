#!/usr/bin/env python

from __future__ import print_function

def make_report(bz, bzurl, args, ignore_summary_patterns=["problem tracking"], ignore_assignees=[]):
    product = "Release Engineering"

    components = []
    bugs = {}
    for component in bz.request("GET", "product/%s" % product)["products"][0]["components"]:
        components.append(component["name"])
        bugs[component["name"]] = {}

    for component in components:
        qs = "?product=%s&component=%s" % (product, component)
        for arg in args:
            qs += "&%s=%s" % (arg, args[arg])
        for bug in bz.request("GET", "bug" + qs)["bugs"]:
            for p in ignore_summary_patterns:
                if p in bug["summary"]:
                    break
            else:
                for ass in ignore_assignees:
                    if bug["assigned_to"] == ass:
                        break
                else:
                    bugs[component][bug["id"]] = bug["summary"]

    report = ["<ul>"]
    for component in sorted(bugs):
        comp_bugs = bugs[component]
        if not comp_bugs:
            continue
        report.append("<li>%s</li>" % component)
        report.append("<ul>")
        for bug, summary in comp_bugs.iteritems():
            report.append("<li><a href='%s/show_bug.cgi?id=%s'>%s</a></li>" % (bzurl, bug, summary))
        report.append("</ul>")
    report.append("</ul>")
    return "\n".join(report)

def fixed_report(bz, bzurl, since):
    args = {
        "resolution": "FIXED",
        "last_change_time": since
    }
    print("Completed work (resolution is 'FIXED'):")
    return make_report(bz, bzurl, args)

def inprogress_report(bz, bzurl, since):
    args = {
        "resolution": "---",
        "last_change_time": since,
    }
    print("In progress work (unresolved and not assigned to nobody):")
    return make_report(bz, bzurl, args, ignore_assignees=["nobody@mozilla.org"])

if __name__ == "__main__":
    import argparse
    from bzrest.client import BugzillaClient

    parser = argparse.ArgumentParser()
    parser.add_argument("--bugzilla-url", dest="bzurl", default="https://bugzilla.mozilla.org")
    parser.add_argument("--bugzilla-api-url", dest="bzapi", default="http://bugzilla.mozilla.org/rest")
    parser.add_argument("--since", dest="since")
    parser.add_argument("reports", nargs="+")

    args = parser.parse_args()

    bz = BugzillaClient()
    bz.configure(args.bzapi, None, None)

    for report in args.reports:
        if report not in ("fixed", "inprogress"):
            raise Exception("Invalid report type: '%s'" % report)
    for report in args.reports:
        if report == "fixed":
            print(fixed_report(bz, args.bzurl, args.since))
        elif report == "inprogress":
            print(inprogress_report(bz, args.bzurl, args.since))
