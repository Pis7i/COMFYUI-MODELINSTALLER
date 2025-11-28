import os
import time
import threading
import subprocess
from aiohttp import web
import json


class ShutdownMonitor:
    def __init__(self):
        self.enabled = False
        self.last_activity = time.time()
        self.timeout = 600
        self.monitor_thread = None
        self.running = False
        self.prompt_server = None
        
    def set_prompt_server(self, server):
        self.prompt_server = server
        
    def reset_timer(self):
        self.last_activity = time.time()
    
    def is_queue_active(self):
        if not self.prompt_server:
            return False
            
        try:
            queue_info = self.prompt_server.prompt_queue.get_queue_info()
            
            queue_pending = queue_info.get('queue_pending', [])
            queue_running = queue_info.get('queue_running', [])
            
            has_items = len(queue_pending) > 0 or len(queue_running) > 0
            
            if has_items:
                self.reset_timer()
                
            return has_items
        except Exception as e:
            print(f"[PMA Utils] Error checking queue: {e}")
            return False
    
    def get_time_remaining(self):
        if not self.enabled:
            return 0
        elapsed = time.time() - self.last_activity
        remaining = max(0, self.timeout - elapsed)
        return int(remaining)
    
    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.reset_timer()
            if not self.running:
                self.start_monitoring()
        return self.enabled
    
    def start_monitoring(self):
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        while self.running:
            if self.enabled:
                self.is_queue_active()
                
                time_remaining = self.get_time_remaining()
                
                if time_remaining <= 0:
                    print("[PMA Utils] Queue empty for 10 minutes. Shutting down RunPod...")
                    self._shutdown_runpod()
                    break
            
            time.sleep(1)
    
    def _shutdown_runpod(self):
        runpod_pod_id = os.environ.get('RUNPOD_POD_ID')
        runpod_api_key = os.environ.get('RUNPOD_API_KEY')
        
        if runpod_pod_id and runpod_api_key:
            try:
                query = f'''
                mutation {{
                    podTerminate(input: {{podId: "{runpod_pod_id}"}}) {{
                        id
                    }}
                }}
                '''
                
                subprocess.run([
                    'curl', '-X', 'POST',
                    '-H', 'Content-Type: application/json',
                    '-H', f'Authorization: Bearer {runpod_api_key}',
                    'https://api.runpod.io/graphql',
                    '-d', json.dumps({'query': query})
                ], check=True)
                
                print("[PMA Utils] RunPod termination request sent successfully")
            except Exception as e:
                print(f"[PMA Utils] Failed to terminate RunPod: {e}")
        else:
            print("[PMA Utils] RunPod environment variables not found. Cannot shutdown.")
            subprocess.run(['killall', '-9', 'python'])


shutdown_monitor = ShutdownMonitor()


async def shutdown_status_handler(request):
    return web.json_response({
        'enabled': shutdown_monitor.enabled,
        'time_remaining': shutdown_monitor.get_time_remaining()
    })


async def shutdown_toggle_handler(request):
    enabled = shutdown_monitor.toggle()
    return web.json_response({
        'enabled': enabled,
        'time_remaining': shutdown_monitor.get_time_remaining()
    })


async def activity_ping_handler(request):
    shutdown_monitor.reset_timer()
    return web.json_response({'status': 'ok'})
