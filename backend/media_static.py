from fastapi.staticfiles import StaticFiles


class MediaStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            response.headers.setdefault(
                "Cache-Control",
                "public, max-age=31536000, immutable",
            )
        return response
