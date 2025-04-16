import random
import json
from collections import defaultdict
import gradio as gr
import os
import tempfile
import base64

# === Internal State ===
appearance_counts = defaultdict(int)
session_config = {"N": 10, "k": 3, "start": 1}

# === Core Batch Logic ===
def format_counts_for_table(counts_dict):
    if not counts_dict:
        return []
    return [[k, v] for k, v in sorted(counts_dict.items())]

def generate_fair_batch(N, k=3, start=1):
    global appearance_counts
    session_config.update({"N": N, "k": k, "start": start})
    if k > N:
        return f"❌ Batch size {k} cannot exceed N={N}.", []

    full_range = list(range(start, start + N))
    full_range_set = set(full_range)
    current_keys = set(appearance_counts.keys())
    out_of_range = current_keys - full_range_set

    warning = ""
    if out_of_range:
        warning = (f"⚠️ Warning: appearance_counts contains keys outside the range "
                   f"[{start}, {start + N - 1}]: {sorted(out_of_range)}.\n"
                   f"These will be ignored.")

    # Generate batch
    min_count = min(appearance_counts.get(i, 0) for i in full_range)
    eligible = [i for i in full_range if appearance_counts[i] == min_count]
    random.shuffle(eligible)

    batch = []
    while eligible and len(batch) < k:
        batch.append(eligible.pop())

    if len(batch) < k:
        remaining = [i for i in full_range if i not in batch]
        batch.extend(random.sample(remaining, k - len(batch)))

    for num in batch:
        appearance_counts[num] += 1

    batch_str = ", ".join(str(n) for n in batch)
    return (warning + "\n\n" if warning else "") + batch_str, format_counts_for_table(appearance_counts)

# === Reset, Clean, Save, Load ===
def reset_progress():
    global appearance_counts
    appearance_counts.clear()
    session_config.update({"N": 10, "k": 3, "start": 1})
    return "", [], 10, 3, 1

def clean_counts_to_current_range():
    global appearance_counts
    valid_range = set(range(session_config["start"], session_config["start"] + session_config["N"]))
    to_delete = [k for k in appearance_counts if k not in valid_range]
    for k in to_delete:
        del appearance_counts[k]
    return "✅ Out-of-range counts removed.", format_counts_for_table(appearance_counts)

def prepare_download_data(data, filename):
    """Convert data to base64 for download"""
    if isinstance(data, dict):
        data = json.dumps(data, indent=2)
    
    # Create a temporary file and return its path for downloading
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
        temp_file.write(data.encode('utf-8'))
        return temp_file.name

def save_counts_only():
    """Create a downloadable JSON file for the counts"""
    data = dict(appearance_counts)
    file_path = prepare_download_data(data, "appearance_counts.json")
    return file_path

def save_full_progress():
    """Create a downloadable JSON file for the full configuration"""
    data = {
        "appearance_counts": dict(appearance_counts),
        "N": session_config["N"],
        "k": session_config["k"],
        "start": session_config["start"]
    }
    file_path = prepare_download_data(data, "full_progress.json")
    return file_path

def load_counts_from_text(json_str):
    try:
        contents = json.loads(json_str)
        global appearance_counts
        appearance_counts = defaultdict(int, {int(k): v for k, v in contents.items()})
        N = session_config["N"]
        start = session_config["start"]
        valid_range = set(range(start, start + N))
        loaded_keys = set(appearance_counts.keys())
        outside_keys = loaded_keys - valid_range

        if outside_keys:
            warning = (f"⚠️ Warning: Loaded counts contain numbers outside current range "
                       f"[{start}, {start + N - 1}]: {sorted(outside_keys)}.\n"
                       f"Consider adjusting N/start, or use Full Load if unsure.")
        else:
            warning = "✅ Appearance counts loaded successfully."

        return warning, format_counts_for_table(appearance_counts)
    except Exception as e:
        return f"Error loading data: {str(e)}", format_counts_for_table(appearance_counts)

