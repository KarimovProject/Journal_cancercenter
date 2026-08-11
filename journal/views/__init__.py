"""
journal/views/__init__.py

Barcha viewlarni bu yerdan import qiling.
urls.py da `from . import views` ishlashi uchun hamma
narsani shu yerdan re-export qilamiz.
"""

# Public sahifalar
from .public import (  # noqa: F401
    home,
    article_list,
    article_detail,
    download_citation,
    author_detail,
    issue_list,
    issue_detail,
    editorial_board,
    department_list,
    conference_list,
    conference_detail,
    postgraduate,
    grant_list,
    static_page,
    for_authors,
    update_list,
    update_detail,
    collection_list,
    collection_detail,
    custom_404,
    custom_500,
)

# Autentifikatsiya va newsletter
from .auth_views import (  # noqa: F401
    register_view,
    login_view,
    logout_view,
    newsletter_subscribe,
    newsletter_confirm,
)

# Maqola yuborish va profil
from .submission import (  # noqa: F401
    submit_article,
    edit_article,
    my_articles,
    edit_profile,
)

# Taqriz va muharrir paneli
from .review import (  # noqa: F401
    read_notification,
    reviewer_dashboard,
    review_article,
    admin_stats_api,
    editor_dashboard,
    editor_article_detail,
    editor_assign_reviewer,
    editor_make_decision,
)
