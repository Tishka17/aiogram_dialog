import asyncio
import importlib
import inspect
import os.path
import sys
from concurrent.futures import ProcessPoolExecutor

from aiohttp import web

from aiogram_dialog.tools.preview import render_preview_content


class Renderer:
    def __init__(self, app_module, app_registry):
        self.app_module = app_module
        self.app_registry = app_registry

    async def _load_preview(self, raw_registry):
        if inspect.iscoroutinefunction(raw_registry):
            registry = await raw_registry()
        elif inspect.isfunction(raw_registry):
            registry = raw_registry()
        else:
            registry = raw_registry

        return await render_preview_content(registry)

    def load(self):
        app_module = importlib.import_module(self.app_module)
        raw_registry = getattr(app_module, self.app_registry)
        return asyncio.run(self._load_preview(raw_registry))


class Controller:
    def __init__(self, app_module, app_registry):
        self.renderer = Renderer(app_module, app_registry)

    async def __call__(self, request):
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor(max_workers=1) as executor:
            text = await loop.run_in_executor(executor, self.renderer.load)
        return web.Response(
            text=text,
            headers={"Content-Type": "text/html"},
        )


def main():
    path, _, app_spec = sys.argv[1].rpartition(os.path.sep)
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