def load_full_from_text(json_str):
    try:
        contents = json.loads(json_str)
        global appearance_counts
        appearance_counts = defaultdict(int, {int(k): v for k, v in contents["appearance_counts"].items()})
        session_config.update({
            "N": contents["N"],
            "k": contents["k"],
            "start": contents["start"]
        })
        return "✅ Full progress restored.", format_counts_for_table(appearance_counts), contents["N"], contents["k"], contents["start"]
    except Exception as e:
        return f"Error loading data: {str(e)}", format_counts_for_table(appearance_counts), session_config["N"], session_config["k"], session_config["start"]

def load_from_file(file_obj):
    global appearance_counts
    
    if file_obj is None:
        return "❌ No file selected", format_counts_for_table(appearance_counts)
    
    try:
        file_content = file_obj.decode('utf-8')
        data = json.loads(file_content)
        
        # Check if it's a full config file or just counts
        if isinstance(data, dict) and "appearance_counts" in data:
            # It's a full config file
            appearance_counts = defaultdict(int, {int(k): v for k, v in data["appearance_counts"].items()})
            session_config.update({
                "N": data["N"],
                "k": data["k"],
                "start": data["start"]
            })
            return "✅ Full configuration loaded!", format_counts_for_table(appearance_counts), data["N"], data["k"], data["start"]
        else:
            # It's just counts
            appearance_counts = defaultdict(int, {int(k): v for k, v in data.items()})
            return "✅ Appearance counts loaded!", format_counts_for_table(appearance_counts), None, None, None
    except Exception as e:
        return f"❌ Error loading file: {str(e)}", format_counts_for_table(appearance_counts), None, None, None

def update_params(status, counts, n=None, k=None, start=None):
    outputs = [status, counts]
    if n is not None:
        outputs.append(n)
    if k is not None:
        outputs.append(k)
    if start is not None:
        outputs.append(start)
    return outputs

