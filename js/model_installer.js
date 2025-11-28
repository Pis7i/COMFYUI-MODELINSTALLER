import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

console.log("[PMA Utils] Loading extension...");

const EXTENSION_NAME = "PMAUtils";
let shutdownStatusButton = null;
let shutdownCheckInterval = null;

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

async function checkShutdownStatus() {
    try {
        const response = await api.fetchApi("/pma_utils/shutdown_status", {
            method: "GET"
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.enabled && shutdownStatusButton) {
                shutdownStatusButton.style.display = "inline-block";
                shutdownStatusButton.textContent = `⏱️ Shutdown in ${formatTime(data.time_remaining)}`;
                shutdownStatusButton.style.background = data.time_remaining < 120 ? "#cc0000" : "#cc6600";
            } else if (shutdownStatusButton) {
                shutdownStatusButton.style.display = "none";
            }
        }
    } catch (error) {
        console.error(`[${EXTENSION_NAME}] Error checking shutdown status:`, error);
    }
}

function addMenuButton() {
    const buttonGroup = document.querySelector(".comfyui-button-group");

    if (!buttonGroup) {
        console.warn(`[${EXTENSION_NAME}] ComfyUI button group not found. Retrying...`);
        setTimeout(addMenuButton, 500);
        return;
    }

    if (document.getElementById("pma-utils-button")) {
        console.log(`[${EXTENSION_NAME}] Button already exists.`);
        return;
    }

    const pmaUtilsButton = document.createElement("button");
    pmaUtilsButton.textContent = "PMA Utils";
    pmaUtilsButton.id = "pma-utils-button";
    pmaUtilsButton.title = "PMA Utilities";

    pmaUtilsButton.onclick = async () => {
        openUtilsDialog();
    };

    buttonGroup.appendChild(pmaUtilsButton);
    console.log(`[${EXTENSION_NAME}] PMA Utils button added to .comfyui-button-group.`);

    shutdownStatusButton = document.createElement("button");
    shutdownStatusButton.id = "shutdown-status-button";
    shutdownStatusButton.style.display = "none";
    shutdownStatusButton.style.cssText = `
        padding: 8px 16px;
        background: #cc6600;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: default;
        font-size: 13px;
        font-family: monospace;
        display: none;
    `;
    buttonGroup.appendChild(shutdownStatusButton);

    shutdownCheckInterval = setInterval(checkShutdownStatus, 1000);

    const menu = document.querySelector(".comfy-menu");
    if (!buttonGroup.contains(pmaUtilsButton) && menu && !menu.contains(pmaUtilsButton)) {
        console.warn(`[${EXTENSION_NAME}] Failed to append button to group, falling back to menu.`);
        const settingsButton = menu.querySelector("#comfy-settings-button");
        if (settingsButton) {
            settingsButton.insertAdjacentElement("beforebegin", pmaUtilsButton);
        } else {
            menu.appendChild(pmaUtilsButton);
        }
    }
}

function openUtilsDialog() {
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

    const dialog = document.createElement("div");
    dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #202020;
        border: 2px solid #444;
        border-radius: 8px;
        padding: 0;
        min-width: 700px;
        max-width: 900px;
        max-height: 85vh;
        overflow: hidden;
        z-index: 10000;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        display: flex;
        flex-direction: column;
    `;

    const header = document.createElement("div");
    header.style.cssText = "padding: 20px; border-bottom: 1px solid #444;";
    
    const title = document.createElement("h2");
    title.textContent = "PMA Utils";
    title.style.cssText = "margin: 0; color: #fff;";
    header.appendChild(title);

    const tabs = document.createElement("div");
    tabs.style.cssText = "display: flex; gap: 0; border-bottom: 1px solid #444; background: #181818;";

    const tabButtons = [];
    const tabContents = [];

    function createTab(name, content) {
        const tabButton = document.createElement("button");
        tabButton.textContent = name;
        tabButton.style.cssText = `
            padding: 12px 24px;
            background: #181818;
            color: #aaa;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        `;
        
        const tabContent = document.createElement("div");
        tabContent.style.cssText = "display: none; padding: 20px; overflow-y: auto; max-height: 60vh;";
        tabContent.appendChild(content);

        tabButton.onclick = () => {
            tabButtons.forEach(btn => {
                btn.style.background = "#181818";
                btn.style.color = "#aaa";
                btn.style.borderBottom = "2px solid transparent";
            });
            tabContents.forEach(tc => tc.style.display = "none");
            
            tabButton.style.background = "#202020";
            tabButton.style.color = "#fff";
            tabButton.style.borderBottom = "2px solid #0066cc";
            tabContent.style.display = "block";
        };

        tabs.appendChild(tabButton);
        tabButtons.push(tabButton);
        tabContents.push(tabContent);
        
        return { button: tabButton, content: tabContent };
    }

    const modelInstallerContent = createModelInstallerTab();
    const shutdownContent = createShutdownTab(overlay);

    createTab("Model Installer", modelInstallerContent);
    createTab("Auto Shutdown", shutdownContent);

    tabButtons[0].click();

    dialog.appendChild(header);
    dialog.appendChild(tabs);
    tabContents.forEach(tc => dialog.appendChild(tc));

    const closeButton = document.createElement("button");
    closeButton.textContent = "Close";
    closeButton.style.cssText = `
        margin: 20px;
        padding: 8px 16px;
        background: #444;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        align-self: flex-end;
    `;
    closeButton.onmouseover = () => closeButton.style.background = "#555";
    closeButton.onmouseout = () => closeButton.style.background = "#444";
    closeButton.onclick = () => {
        document.body.removeChild(overlay);
    };
    dialog.appendChild(closeButton);

    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
}

