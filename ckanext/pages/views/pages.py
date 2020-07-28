from flask import Blueprint
import ckan.plugins as p
import ckan.lib.helpers as helpers
import ckantoolkit as tk

_ = p.toolkit._
config = p.toolkit.config

pages = Blueprint("pages", __name__)


def _inject_views_into_page(_page):
    # this is a good proxy to a version of CKAN with views enabled.
    if not p.plugin_loaded("image_view"):
        return
    try:
        import lxml
        import lxml.html
    except ImportError:
        return

    try:
        root = lxml.html.fromstring(_page["content"])
    # Return if any errors are found while parsing the content
    except (lxml.etree.XMLSyntaxError, lxml.etree.ParserError):
        return

    for element in root.findall(".//iframe"):
        embed_element = element.attrib.pop("data-ckan-view-embed", None)
        if not embed_element:
            continue
        element.tag = "div"
        error = None

        try:
            iframe_src = element.attrib.pop("src", "")
            width = element.attrib.pop("width", "80")
            if not width.endswith("%") and not width.endswith("px"):
                width = width + "px"
            height = element.attrib.pop("height", "80")
            if not height.endswith("%") and not height.endswith("px"):
                height = height + "px"
            align = element.attrib.pop("align", "none")
            style = (
                "width: %s; height: %s; float: %s; overflow: auto; vertical-align:middle; position:relative"
                % (width, height, align)
            )
            element.attrib["style"] = style
            element.attrib["class"] = "pages-embed"
            view = p.toolkit.get_action("resource_view_show")(
                {}, {"id": iframe_src[-36:]}
            )
            context = {}
            resource = p.toolkit.get_action("resource_show")(
                context, {"id": view["resource_id"]}
            )
            package_id = context["resource"].resource_group.package_id
            package = p.toolkit.get_action("package_show")(
                context, {"id": package_id}
            )
        except p.toolkit.ObjectNotFound:
            error = _(
                "ERROR: View not found {view_id}".format(view_id=iframe_src)
            )

        if error:
            resource_view_html = "<h4> %s </h4>" % error
        elif not helpers.resource_view_is_iframed(view):
            resource_view_html = helpers.rendered_resource_view(
                view, resource, package
            )
        else:
            src = helpers.url_for(
                "resource.view",
                qualified=True,
                id=package["name"],
                resource_id=resource["id"],
                view_id=view["id"],
            )
            message = _("Your browser does not support iframes.")
            resource_view_html = '<iframe src="{src}" frameborder="0" width="100%" height="100%" style="display:block"> <p>{message}</p> </iframe>'.format(
                src=src, message=message
            )

        view_element = lxml.html.fromstring(resource_view_html)
        element.append(view_element)

    new_content = lxml.html.tostring(root)
    if new_content.startswith("<div>") and new_content.endswith("</div>"):
        # lxml will add a <div> tag to text that starts with an HTML tag,
        # which will cause the rendering to fail
        new_content = new_content[5:-6]
    elif new_content.startswith("<p>") and new_content.endswith("</p>"):
        # lxml will add a <p> tag to plain text snippet, which will cause the
        # rendering to fail
        new_content = new_content[3:-4]
    _page["content"] = new_content


def _pages_list_pages(page_type):
    data_dict = {"org_id": None, "page_type": page_type}
    if page_type == "blog":
        data_dict["order_publish_date"] = True
    p.toolkit.c.pages_dict = p.toolkit.get_action("ckanext_pages_list")(
        data_dict=data_dict
    )
    p.toolkit.c.page = helpers.Page(
        collection=p.toolkit.c.pages_dict,
        page=p.toolkit.request.params.get("page", 1),
        url=helpers.pager_url,
        items_per_page=21,
    )

    if page_type == "blog":
        return p.toolkit.render("ckanext_pages/blog_list.html")
    return p.toolkit.render("ckanext_pages/pages_list.html")


@pages.route("/pages_delete/", methods=["POST", "GET"])
@pages.route("/pages_delete/<path:page>", methods=["POST", "GET"])
def delete(page=None, page_type="pages"):
    page = page[1:]
    if "cancel" in p.toolkit.request.params:
        return p.toolkit.redirect_to("%s.edit" % page_type, page="/" + page)

    try:
        if p.toolkit.request.method == "POST":
            p.toolkit.get_action("ckanext_pages_delete")({}, {"page": page})
            return p.toolkit.redirect_to("%s.index" % page_type)
        else:
            p.toolkit.abort(404, _("Page Not Found"))
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, _("Unauthorized to delete page"))
    except p.toolkit.ObjectNotFound:
        p.toolkit.abort(404, _("Group not found"))
    return p.toolkit.render(
        "ckanext_pages/confirm_delete.html", {"page": page}
    )


@pages.route("/pages_edit/", methods=["POST", "GET"])
@pages.route("/pages_edit/<path:page>", methods=["POST", "GET"])
def edit(
    page='', data=None, errors=None, error_summary=None, page_type="pages"
):
    if page:
        page = page[1:]
    _page = p.toolkit.get_action("ckanext_pages_show")(
        data_dict={"org_id": None, "page": page,}
    )
    if _page is None:
        _page = {}

    if p.toolkit.request.method == "POST" and not data:
        data = dict(p.toolkit.request.form)

        _page.update(data)

        _page["org_id"] = None
        _page["page"] = page
        _page["page_type"] = "page" if page_type == "pages" else page_type

        try:
            junk = p.toolkit.get_action("ckanext_pages_update")(
                data_dict=_page
            )
        except p.toolkit.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return edit(
                "/" + page, data, errors, error_summary, page_type=page_type
            )
        return p.toolkit.redirect_to(
            "%s.show" % page_type, page="/" + _page["name"]
        )

    try:
        p.toolkit.check_access(
            "ckanext_pages_update",
            {"user": p.toolkit.c.user or p.toolkit.c.author},
        )
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, _("Unauthorized to create or edit a page"))

    if not data:
        data = _page

    errors = errors or {}
    error_summary = error_summary or {}

    form_snippet = config.get(
        "ckanext.pages.form", "ckanext_pages/base_form.html"
    )

    vars = {
        "data": data,
        "errors": errors,
        "error_summary": error_summary,
        "page": page,
        "form_snippet": form_snippet,
    }

    return p.toolkit.render(
        "ckanext_pages/%s_edit.html" % page_type, extra_vars=vars
    )


@pages.route("/pages/")
@pages.route("/pages/<path:page>")
def show(page=None, page_type="page"):
    if not page:
        return _pages_list_pages("page")
    p.toolkit.c.page_type = page_type
    if page:
        page = page[1:]
    if not page:
        return _pages_list_pages(page_type)
    _page = p.toolkit.get_action("ckanext_pages_show")(
        data_dict={"org_id": None, "page": page}
    )
    if _page is None:
        return _pages_list_pages(page_type)
    p.toolkit.c.page = _page
    _inject_views_into_page(_page)

    return p.toolkit.render("ckanext_pages/%s.html" % page_type)


@pages.route("/pages_uploads", methods=["POST", "GET"])
def upload():
    if not p.toolkit.request.method == "POST":
        p.toolkit.abort(409, _("Only Posting is availiable"))

    try:
        url = p.toolkit.get_action("ckanext_pages_upload")(
            None, dict(p.toolkit.request.POST)
        )
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, _("Unauthorized to upload file %s") % id)

    return """<script type='text/javascript'>
                      window.parent.CKEDITOR.tools.callFunction(%s, '%s');
                  </script>""" % (
        p.toolkit.request.args["CKEditorFuncNum"],
        url["url"],
    )
