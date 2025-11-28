import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

console.log("[ModelInstaller] Loading extension...");

const EXTENSION_NAME = "ModelInstaller";

function addMenuButton() {
    const buttonGroup = document.querySelector(".comfyui-button-group");

    if (!buttonGroup) {
        console.warn(`[${EXTENSION_NAME}] ComfyUI button group not found. Retrying...`);
        setTimeout(addMenuButton, 500);
        return;
    }

    if (document.getElementById("model-installer-button")) {
        console.log(`[${EXTENSION_NAME}] Button already exists.`);
        return;
    }

    const modelInstallerButton = document.createElement("button");
    modelInstallerButton.textContent = "Install Models";
    modelInstallerButton.id = "model-installer-button";
    modelInstallerButton.title = "Download and Install Models";

    modelInstallerButton.onclick = async () => {
        const dialog = document.createElement("div");
        dialog.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #202020;
            border: 2px solid #444;
            border-radius: 8px;
            padding: 20px;
            min-width: 600px;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            z-index: 10000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        `;
        
        const title = document.createElement("h2");
        title.textContent = "Model Installer";
        title.style.cssText = "margin: 0 0 15px 0; color: #fff;";
        
        const progressContainer = document.createElement("div");
        progressContainer.style.cssText = "margin: 15px 0;";
        
        const statusText = document.createElement("div");
        statusText.style.cssText = `
            font-family: monospace;
            font-size: 13px;
            color: #aaa;
            background: #151515;
            padding: 15px;
            border-radius: 4px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            margin-bottom: 15px;
        `;
        statusText.textContent = "Starting download process...\n";
        
        const buttonContainer = document.createElement("div");
        buttonContainer.style.cssText = "display: flex; gap: 10px; justify-content: flex-end;";
        
        const startButton = document.createElement("button");
        startButton.textContent = "Start Download";
        startButton.style.cssText = `
            padding: 8px 16px;
            background: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        `;
        startButton.onmouseover = () => startButton.style.background = "#0052a3";
        startButton.onmouseout = () => startButton.style.background = "#0066cc";
        
        const closeButton = document.createElement("button");
        closeButton.textContent = "Close";
        closeButton.style.cssText = `
            padding: 8px 16px;
            background: #444;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        `;
        closeButton.onmouseover = () => closeButton.style.background = "#555";
        closeButton.onmouseout = () => closeButton.style.background = "#444";
        closeButton.onclick = () => {
            document.body.removeChild(overlay);
        };
        
        startButton.onclick = async () => {
            startButton.disabled = true;
            startButton.style.background = "#666";
            startButton.style.cursor = "not-allowed";
            statusText.textContent = "Initiating download...\n";
            
            try {
                const response = await api.fetchApi("/model_installer/download", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });
                
                if (response.ok) {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        const text = decoder.decode(value);
                        statusText.textContent += text;
                        statusText.scrollTop = statusText.scrollHeight;
                    }
                    
                    statusText.textContent += "\n✅ All downloads completed!\n";
                } else {
                    statusText.textContent += `\n❌ Error: ${response.statusText}\n`;
                }
            } catch (error) {
                statusText.textContent += `\n❌ Error: ${error.message}\n`;
            }
            
            startButton.textContent = "Download Complete";
        };
        
        buttonContainer.appendChild(startButton);
        buttonContainer.appendChild(closeButton);
        
        progressContainer.appendChild(statusText);
        
        dialog.appendChild(title);
        dialog.appendChild(progressContainer);
        dialog.appendChild(buttonContainer);
        
        const overlay = document.createElement("div");
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 9999;
        `;
        overlay.appendChild(dialog);
        
        document.body.appendChild(overlay);
    };

    buttonGroup.appendChild(modelInstallerButton);
    console.log(`[${EXTENSION_NAME}] Install Models button added to .comfyui-button-group.`);

    const menu = document.querySelector(".comfy-menu");
    if (!buttonGroup.contains(modelInstallerButton) && menu && !menu.contains(modelInstallerButton)) {
        console.warn(`[${EXTENSION_NAME}] Failed to append button to group, falling back to menu.`);
        const settingsButton = menu.querySelector("#comfy-settings-button");
        if (settingsButton) {
            settingsButton.insertAdjacentElement("beforebegin", modelInstallerButton);
        } else {
            menu.appendChild(modelInstallerButton);
        }
    }
}

app.registerExtension({
    name: "ModelInstaller.Downloader",
    async setup() {
        console.log(`[${EXTENSION_NAME}] Setting up Model Installer Extension...`);
        addMenuButton();
        console.log(`[${EXTENSION_NAME}] Extension setup complete.`);
    },
});

console.log("[ModelInstaller] Extension registered successfully");
