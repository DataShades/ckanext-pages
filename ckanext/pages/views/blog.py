from flask import Blueprint
from ckanext.pages.views.pages import _pages_list_pages, show as pshow, edit as pedit, delete as pdelete


blog = Blueprint("blog", __name__)


@blog.route("/blog/")
@blog.route("/blog/<path:page>")
def show(page=None):
    if page:
        return pshow(page, page_type="blog")
    return _pages_list_pages("blog")


@blog.route("/blog_delete/", methods=["POST", "GET"])
@blog.route("/blog_delete/<path:page>", methods=["POST", "GET"])
def delete(page=None):
    return pdelete(page, page_type="blog")


@blog.route("/blog_edit/", methods=["POST", "GET"])
@blog.route("/blog_edit/<path:page>", methods=["POST", "GET"])
def edit(page=None, data=None, errors=None, error_summary=None):
    return pedit(
        page=page,
        data=data,
        errors=errors,
        error_summary=error_summary,
        page_type="blog",
    )
