import importlib
import inspect
import os.path
import sys

from aiohttp import web

from aiogram_dialog.tools.preview import render_preview_content


class Controller:
    def __init__(self, app_module, app_registry):
        self.app_module = importlib.import_module(app_module)
        self.app_registry = app_registry

    async def __call__(self, request):
        self.app_module = importlib.reload(self.app_module)
        raw_registry = getattr(self.app_module, self.app_registry)
        if inspect.iscoroutinefunction(raw_registry):
            registry = await raw_registry()
        elif inspect.isfunction(raw_registry):
            registry = raw_registry()
        else:
            registry = raw_registry

        text = await render_preview_content(registry)
        return web.Response(
            text=text,
            headers={"Content-Type": "text/html"},
        )


def main():
    path,_, app_spec = sys.argv[1].rpartition(os.path.sep)
    print(path, app_spec)
    if path:
        sys.path.append(path)
    else:
        sys.path.append(os.curdir)
    app_module, app_registry = app_spec.split(":")
    controller = Controller(app_module, app_registry)
    routes = web.RouteTableDef()
    routes.get("/")(controller)

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
