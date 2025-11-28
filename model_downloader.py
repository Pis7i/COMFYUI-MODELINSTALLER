import os
import subprocess
import folder_paths
from aiohttp import web
import asyncio


class ModelDownloader:
    MODELS = [
        {
            "url": "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors",
            "path": "controlnet/diffusion_pytorch_model_promax.safetensors",
            "name": "ControlNet Union SDXL"
        },
        {
            "url": "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/facerestore_models/GFPGANv1.3.pth",
            "path": "facerestore_models/GFPGANv1.3.pth",
            "name": "GFPGAN Face Restore"
        },
        {
            "url": "https://huggingface.co/thesudio/clip_vision_SDXL_vit-h.safetensors/resolve/main/SDXLopen_clip_pytorch_model_vit_h.safetensors",
            "path": "clip_vision/SDXLopen_clip_pytorch_model_vit_h.safetensors",
            "name": "CLIP Vision SDXL"
        },
        {
            "url": "https://huggingface.co/pmabtz/gonzalomoXLFluxPony_v60PhotoXLDMD.safetensors/resolve/main/gonzalomoXLFluxPony_v60PhotoXLDMD.safetensors",
            "path": "checkpoints/gonzalomoXLFluxPony_v60PhotoXLDMD.safetensors",
            "name": "GonzalomoXL Checkpoint"
        },
        {
            "url": "https://www.dropbox.com/scl/fi/gz7e4zv3v6rh2l82uals5/ip-adapter-faceid-plusv2_sdxl.bin?rlkey=lk1yw94ndgfxggxohu136eki0&st=98jiced8&dl=0",
            "path": "ipadapter/ip-adapter-faceid-plusv2_sdxl.bin",
            "name": "IP-Adapter FaceID Plus v2"
        },
        {
            "url": "https://www.dropbox.com/scl/fi/xsflrbsfnl95gnagfxo44/SwinIR_4x.pth?rlkey=4fny62ak5fymel7h16ctnguaw&st=6jp0cxo4&dl=0",
            "path": "upscale_models/SwinIR_4x.pth",
            "name": "SwinIR 4x Upscaler"
        },
        {
            "url": "https://www.dropbox.com/scl/fi/gwghcy1adp1mloxnppqou/epiCNegative.pt?rlkey=f2zz5zzbgg984835mojueao65&st=03dalxxr&dl=0",
            "path": "embeddings/epiCNegative.pt",
            "name": "EpiC Negative Embedding"
        },
        {
            "url": "https://www.dropbox.com/scl/fi/h0pi6xyjozna49kophedo/ng_deepnegative_v1_75t.pt?rlkey=1ndqdpixtfhte6odhnq155tmy&st=hf53oek5&dl=0",
            "path": "embeddings/ng_deepnegative_v1_75t.pt",
            "name": "Deep Negative Embedding"
        }
    ]

    @staticmethod
    async def download_models_stream(response):
        base_dir = folder_paths.base_path
        
        for idx, model in enumerate(ModelDownloader.MODELS, 1):
            full_path = os.path.join(base_dir, "models", model["path"])
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            if os.path.exists(full_path):
                msg = f"[{idx}/{len(ModelDownloader.MODELS)}] ⏭️  Skipping {model['name']} (already exists)\n"
                await response.write(msg.encode())
                continue
            
            msg = f"[{idx}/{len(ModelDownloader.MODELS)}] 📥 Downloading {model['name']}...\n"
            await response.write(msg.encode())
            
            try:
                process = await asyncio.create_subprocess_exec(
                    "wget", "-q", "--show-progress", "-c", "-O", full_path, model["url"],
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                while True:
                    line = await process.stderr.readline()
                    if not line:
                        break
                    await response.write(line)
                
                await process.wait()
                
                if process.returncode == 0:
                    msg = f"✅ {model['name']} downloaded successfully\n\n"
                else:
                    msg = f"❌ {model['name']} failed to download\n\n"
                await response.write(msg.encode())
                
            except FileNotFoundError:
                msg = "❌ wget command not found. Please install wget.\n"
                await response.write(msg.encode())
                return
            except Exception as e:
                msg = f"❌ Error downloading {model['name']}: {str(e)}\n\n"
                await response.write(msg.encode())
        
        final_msg = "\n🎉 Download process completed!\n"
        await response.write(final_msg.encode())


async def download_handler(request):
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Cache-Control'] = 'no-cache'
    await response.prepare(request)
    
    await ModelDownloader.download_models_stream(response)
    
    await response.write_eof()
    return response


WEB_DIRECTORY = "./js"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
