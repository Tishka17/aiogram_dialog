import asyncio
import importlib
import inspect
import os.path
import sys
from concurrent.futures import ProcessPoolExecutor
from tempfile import NamedTemporaryFile

from aiohttp import web

from aiogram_dialog.tools.preview import render_preview_content
from aiogram_dialog.tools.transitions import render_transitions


class Renderer:
    def __init__(self, app_module, app_registry):
        self.app_module = app_module
        self.app_registry = app_registry

    async def _get_registry(self):
        app_module = importlib.import_module(self.app_module)
        raw_registry = getattr(app_module, self.app_registry)
        if inspect.iscoroutinefunction(raw_registry):
            registry = await raw_registry()
        elif inspect.isfunction(raw_registry):
            registry = raw_registry()
        else:
            registry = raw_registry
        return registry

    async def _load_preview(self):
        registry = await self._get_registry()
        return await render_preview_content(registry)

    async def _load_transitions(self, path: str):
        registry = await self._get_registry()
        name = path.removesuffix(".png")
        render_transitions(registry, filename=name)

    def load_preview(self):
        return asyncio.run(self._load_preview())

    def load_transitions(self, path):
        return asyncio.run(self._load_transitions(path))


class Controller:
    def __init__(self, app_module, app_registry):
        self.renderer = Renderer(app_module, app_registry)

    async def preview(self, _request):
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor(max_workers=1) as executor:
            text = await loop.run_in_executor(
                executor, self.renderer.load_preview,
            )
        return web.Response(
            text=text,
            headers={"Content-Type": "text/html"},
        )

    async def transitions(self, _request):
        loop = asyncio.get_event_loop()
        with NamedTemporaryFile(suffix=".png") as f:
            with ProcessPoolExecutor(max_workers=1) as executor:
                await loop.run_in_executor(
                    executor, self.renderer.load_transitions, f.name,
                )
            return web.Response(
                body=f.read(),
                headers={"Content-Type": "image/png"},
            )


PORT = 9876
INTRO = f"""
Aiogram Dialog
====================

HTML preview:
http://127.0.0.1:{PORT}/

PNG transitions diagram:
http://127.0.0.1:{PORT}/transitions

======================
"""


def disable_print(*_args, **_kwargs):
    pass


def main():
    path, _, app_spec = sys.argv[1].rpartition(os.path.sep)
    if path:
        sys.path.append(path)
    else:
        sys.path.append(os.curdir)
    app_module, app_registry = app_spec.split(":")
    controller = Controller(app_module, app_registry)
    routes = web.RouteTableDef()
    routes.get("/transitions")(controller.transitions)
    routes.get("/")(controller.preview)

    app = web.Application()
    app.add_routes(routes)
    print(INTRO)  # noqa: T201
    web.run_app(app, port=PORT, print=disable_print)
