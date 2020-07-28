import ckan.plugins as p


class PagesMixin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    def after_map(self, map):
        controller = "ckanext.pages.controller:PagesController"

        if self.organization_pages:
            map.connect(
                "pages_organization.delete",
                "/organization/pages_delete/{id}{page:/.*|}",
                action="org_delete",
                ckan_icon="delete",
                controller=controller,
            )
            map.connect(
                "pages_organization.edit",
                "/organization/pages_edit/{id}{page:/.*|}",
                action="org_edit",
                ckan_icon="edit",
                controller=controller,
            )
            map.connect(
                "pages_organization.index",
                "/organization/pages/{id}",
                action="org_show",
                ckan_icon="file",
                controller=controller,
                highlight_actions="org_edit org_show",
                page="",
            )
            map.connect(
                "pages_organization.show",
                "/organization/pages/{id}{page:/.*|}",
                action="org_show",
                ckan_icon="file",
                controller=controller,
                highlight_actions="org_edit org_show",
            )

        if self.group_pages:
            map.connect(
                "pages_group.delete",
                "/group/pages_delete/{id}{page:/.*|}",
                action="group_delete",
                ckan_icon="delete",
                controller=controller,
            )
            map.connect(
                "pages_group.edit",
                "/group/pages_edit/{id}{page:/.*|}",
                action="group_edit",
                ckan_icon="edit",
                controller=controller,
            )
            map.connect(
                "pages_group.index",
                "/group/pages/{id}",
                action="group_show",
                ckan_icon="file",
                controller=controller,
                highlight_actions="group_edit group_show",
                page="",
            )
            map.connect(
                "pages_group.show",
                "/group/pages/{id}{page:/.*|}",
                action="group_show",
                ckan_icon="file",
                controller=controller,
                highlight_actions="group_edit group_show",
            )

        map.connect(
            "pages.delete",
            "/pages_delete{page:/.*|}",
            action="pages_delete",
            ckan_icon="delete",
            controller=controller,
        )
        map.connect(
            "pages.edit",
            "/pages_edit{page:/.*|}",
            action="pages_edit",
            ckan_icon="edit",
            controller=controller,
        )
        map.connect(
            "pages.index",
            "/pages",
            action="pages_index",
            ckan_icon="file",
            controller=controller,
            highlight_actions="pages_edit pages_index pages_show",
        )
        map.connect(
            "pages.show",
            "/pages{page:/.*|}",
            action="pages_show",
            ckan_icon="file",
            controller=controller,
            highlight_actions="pages_edit pages_index pages_show",
        )
        map.connect(
            "pages.upload",
            "/pages_upload",
            action="pages_upload",
            controller=controller,
        )

        map.connect(
            "blog.delete",
            "/blog_delete{page:/.*|}",
            action="blog_delete",
            ckan_icon="delete",
            controller=controller,
        )
        map.connect(
            "blog.edit",
            "/blog_edit{page:/.*|}",
            action="blog_edit",
            ckan_icon="edit",
            controller=controller,
        )
        map.connect(
            "blog.index",
            "/blog",
            action="blog_index",
            ckan_icon="file",
            controller=controller,
            highlight_actions="blog_edit blog_index blog_show",
        )
        map.connect(
            "blog.show",
            "/blog{page:/.*|}",
            action="blog_show",
            ckan_icon="file",
            controller=controller,
            highlight_actions="blog_edit blog_index blog_show",
        )
        return map
