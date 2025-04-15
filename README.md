# 🎲 Fair Batch Generator

An interactive [Gradio](https://gradio.app/) web app for generating **fair batches of integers** from a configurable range. This app ensures balanced usage over time, useful for sampling, experimentation, and fairness-based systems.

---

## 🚀 Features

✅ **Fair Sampling**  
Generates batches of `k` integers from a specified range such that all numbers appear with roughly equal frequency over time.

✅ **Configurable Parameters**  
You control:
- `N`: Range size (number of elements)
- `k`: Batch size
- `start`: Starting value of the range (inclusive)

✅ **Live Session State**  
Tracks how many times each number has been selected via an internal `appearance_counts` dictionary.

✅ **Two Types of Save/Load**  
- **Quick Save/Load**: Saves only the appearance count data  
- **Full Save/Load**: Saves counts **plus** your current input settings (`N`, `k`, `start`)

✅ **Mismatch Warnings**  
If you change `N`, `k`, or `start` after loading a save file, the app will warn you if the loaded data is no longer valid for the new range.

✅ **Clean Counts Feature**  
🧹 A one-click button to clean out-of-range entries in `appearance_counts` after modifying input parameters.

✅ **Interactive UI**  
Gradio-based interface with:
- Batch generator
- Real-time data table
- Upload/download buttons
- Input controls for easy experimentation

---

## 📁 File Structure

```
fair-batch-app/
├── app.py               # Main Gradio app
├── requirements.txt     # Dependency file
└── README.md            # This file
```

---

## 💻 Run Locally

1. Clone this repo:

```bash
git clone https://github.com/YOUR_USERNAME/fair-batch-app.git
cd fair-batch-app
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Launch the app:

```bash
python app.py
```

Open your browser to `http://localhost:7860`

---

## 🌐 Deploy to Hugging Face Spaces

1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Create a new **Gradio** Space
3. Choose **“From GitHub”** and link this repo
4. The app will be deployed automatically

---

## 🔬 Example Use Cases

- 🧠 Curriculum learning: ensure balanced exposure to all data points
- 🧪 Fair participant sampling for experiments
- 🎮 Fair rotation of players, maps, or assets in games
- 🗂️ Random selection with usage balancing

---

## 📘 How It Works

The batching logic operates as follows:

1. Track how often each number has been selected (`appearance_counts`)
2. In each batch:
   - Prefer numbers with the fewest appearances
   - Fill remaining slots randomly without repeating numbers
3. Update the appearance counts in real time
4. Validate saved state compatibility with current settings

---

## 🛡️ License

This project is open source under the [MIT License](LICENSE). Feel free to use, modify, or extend it!

---

## 🤝 Contributions

Pull requests are welcome! Feel free to submit bug fixes, new features, or improvements to documentation.

---

## 📬 Contact

Questions or ideas? File an issue or reach out via GitHub.