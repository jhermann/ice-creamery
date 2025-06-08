"""
    MkDocs 'macros' plugin extensions.

     * https://mkdocs-macros-plugin.readthedocs.io/en/latest/macros/
     * https://tedboy.github.io/jinja2/templ14.html
"""

import pathlib

def define_env(env):
    """
        This is the hook for defining variables, macros and filters.

        - variables: the dictionary that contains the environment variables
        - macro: a decorator function, to declare a macro.
        - filter: a function with one of more arguments,
          used to perform a transformation.
    """
    # add to the dictionary of variables available to markdown pages
    #env.variables['baz'] = "John Doe"

    # NOTE: you may also treat env.variables as a namespace,
    #       with the dot notation
    #env.variables.baz = "John Doe"

    @env.macro
    def path(filename):
        return pathlib.Path(filename)

    @env.filter
    def rchop(text, length):
        return text[:-length]

    # If you wish, you can  declare a macro with a different name
    #def f(x):
    #    return x * x
    #env.macro(f, 'barbaz')

    # or to export some predefined function
    #env.macro(math.floor) # will be exported as 'floor'

    # create a jinja2 filter
    #@env.filter
    #def reverse(x):
    #    "Reverse a string (and uppercase)"
    #    return x.upper()[::-1]