# === Gradio UI ===
with gr.Blocks(theme=gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
    neutral_hue="slate",
    radius_size=gr.themes.sizes.radius_md,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
)) as demo:
    # Banner and title
    gr.Markdown("""
    <div style="text-align: center; margin-bottom: 1rem">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem">🎲 Fair Batch Generator</h1>
        <p style="font-size: 1.1rem; margin: 0; color: var(--body-text-color-subdued)">
            Generate batches of numbers with balanced frequency distribution
        </p>
        <hr style="margin: 1.5rem 0; border-color: var(--border-color-primary)">
    </div>
    """)
    
    # Add custom CSS for styling
    gr.Markdown("""
    <style>
    #counts-table .table-container {
        max-height: 500px;
        overflow-y: auto;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .header-box {
        background: linear-gradient(to right, var(--background-fill-primary), var(--background-fill-secondary));
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .header-box h3 {
        margin: 0;
        font-weight: 600;
    }
    
    .action-button {
        transition: transform 0.2s;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
    }
    
    .result-area {
        background-color: var(--background-fill-secondary);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    </style>
    """)
    
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            # Input Controls
            with gr.Group():
                # Configuration header in a styled box
                gr.Markdown('<div class="header-box"><h3>⚙️ Configuration</h3></div>')
                
                with gr.Column(variant="panel"):
                    n_input = gr.Number(value=10, label="Range Size (N)", precision=0, minimum=1)
                    k_input = gr.Number(value=3, label="Batch Size (k)", precision=0, minimum=1)
                    start_input = gr.Number(value=1, label="Range Start (inclusive)", precision=0)
                    
                    with gr.Row():
                        generate_btn = gr.Button("🔁 Generate Batch", variant="primary", size="lg", elem_classes=["action-button"])
                        reset_btn = gr.Button("♻️ Reset", variant="secondary", size="lg", elem_classes=["action-button"])
                    
                    clean_btn = gr.Button("🧹 Clean Counts to Match Current Range", variant="secondary", elem_classes=["action-button"])

            # Save/Load Controls
            with gr.Group():
                # Save/Load header in a styled box
                gr.Markdown('<div class="header-box"><h3>💾 Save/Load</h3></div>')
                
                with gr.Column(variant="panel"):
                    # Save
                    gr.Markdown("#### Save Data")
                    with gr.Row():
                        with gr.Column():
                            save_counts_btn = gr.Button("📥 Save Counts Only", variant="secondary", elem_classes=["action-button"])
                            save_counts_file = gr.File(label="Download Counts", interactive=False, type="filepath")
                        
                        with gr.Column():
                            save_full_btn = gr.Button("📦 Save Full Config", variant="secondary", elem_classes=["action-button"])
                            save_full_file = gr.File(label="Download Full Config", interactive=False, type="filepath")
                    
                    # Load
                    gr.Markdown("#### Load Data")
                    with gr.Tabs(selected=0):
                        with gr.Tab("Upload File"):
                            upload_file = gr.File(label="Upload JSON File")
                            upload_btn = gr.Button("Load File", variant="secondary", elem_classes=["action-button"])
                        
                        with gr.Tab("Paste JSON"):
                            counts_json_input = gr.Textbox(label="Paste Counts JSON", lines=4)
                            load_counts_btn = gr.Button("Load Counts Only", variant="secondary", elem_classes=["action-button"])
                            
                            full_json_input = gr.Textbox(label="Paste Full Config JSON", lines=4)
                            load_full_btn = gr.Button("Load Full Configuration", variant="secondary", elem_classes=["action-button"])

        with gr.Column(scale=2):
            # Output Area
            with gr.Group():
                # Results header in a styled box
                gr.Markdown('<div class="header-box"><h3>🎯 Results</h3></div>')
                
                with gr.Column(variant="panel", elem_classes=["result-area"]):
                    batch_output = gr.Textbox(label="Generated Batch / Messages", show_label=False, lines=4)
                
                gr.Markdown('<div class="header-box"><h3>📊 Appearance Counts</h3></div>')
                with gr.Column(variant="panel"):
                    count_output = gr.Dataframe(
                        headers=["Item", "Count"],
                        label="Count Table",
                        wrap=True,
                        elem_id="counts-table"
                    )

    # Hook up buttons
    generate_btn.click(
        fn=generate_fair_batch,
        inputs=[n_input, k_input, start_input],
        outputs=[batch_output, count_output]
    )

    reset_btn.click(
        fn=reset_progress,
        inputs=[],
        outputs=[batch_output, count_output, n_input, k_input, start_input]
    )

    clean_btn.click(
        fn=clean_counts_to_current_range,
        inputs=[],
        outputs=[batch_output, count_output]
    )

    # Save functions
    save_counts_btn.click(
        fn=save_counts_only,
        inputs=[],
        outputs=[save_counts_file]
    )

    save_full_btn.click(
        fn=save_full_progress,
        inputs=[],
        outputs=[save_full_file]
    )

    # Load from file
    upload_btn.click(
        fn=load_from_file,
        inputs=[upload_file],
        outputs=[batch_output, count_output, n_input, k_input, start_input]
    ).then(
        fn=update_params,
        inputs=[batch_output, count_output, n_input, k_input, start_input],
        outputs=[batch_output, count_output, n_input, k_input, start_input]
    )

    # Load from text inputs
    load_counts_btn.click(
        fn=load_counts_from_text,
        inputs=[counts_json_input],
        outputs=[batch_output, count_output]
    )

    load_full_btn.click(
        fn=load_full_from_text,
        inputs=[full_json_input],
        outputs=[batch_output, count_output, n_input, k_input, start_input]
    )

    # Add footer
    gr.Markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; border-top: 1px solid var(--border-color-primary)">
        <p style="color: var(--body-text-color-subdued); font-size: 0.9rem;">
            🎲 Fair Batch Generator | <a href="https://github.com/xga0/fair-batch-app" target="_blank">GitHub</a> | <a href="https://huggingface.co/spaces/xga0/fair-batch-app" target="_blank">Hugging Face Spaces</a>
        </p>
        <p style="color: var(--body-text-color-subdued); font-size: 0.8rem;">
            Created with Gradio 5.23.2 | MIT License
        </p>
    </div>
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=True)
