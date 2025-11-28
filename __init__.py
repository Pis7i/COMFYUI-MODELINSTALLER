from .model_downloader import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, WEB_DIRECTORY, download_handler
from .shutdown_monitor import shutdown_status_handler, shutdown_toggle_handler, activity_ping_handler, shutdown_monitor
import server

try:
    if hasattr(server.PromptServer, 'instance') and server.PromptServer.instance is not None:
        routes = server.PromptServer.instance.routes
        routes.post("/model_installer/download")(download_handler)
        routes.get("/pma_utils/shutdown_status")(shutdown_status_handler)
        routes.post("/pma_utils/shutdown_toggle")(shutdown_toggle_handler)
        routes.post("/pma_utils/activity_ping")(activity_ping_handler)
        
        shutdown_monitor.set_prompt_server(server.PromptServer.instance)
        
        print("[PMA Utils] All routes registered successfully")
        print("[PMA Utils] Shutdown monitor initialized with queue tracking")
except Exception as e:
    print(f"[PMA Utils] Warning: Could not register routes immediately: {e}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
