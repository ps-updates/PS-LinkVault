from aiohttp import web
from datetime import datetime

async def start_webserver(client, port):
    routes = web.RouteTableDef()

    @routes.get("/", allow_head=True)
    async def root_handler(request):
        return web.json_response({"status": "running"})

    @routes.get("/info", allow_head=True)
    async def info_handler(request):
        uptime = int((datetime.now() - client.uptime).total_seconds())
        return web.json_response({
            "username": client.username,
            "first_name": client.first_name,
        })

    app = web.Application(client_max_size=30 * 1024 * 1024)
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    client.log(__name__).info(f"✅ Web server running at {port}")
