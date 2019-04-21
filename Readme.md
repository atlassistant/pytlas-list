list skill for pytlas [![Build Status](https://travis-ci.org/atlassistant/pytlas-list.svg?branch=master)](https://travis-ci.org/atlassistant/pytlas-list) ![License]( https://img.shields.io/badge/License-GPL%20v3-blue.svg)
===============================

A skill to manage your memory aids.

A skill powered by the open, non intrusive and super easy  pytlas assistant framework 

see for details: https://github.com/atlassistant/pytlas

Supported languages
-------------------
- English

Typical sentences
-----------------
- create a new list named shopping list
- add eggs in my shopping list
- remove eggs from my shopping list
- delete the list shopping list
- show me the shopping list
- send to to.someone@mail.com the shopping list
- send to me the shopping list
- how does the list skill work

Configuration:
---------------
- path = (folder where list are stored as simple json file)  
- from email = (email from used when sending a list)
- smtp address = (smtp server used to send email)
- smtp login = (smtp login if credential are required)
- smtp password = (associated smtp password )

Launching tests
---------------
In order to launch tests, you will need to install required dependencies and then launch the test suite with:

```bash
$ pip install -r requirements_tests.txt
$ python -m nose --with-coverage --cover-package=list
```