"""
    MkDocs 'macros' plugin extensions.

     * https://mkdocs-macros-plugin.readthedocs.io/en/latest/macros/
     * https://tedboy.github.io/jinja2/templ14.html
"""
import sys
import pathlib
import importlib.util as imp_util

def load_module(file_name, module_name=''):
    """Load a script fiel as a module."""
    module_name = module_name or pathlib.Path(file_name).stem.replace('-', '_')
    spec = imp_util.spec_from_file_location(module_name, file_name)
    module = imp_util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

recipe_lib = load_module(pathlib.Path(__file__).parent / 'scripts' / 'ice-cream-recipe.py')
recipe_lib.parse_info_docs('ingredients', '### ')

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

    @env.filter
    def ingredient(text):
        #return f'[{ text.replace("]", "\\]") }](/ice-creamery/info/ingredients/#{anchor})' + '' + \
        return recipe_lib.ingredient_link(text)

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
