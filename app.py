import random
import json
from collections import defaultdict
import gradio as gr

# === Internal State ===
appearance_counts = defaultdict(int)
session_config = {"N": 10, "k": 3, "start": 1}

# === Core Batch Logic ===
def format_counts_for_table(counts_dict):
    if not counts_dict:
        return []
    return [[k, v] for k, v in sorted(counts_dict.items())]

def generate_fair_batch(N, k=3, start=1):
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
    appearance_counts.clear()
    session_config.update({"N": 10, "k": 3, "start": 1})
    return "", [], 10, 3, 1

def clean_counts_to_current_range():
    valid_range = set(range(session_config["start"], session_config["start"] + session_config["N"]))
    to_delete = [k for k in appearance_counts if k not in valid_range]
    for k in to_delete:
        del appearance_counts[k]
    return "✅ Out-of-range counts removed.", format_counts_for_table(appearance_counts)

def save_counts_only():
    counts_json = json.dumps(dict(appearance_counts), indent=2)
    return counts_json

def load_counts_only(file):
    global appearance_counts
    contents = json.load(file)
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

def save_full_progress():
    full_data = {
        "appearance_counts": dict(appearance_counts),
        "N": session_config["N"],
        "k": session_config["k"],
        "start": session_config["start"]
    }
    return json.dumps(full_data, indent=2)

def load_full_progress(file):
    global appearance_counts
    contents = json.load(file)
    appearance_counts = defaultdict(int, {int(k): v for k, v in contents["appearance_counts"].items()})
    session_config.update({
        "N": contents["N"],
        "k": contents["k"],
        "start": contents["start"]
    })
    return "✅ Full progress restored.", format_counts_for_table(appearance_counts), contents["N"], contents["k"], contents["start"]

# === Gradio UI ===
with gr.Blocks() as demo:
    gr.Markdown("# 🎲 Fair Batch Generator")
    
    with gr.Row():
        n_input = gr.Number(value=10, label="Range Size (N)", precision=0)
        k_input = gr.Number(value=3, label="Batch Size (k)", precision=0)
        start_input = gr.Number(value=1, label="Range Start (inclusive)", precision=0)

    with gr.Row():
        generate_btn = gr.Button("🔁 Generate Batch")
        reset_btn = gr.Button("♻️ Reset Progress")

    batch_output = gr.Textbox(label="Generated Batch / Messages")
    
    with gr.Row():
        count_output = gr.Dataframe(
            headers=["Item", "Count"],
            label="Appearance Count Table",
            height=400,  # Fixed height in pixels
            wrap=True    # Enable text wrapping
        )

    with gr.Row():
        save_counts_btn = gr.Button("💾 Download Appearance Counts (Quick Save)")
        save_full_btn = gr.Button("📦 Download Full Progress")
        counts_download = gr.File(label="Download JSON", interactive=False)
        full_download = gr.File(label="Download JSON", interactive=False)
    
    with gr.Row():
        load_counts_file = gr.File(label="📂 Upload Appearance Counts (Quick Load)", file_types=[".json"])
        load_full_file = gr.File(label="📦 Upload Full Progress", file_types=[".json"])

    clean_btn = gr.Button("🧹 Clean Counts to Match Current Range")

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

    save_counts_btn.click(
        fn=save_counts_only,
        inputs=[],
        outputs=[counts_download]
    )

    save_full_btn.click(
        fn=save_full_progress,
        inputs=[],
        outputs=[full_download]
    )

    load_counts_file.upload(
        fn=load_counts_only,
        inputs=[load_counts_file],
        outputs=[batch_output, count_output]
    )

    load_full_file.upload(
        fn=load_full_progress,
        inputs=[load_full_file],
        outputs=[batch_output, count_output, n_input, k_input, start_input]
    )

demo.launch()
