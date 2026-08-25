"""
journal/utils/citations.py

Maqolalar uchun iqtibos (citation) generatorlari.
Ilgari bu mantiq Article modelida edi. Endi toza va xavfsiz Arxitektura (Separation of Concerns) uchun bu yerga olindi.
"""

def generate_citation_apa(article):
    """Simple APA-style citation string."""
    names = [a.full_name for a in article.authors.all()]
    if len(names) > 1:
        author_str = ', '.join(names[:-1]) + ' & ' + names[-1]
    else:
        author_str = names[0] if names else ''
    year = article.year or ''
    parts = [p for p in [f'{author_str} ({year}).' if author_str else '', f'{article.title}.'] if p]
    cite = ' '.join(parts)
    if getattr(article, 'issue', None):
        cite += f' Vol. {article.issue.volume}({article.issue.number}).'
    if article.doi:
        cite += f' https://doi.org/{article.doi}'
    return cite.strip()


def generate_citation_mla(article):
    """Simple MLA-style citation string."""
    names = [a.full_name for a in article.authors.all()]
    if len(names) > 2:
        author_str = f"{names[0]}, et al."
    elif len(names) == 2:
        author_str = f"{names[0]}, and {names[1]}."
    elif names:
        author_str = f"{names[0]}."
    else:
        author_str = ""
    cite = f'{author_str} "{article.title}." Central Asian Cancer Sciences'
    if getattr(article, 'issue', None):
        cite += f', vol. {article.issue.volume}, no. {article.issue.number}'
    if article.year:
        cite += f', {article.year}'
    if getattr(article, 'pages', None):
        cite += f', pp. {article.pages}'
    cite += '.'
    if article.doi:
        cite += f' https://doi.org/{article.doi}'
    return cite.strip()


def generate_citation_harvard(article):
    """Simple Harvard-style citation string."""
    names = [a.full_name for a in article.authors.all()]
    author_str = ' and '.join(names) if names else ''
    year = article.year or ''
    cite = f"{author_str} ({year}) '{article.title}', Central Asian Cancer Sciences"
    if getattr(article, 'issue', None):
        cite += f', {article.issue.volume}({article.issue.number})'
    if getattr(article, 'pages', None):
        cite += f', pp. {article.pages}.'
    else:
        cite += '.'
    if article.doi:
        cite += f' Available at: https://doi.org/{article.doi}.'
    return cite.strip()


def generate_citation_vancouver(article):
    """Simple Vancouver-style citation string."""
    names = [a.full_name for a in article.authors.all()]
    author_str = ', '.join(names) if names else ''
    cite = f"{author_str}. {article.title}. Central Asian Cancer Sciences."
    if article.year:
        cite += f" {article.year};"
    if getattr(article, 'issue', None):
        cite += f"{article.issue.volume}({article.issue.number})"
    if getattr(article, 'pages', None):
        cite += f":{article.pages}."
    else:
        cite += "."
    return cite.strip()


def generate_citation_ris(article):
    """Generates RIS format citation."""
    lines = [
        "TY  - JOUR",
        f"T1  - {article.title}",
        "JO  - Central Asian Cancer Sciences"
    ]
    for a in article.authors.all():
        lines.append(f"AU  - {a.full_name}")
    if article.year:
        lines.append(f"PY  - {article.year}")
    if getattr(article, 'issue', None):
        lines.append(f"VL  - {article.issue.volume}")
        lines.append(f"IS  - {article.issue.number}")
    if getattr(article, 'pages', None):
        sp, _, ep = str(article.pages).partition('-')
        if sp: lines.append(f"SP  - {sp.strip()}")
        if ep: lines.append(f"EP  - {ep.strip()}")
    if getattr(article, 'abstract', None):
        lines.append(f"AB  - {article.abstract}")
    if article.doi:
        lines.append(f"DO  - {article.doi}")
        lines.append(f"UR  - https://doi.org/{article.doi}")
    lines.append("ER  - ")
    return "\n".join(lines)
