from flask import Blueprint
import ckan.plugins as p
import ckantoolkit as tk

_ = tk._

group = Blueprint("pages_group", __name__)


def _group_list_pages(id, group_dict=None):
    tk.c.pages_dict = tk.get_action("ckanext_pages_list")(
        data_dict={"org_id": tk.c.group_dict["id"]}
    )
    return tk.render(
        "ckanext_pages/group_page_list.html",
        extra_vars={"group_type": "group", "group_dict": group_dict},
    )


def _template_setup_group(id):
    if not id:
        return
    # we need the org for the rest of the page
    context = {"for_view": True}
    try:
        tk.c.group_dict = tk.get_action("group_show")(context, {"id": id})
    except tk.ObjectNotFound:
        tk.abort(404, _("Group not found"))
    except tk.NotAuthorized:
        tk.abort(401, _("Unauthorized to read group %s") % id)


@group.route("/group/pages_delete/<id>/", methods=["POST", "GET"])
@group.route("/group/pages_delete/<id>/<path:page>", methods=["POST", "GET"])
def delete(id, page=''):
    _template_setup_group(id)
    page = page[1:]
    if "cancel" in tk.request.params:
        return tk.redirect_to(
            "pages_group.edit", id=tk.c.group_dict["name"], page="/" + page
        )
    try:
        if tk.request.method == "POST":
            action = tk.get_action("ckanext_group_pages_delete")
            action({}, {"org_id": tk.c.group_dict["id"], "page": page})
            return tk.redirect_to("pages_group.show", id=id)
        else:
            tk.abort(404, _("Page Not Found"))
    except tk.NotAuthorized:
        tk.abort(401, _("Unauthorized to delete page"))
    except tk.ObjectNotFound:
        tk.abort(404, _("Group not found"))

    context = {"for_view": True}
    group_dict = tk.get_action("group_show")(context, {"id": id})

    return tk.render(
        "ckanext_pages/confirm_delete.html",
        {"page": page, "group_type": "group", "group_dict": group_dict},
    )


@group.route("/group/pages_edit/<id>/", methods=["POST", "GET"])
@group.route("/group/pages_edit/<id>/<path:page>", methods=["POST", "GET"])
def edit(id, page=None, data=None, errors=None, error_summary=None):
    _template_setup_group(id)
    if page:
        page = page[1:]
    _page = tk.get_action("ckanext_pages_show")(
        data_dict={"org_id": tk.c.group_dict["id"], "page": page}
    )
    if _page is None:
        _page = {}

    if tk.request.method == "POST" and not data:
        data = tk.request.form
        items = ["title", "name", "content", "private"]
        # update config from form
        for item in items:
            if item in data:
                _page[item] = data[item]
        _page["org_id"] = tk.c.group_dict["id"]
        _page["page"] = page
        try:
            junk = tk.get_action("ckanext_group_pages_update")(data_dict=_page)
        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return edit(id, "/" + page, data, errors, error_summary)
        return tk.redirect_to(
            "pages_group.show", id=id, page="/" + _page["name"]
        )

    if not data:
        data = _page

    errors = errors or {}
    error_summary = error_summary or {}

    context = {"for_view": True}
    group_dict = tk.get_action("group_show")(context, {"id": id})

    vars = {
        "data": data,
        "errors": errors,
        "error_summary": error_summary,
        "page": page,
        "group_type": "group",
        "group_dict": group_dict,
    }

    return tk.render("ckanext_pages/group_page_edit.html", extra_vars=vars)


@group.route("/group/pages/<id>/")
@group.route("/group/pages/<id>/<path:page>")
def show(id, page=None):
    if page:
        page = page[1:]
    _template_setup_group(id)

    context = {"for_view": True}
    group_dict = tk.get_action("group_show")(context, {"id": id})
    if not page:
        return _group_list_pages(id, group_dict)
    _page = tk.get_action("ckanext_pages_show")(
        data_dict={"org_id": tk.c.group_dict["id"], "page": page}
    )
    if _page is None:
        return _group_list_pages(id, group_dict)
    tk.c.page = _page
    return tk.render(
        "ckanext_pages/group_page.html",
        {"group_type": "group", "group_dict": group_dict},
    )
