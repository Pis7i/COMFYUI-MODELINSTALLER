from .model_downloader import NODE_CLASS_MAPPINGS as MODEL_NODES, NODE_DISPLAY_NAME_MAPPINGS as MODEL_NAMES, WEB_DIRECTORY, download_handler
from .shutdown_monitor import shutdown_status_handler, shutdown_toggle_handler, activity_ping_handler, shutdown_monitor
from .character_swap_node import NODE_CLASS_MAPPINGS as CHAR_NODES, NODE_DISPLAY_NAME_MAPPINGS as CHAR_NAMES
from .eye_stabilizer_node import NODE_CLASS_MAPPINGS as EYE_NODES, NODE_DISPLAY_NAME_MAPPINGS as EYE_NAMES
import server

NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(MODEL_NODES)
NODE_CLASS_MAPPINGS.update(CHAR_NODES)
NODE_CLASS_MAPPINGS.update(EYE_NODES)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(MODEL_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(CHAR_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(EYE_NAMES)

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
        print("[PMA Utils] Character swap nodes loaded")
        print("[PMA Utils] Eye stabilizer node loaded")
except Exception as e:
    print(f"[PMA Utils] Warning: Could not register routes immediately: {e}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
