Eve
===


Installation
------------

Eve should work with both python 2 and 3[¹](#caldav-python3), but python2 isn't
recommanded if you plan to use non-ascii strings.

Requirements:

- caldav[¹](#caldav-python3) >= 0.4.0
- irc >= 12.1.2


Notes
-----

<a name="caldav-python3">¹</a>  Be carefull with caldav and python3: there is a
dependance in vobject, which doesn't have a proper python3 port. You'll need to
find a good python3 fork. The 2015-04-29, I used
[tBaxter's fork](https://github.com/tBaxter/vobject).
