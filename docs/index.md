# About
A collection of my Ninja Creami recipes; the goal is to have only tested / approved ones,
but on the way there [draft](https://jhermann.github.io/ice-creamery/tags/#tag:draft) recipes
are tagged as such.
Most recipes are formulated so that they also work in a classic churning machine.

It currently has `{{ path(config.docs_dir).glob('?/*.md') | list | length }}` recipes.

> <img width=720 alt="Gelato Cart" src="https://raw.githubusercontent.com/jhermann/ice-creamery/refs/heads/main/assets/gelato-cart.webp" />

🗓️ Last changed *{{ git.date_ISO | rchop(14) }}* by *{{ git.author }}*

> [{{ git.short_commit }}](https://github.com/jhermann/ice-creamery/commit/{{ git.short_commit }}){target="_blank"} `{{ git.message | truncate(50) }}`

## How to Use This Site?
Use the top bar to navigate using [Tags](tags/) or the first letter of a recipe name.

> 💡 You can load the <a href="/ice-creamery/print_page/" target="_blank">All You Can Read<sup>↗</sup></a>
> version to save the site as a stand-alone HTML or PDF document, to read off-line.

Check out the [Info](info/) section to get background information on the 'philosophy'
behind the specific formulation of these recipes, the ingredients used, and some tips & tricks
to successfully reproduce them in your kitchen.

That section also contains a FAQ page and a glossary, in case some abbreviations used are unknown to you.

> <span id="audio">🗣️</span> Another way to explore background topics is to listen to this ~18min long interview-style summary of the site.
> 
> <audio controls><source src="https://github.com/jhermann/ice-creamery/raw/refs/heads/main/assets/audio/interview-style-tour-of-the-site-96k.mp3" type="audio/mpeg" /></audio>
> 
> If your browser does not support the audio element, try to [download](https://github.com/jhermann/ice-creamery/raw/refs/heads/main/assets/audio/interview-style-tour-of-the-site-96k.mp3) the MP3 file.

## How It's Made?
This website is based on a collection of calculated recipes stored in a
[GitHub repository](https://github.com/jhermann/ice-creamery#readme).

```embed
url: https://github.com/jhermann/ice-creamery#readme
```

The recipes are written as [LibreOffice](https://www.libreoffice.org/download/download-libreoffice/)
spreadsheets, which allows to directly use formulas for the calculation of
important ice cream metrics and nutritional information.

```embed
url: https://www.libreoffice.org/
image: https://raw.githubusercontent.com/jhermann/ice-creamery/refs/heads/main/assets/libre-office-logo.png
favicon: https://raw.githubusercontent.com/jhermann/ice-creamery/refs/heads/main/assets/libre-office-favicon.ico
```

A Python script then converts CSV exports of the spreadsheets to markdown files, which are in turn used to render this HTML web site using
[MkDocs](https://github.com/mkdocs/mkdocs#readme).

```embed
url: https://www.mkdocs.org/
```

<!--
{ macros_info() }}
{ context(git) | pretty }}
-->
