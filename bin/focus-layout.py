#!/usr/bin/env python3
"""Explicitly arrange 2-3 named panes in one row; ID changes are read back after moves."""
import argparse
from common import unique,run
p=argparse.ArgumentParser();p.add_argument('labels',nargs='+');a=p.parse_args()
if not 2<=len(a.labels)<=3:raise SystemExit('Provide two or three exact, unique pane labels')
if len(set(a.labels))!=len(a.labels):raise SystemExit('Labels must differ')
selected=[unique(label) for label in a.labels];anchor=selected[0];tab=anchor['tab_id']
for i,label in enumerate(a.labels[1:],start=1):
    pane=unique(label)
    # Herdr ignores moves within one tab: lift to a temporary tab first.
    if pane['tab_id']==tab:
        run('pane','move',pane['pane_id'],'--new-tab','--workspace',anchor['workspace_id'],'--label','kit-layout','--no-focus')
        pane=unique(label)
    run('pane','move',pane['pane_id'],'--tab',tab,'--target-pane',anchor['pane_id'],'--split','right',
        '--ratio',str(1/(len(a.labels)-i+1)),'--no-focus')
    anchor=unique(label)
print('Requested pane row arranged. Herdr preserves its layout; register agent sessions separately.')
