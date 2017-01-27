____________________________________________
Pytroll coding guidelines and best practices
____________________________________________



    “It is not the strongest of the species that survives, 
  
    nor the most intelligent that survives. 
  
    It is the one that is most adaptable to change.”
  
    -- Charles Darwin



    “It seems that perfection is attained, 
  
    not when there is nothing more to add, 
  
    but when there is nothing more to take away.” 
  
    -- Antoine de Saint Exupéry




Coding Style
------------

Language is US English.


We generally follow the pep-8 and pep-257


Indentation is 4 spaces (no tabs!)


Max line length is set to 80 chars, but up to 120 is tolerated.


Every unit of code must be properly tested and documented.


Global constants are written in capital letters, eg. PLANK_CONSTANT if they are not modified in the module and should be placed at the top of the module.


About docstrings, we follow the google style: https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments


Prepare to be Python3 compatible.


When in doubt, read pep 20, the Zen of Python (see appendix A)


Maintainability Guidelines
--------------------------

- Functions/methods should not contain more than 15 lines of code (including blank lines and comments).
- There should be a maximum of 3 branches in each function/method.
- Functions/methods should not have more than 5 parameters. Think of bundling arguments in helper classes for example.


Style Checking
--------------

In your IDE/editor, it is highly recommended to activate/install a plugin for/script a save hook for doing automatic style checks and/or corrections, eg autopep8, pylint, pyflakes


Working with Github
-------------------

Before submitting your changes, make sure your code follow the coding style above, and that your changes are properly covered by tests and documented. Make sure you run a style checker (eg pylint) on your code.


If you want to help develop a Pytroll package, the preferred way to contribute is to fork the original repository and submit a pull request with your proposed changes. 

The workflow in a nutshell is to:
 * Fork the repository in github
 * Implement the fix (with a test), it can be multiple commits
 * Submit a pull request (PR) to the project owner making sure changes will be merged to the ‘develop’ or ‘pre-master’ branch.
 * If you need to make further changes after the PR is issued, just push your commits to your fork: they will automatically be appended to the PR.


Pull requests should avoid committing or adding unused files (ex. .pyc files). Even if they are deleted in future commits they should be purged from the commit history. See https://help.github.com/articles/removing-sensitive-data-from-a-repository/ for instructions.


- https://help.github.com/articles/creating-a-pull-request/
- https://help.github.com/articles/fork-a-repo/




Alternatively, patches formatted with the git format-patch command can be sent to the bdfl of the package.


The submitted work will be reviewed by the main contributors of the package, possibly engaging in a discussion on the patch, and maybe requesting changes. Be prepared to follow up on your work.


Commit messages:
 * Separate subject from body with a blank line
 * Limit the subject line to 50 characters
 * Capitalize the subject line
 * Do not end the subject line with a period
 * Use the imperative mood in the subject line
 * Wrap the body at 72 characters
 * Use the body to explain what and why (not how)




- http://chris.beams.io/posts/git-commit/
- http://who-t.blogspot.de/2009/12/on-commit-messages.html


Making releases
---------------

“Release early, release often”
Versioning: http://semver.org/


The procedure for releasing is provided here https://github.com/pytroll/pytroll/wiki/Making-a-release




Appendix A
----------

PEP 20: The Zen of Python
~~~~~~~~~~~~~~~~~~~~~~~~~

 * Beautiful is better than ugly.
 * Explicit is better than implicit.
 * Simple is better than complex.
 * Complex is better than complicated.
 * Flat is better than nested.
 * Sparse is better than dense.
 * Readability counts.
 * Special cases aren't special enough to break the rules.
 * Although practicality beats purity.
 * Errors should never pass silently.
 * Unless explicitly silenced.
 * In the face of ambiguity, refuse the temptation to guess.
 * There should be one-- and preferably only one --obvious way to do it.
 * Although that way may not be obvious at first unless you're Dutch.
 * Now is better than never.
 * Although never is often better than *right* now.
 * If the implementation is hard to explain, it's a bad idea.
 * If the implementation is easy to explain, it may be a good idea.
 * Namespaces are one honking great idea -- let's do more of those!
