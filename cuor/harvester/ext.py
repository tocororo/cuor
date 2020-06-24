from .cli import harvester


class CuORHarvester(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.cli.add_command(harvester)
        app.extensions['cuor-harvester'] = self
