from flask import Blueprint
import ckan.plugins as p
import ckantoolkit as tk

_ = tk._


organization = Blueprint("pages_organization", __name__)


def _org_list_pages(id, org_dict=None):
    tk.c.pages_dict = tk.get_action("ckanext_pages_list")(
        data_dict={"org_id": tk.c.group_dict["id"]}
    )
    return tk.render(
        "ckanext_pages/organization_page_list.html",
        {"group_type": "organization", "group_dict": org_dict},
    )


def _template_setup_org(id):
    if not id:
        return
    # we need the org for the rest of the page
    context = {"for_view": True}
    try:
        tk.c.group_dict = tk.get_action("organization_show")(
            context, {"id": id}
        )
    except tk.ObjectNotFound:
        tk.abort(404, _("Organization not found"))
    except tk.NotAuthorized:
        tk.abort(401, _("Unauthorized to read organization %s") % id)


@organization.route("/organization/pages_delete/<id>/", methods=["POST", "GET"])
@organization.route(
    "/organization/pages_delete/<id>/<path:page>", methods=["POST", "GET"]
)
def delete(id, page=''):
    _template_setup_org(id)
    page = page.lstrip('/')
    if "cancel" in tk.request.params:
        return tk.redirect_to(
            "pages_organization.edit",
            id=tk.c.group_dict["name"],
            page="/" + page,
        )
    try:
        if tk.request.method == "POST":
            action = tk.get_action("ckanext_org_pages_delete")
            action({}, {"org_id": tk.c.group_dict["id"], "page": page})
            return tk.redirect_to("pages_organization.show", id=id)
        else:
            tk.abort(404, _("Page Not Found"))
    except tk.NotAuthorized:
        tk.abort(401, _("Unauthorized to delete page"))
    except tk.ObjectNotFound:
        tk.abort(404, _("Organization not found"))
    context = {"for_view": True}
    org_dict = tk.get_action("organization_show")(context, {"id": id})

    return tk.render(
        "ckanext_pages/confirm_delete.html",
        {"page": page, "group_type": "organization", "group_dict": org_dict},
    )


@organization.route("/organization/pages_edit/<id>/", methods=["POST", "GET"])
@organization.route(
    "/organization/pages_edit/<id>/<path:page>", methods=["POST", "GET"]
)
def edit(id, page=None, data=None, errors=None, error_summary=None):
    _template_setup_org(id)
    if page:
        page = page.lstrip('/')
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
            junk = tk.get_action("ckanext_org_pages_update")(data_dict=_page)
        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return edit(id, "/" + page, data, errors, error_summary)
        return tk.redirect_to(
            "pages_organization.show", id=id, page="/" + _page["name"]
        )

    if not data:
        data = _page

    errors = errors or {}
    error_summary = error_summary or {}

    context = {"for_view": True}
    org_dict = tk.get_action("organization_show")(context, {"id": id})

    vars = {
        "data": data,
        "errors": errors,
        "error_summary": error_summary,
        "page": page,
        "group_type": "organization",
        "group_dict": org_dict,
    }

    return tk.render(
        "ckanext_pages/organization_page_edit.html", extra_vars=vars
    )


@organization.route("/organization/pages/<id>/")
@organization.route("/organization/pages/<id>/<path:page>")
def show(id, page=None):
    if page:
        page = page.lstrip('/')
    _template_setup_org(id)

    context = {"for_view": True}
    org_dict = tk.get_action("organization_show")(context, {"id": id})

    if not page:
        return _org_list_pages(id, org_dict)
    _page = tk.get_action("ckanext_pages_show")(
        data_dict={"org_id": tk.c.group_dict["id"], "page": page,}
    )
    if _page is None:
        return _org_list_pages(id, org_dict)
    tk.c.page = _page

    return tk.render(
        "ckanext_pages/organization_page.html",
        {"group_type": "organization", "group_dict": org_dict},
    )
