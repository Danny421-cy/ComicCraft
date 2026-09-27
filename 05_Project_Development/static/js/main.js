/**
 * ComicCraft — Client Interactive Logic & Presets
 */

const PRESETS = {
    superhero: {
        prompt: "A cybernetically enhanced detective defends Neo-Tokyo against an AI crime syndicate that hacked the city's power grid.",
        character: "Cipher Knight",
        setting: "Neon Neo-Tokyo, 2099",
        tone: "Superhero / Action",
        style: "Classic Comic Book"
    },
    scifi: {
        prompt: "An orbital archaeologist activates an ancient alien monolith on Jupiter's moon, awakening a dormant star gate.",
        character: "Dr. Elena Vance",
        setting: "Europa Sub-Surface Research Base",
        tone: "Sci-Fi / Cyberpunk",
        style: "Dark Cyberpunk"
    },
    steampunk: {
        prompt: "A Victorian clockmaker discovers that the Great Clock of London controls the flow of time and someone has stolen a golden gear.",
        character: "Barnaby Cogsworth",
        setting: "Cobblestone Gaslit London, 1888",
        tone: "Mystery / Noir",
        style: "Vintage Pop Art"
    },
    fantasy: {
        prompt: "A rookie dragon courier must deliver an urgent royal peace treaty across a treacherous mountain range during a thunder vortex.",
        character: "Kaelen & Zephyr",
        setting: "The Floating Spires of Aethelgard",
        tone: "Epic Fantasy",
        style: "Graphic Novel Realism"
    }
};

function applyPreset(key) {
    const data = PRESETS[key];
    if (!data) return;

    const promptEl = document.getElementById("story_prompt");
    const charEl = document.getElementById("character_name");
    const settingEl = document.getElementById("setting");
    const toneEl = document.getElementById("tone");
    const styleEl = document.getElementById("art_style");

    if (promptEl) promptEl.value = data.prompt;
    if (charEl) charEl.value = data.character;
    if (settingEl) settingEl.value = data.setting;
    if (toneEl) toneEl.value = data.tone;
    if (styleEl) styleEl.value = data.style;

    // Subtle highlight pulse
    if (promptEl) {
        promptEl.style.borderColor = "#FF3E3E";
        setTimeout(() => {
            promptEl.style.borderColor = "";
        }, 500);
    }
}

// Progress Steps Simulation during Comic Generation
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("comicForm");
    const overlay = document.getElementById("loadingOverlay");
    const statusText = document.getElementById("loadingStatusText");
    const progressBar = document.getElementById("progressBar");

    if (!form || !overlay) return;

    form.addEventListener("submit", (e) => {
        const promptInput = document.getElementById("story_prompt");
        if (!promptInput.value.trim()) {
            e.preventDefault();
            alert("Please enter a story prompt before generating!");
            promptInput.focus();
            return;
        }

        // Show loading modal
        overlay.style.display = "flex";

        const steps = [
            { text: "Gemini Flash is drafting the 5-panel dramatic arc...", pct: 25, active: "step1" },
            { text: "Gemini Pro is scripting character dialogue & sound effects...", pct: 50, active: "step2" },
            { text: "Diffusion AI is rendering stylized visual panel illustrations...", pct: 75, active: "step3" },
            { text: "Layout builder is compiling typography, bubbles & printable PDF...", pct: 90, active: "step4" }
        ];

        let currentIdx = 0;
        const interval = setInterval(() => {
            if (currentIdx < steps.length) {
                const s = steps[currentIdx];
                if (statusText) statusText.innerText = s.text;
                if (progressBar) progressBar.style.width = `${s.pct}%`;

                // Update step pills
                document.querySelectorAll(".step-pill").forEach(el => el.classList.remove("current"));
                const pill = document.getElementById(s.active);
                if (pill) pill.classList.add("current");

                if (currentIdx > 0) {
                    const prevPill = document.getElementById(steps[currentIdx - 1].active);
                    if (prevPill) {
                        prevPill.classList.remove("current");
                        prevPill.classList.add("done");
                    }
                }
                currentIdx++;
            } else {
                clearInterval(interval);
            }
        }, 3200);
    });
});

