from .model_downloader import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, WEB_DIRECTORY, download_handler
import server

try:
    if hasattr(server.PromptServer, 'instance') and server.PromptServer.instance is not None:
        server.PromptServer.instance.routes.post("/model_installer/download")(download_handler)
except Exception as e:
    print(f"[ModelInstaller] Warning: Could not register route immediately: {e}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
