=======================
AARTFAAC Control System
=======================

.. image:: https://travis-ci.com/transientskp/aartfaac-control.svg?token=JM8FL3pgLyGt38ces8j4&branch=master
    :target: https://travis-ci.com/transientskp/aartfaac-control
.. image:: https://coveralls.io/repos/github/transientskp/aartfaac-control/badge.svg?branch=master 
    :target: https://coveralls.io/github/transientskp/aartfaac-control?branch=master

The control system is a daemon which runs on the LOFAR Main Control Unit
(MCU). It watches for new parsets which describe upcoming observations and
extracts relevant details. It maintains a queue of upcoming observations, and,
where appropriate, configures the RSP boards (on the station Local Control
Units) to select the appropriate data for AARTFAAC and starts the GPU
correlator and CPU imaging pipeline with appropriate configuration using
an AARTFAAC cfg file.

MCU System Setup
----------------

The MCU may be accessed through the LOFAR portal by ssh to ``mcu001``. All
AARTFAAC-related tools on the MCU are installed in ``/opt/aartfaac``. Note
that several tools on the MCU are old (Python 2.4, etc), but we are asked not
to install our own versions.

Parsets describing upcoming observations are written to disk in
``/opt/lofar/var/run``. The ID numbers in the filenames are not directly
useful, but the can be sorted by ctime.

LCU System Setup
----------------

The LCUs are accessed through the LOFAR portal by ssh to (eg) ``cs005c`` (for
CS005).

The RSPs are controlled using the command ``rspctl``. For example::

  $ rspctl --status
