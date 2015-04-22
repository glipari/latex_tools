Track changes in LaTeX
======================

This is LaTeX file for 3 simple macros that allow to implement track
changes feature.

See example.tex for an example of usage and some additional
documentation.

*TODO*: Add support for the changes.sty package in accept_revisions.py

## Accepting revision ##

Once the revisions start to become a lot, it is better to clean up the
file *accepting* or *rejecting* the revisions. To do this step by
step, run the script accept_revision.py.

It takes as argument the tex file to transform.  As first thing, it
makes a copy into `backup_<filename>_i`, where i is a progressie
number. Therefore, if you run this script often on the same file, you
get a lot of backups, that you can clean simply with

	rm backup_*

(unless you have a file that starts with `backup_`, in which case, you
may want to modify the script accordingly).

The script is interactive: it stops at every use of a change macro,
prints two lines before and two lines after the change, and the change
is highlighted in blue. It then asks you if you want to (A)ccept,
(R)eject or (S)kip the change. In any cases, it prints the results
(with the change in bold), before continuing with the following change. 

It also takes three possible options:

- `-h, --help` print the help
- `-a, --accept` accept all changes (non-interactive)
- `-r, --reject` reject all changes (non-interactive)

The changes are written on a `/tmp/accept-temp` file and recopied on
the original file before the script ends. If you press `Ctrl-C` before
the script ends, the original file is not overwritten and the partial
changes remain in `/tmp/accept-temp`. 
