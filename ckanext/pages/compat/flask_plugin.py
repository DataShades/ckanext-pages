import ckan.plugins as p
import ckanext.pages.views as views


class PagesMixin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    def get_blueprint(self):
        blueprints = [views.pages, views.blog]
        if self.organization_pages:
            blueprints.append(views.organization)
        if self.group_pages:
            blueprints.append(views.group)
        return blueprints