function createModelInstallerTab() {
    const container = document.createElement("div");
    
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
    statusText.textContent = "Ready to download models...\n";
    
    const startButton = document.createElement("button");
    startButton.textContent = "Start Download";
    startButton.style.cssText = `
        padding: 10px 20px;
        background: #0066cc;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    `;
    startButton.onmouseover = () => startButton.style.background = "#0052a3";
    startButton.onmouseout = () => startButton.style.background = "#0066cc";
    
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
    
    container.appendChild(statusText);
    container.appendChild(startButton);
    
    return container;
}

function createShutdownTab(overlay) {
    const container = document.createElement("div");
    
    const description = document.createElement("p");
    description.textContent = "Automatically shutdown the RunPod instance after 10 minutes of inactivity.";
    description.style.cssText = "color: #aaa; margin-bottom: 20px;";
    
    const statusContainer = document.createElement("div");
    statusContainer.style.cssText = "margin-bottom: 20px;";
    
    const statusLabel = document.createElement("div");
    statusLabel.style.cssText = "color: #fff; margin-bottom: 10px; font-size: 16px;";
    statusLabel.textContent = "Status: Loading...";
    
    const timeLabel = document.createElement("div");
    timeLabel.style.cssText = "color: #aaa; font-size: 14px;";
    
    const toggleButton = document.createElement("button");
    toggleButton.style.cssText = `
        padding: 10px 20px;
        background: #444;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        margin-top: 10px;
    `;
    
    async function updateShutdownStatus() {
        try {
            const response = await api.fetchApi("/pma_utils/shutdown_status", {
                method: "GET"
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.enabled) {
                    statusLabel.textContent = "Status: ✅ Enabled";
                    statusLabel.style.color = "#00cc00";
                    timeLabel.textContent = `Time until shutdown: ${formatTime(data.time_remaining)}`;
                    toggleButton.textContent = "Disable Auto Shutdown";
                    toggleButton.style.background = "#cc0000";
                } else {
                    statusLabel.textContent = "Status: ❌ Disabled";
                    statusLabel.style.color = "#cc0000";
                    timeLabel.textContent = "";
                    toggleButton.textContent = "Enable Auto Shutdown";
                    toggleButton.style.background = "#00cc00";
                }
            }
        } catch (error) {
            console.error(`[${EXTENSION_NAME}] Error fetching shutdown status:`, error);
        }
    }
    
    toggleButton.onclick = async () => {
        try {
            const response = await api.fetchApi("/pma_utils/shutdown_toggle", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });
            
            if (response.ok) {
                await updateShutdownStatus();
            }
        } catch (error) {
            console.error(`[${EXTENSION_NAME}] Error toggling shutdown:`, error);
        }
    };
    
    updateShutdownStatus();
    const interval = setInterval(updateShutdownStatus, 1000);
    
    overlay.addEventListener("remove", () => clearInterval(interval));
    
    statusContainer.appendChild(statusLabel);
    statusContainer.appendChild(timeLabel);
    
    container.appendChild(description);
    container.appendChild(statusContainer);
    container.appendChild(toggleButton);
    
    return container;
}

app.registerExtension({
    name: "PMAUtils.Main",
    async setup() {
        console.log(`[${EXTENSION_NAME}] Setting up PMA Utils Extension...`);
        addMenuButton();
        console.log(`[${EXTENSION_NAME}] Extension setup complete.`);
    },
});

console.log("[PMA Utils] Extension registered successfully");
