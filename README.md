---
title: Fair Batch App
emoji: 🎲
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.23.2"
app_file: app.py
pinned: false
---

# 🎲 Fair Batch Generator

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Gradio Demo](https://img.shields.io/badge/gradio-demo-orange.svg)](https://huggingface.co/spaces/xga0/fair-batch-app)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

> Try it now: [**Live Demo on Hugging Face**](https://huggingface.co/spaces/xga0/fair-batch-app)

A Gradio web application that generates fair batches from a range of numbers, ensuring each number appears a roughly equal number of times across multiple batch generations.

## 📋 Overview

### What is Fair Sampling & Why It Matters

Traditional random sampling tends to create imbalances — some elements appear frequently while others rarely show up, especially in small batches. **Fair sampling** solves this problem by:

1. **Tracking appearances**: Keeping count of how often each number has been chosen
2. **Prioritizing under-represented elements**: Preferentially selecting numbers that have appeared less frequently
3. **Balancing representation**: Ensuring all numbers have roughly equal representation over time

This matters in many real-world scenarios:
- **Machine Learning**: Preventing bias in training data selection
- **User Testing**: Ensuring all test cases receive equal attention
- **Resource Allocation**: Fairly distributing limited resources across multiple targets

### Simple Example

Imagine you have numbers 1-5 and want to generate batches of size 2:

```
Initial state: Each number has appeared 0 times
[1, 2, 3, 4, 5] → counts: [0, 0, 0, 0, 0]

Batch 1: [1, 2]
[1, 2, 3, 4, 5] → counts: [1, 1, 0, 0, 0]

Batch 2: [3, 4] (chosen because they have the lowest counts)
[1, 2, 3, 4, 5] → counts: [1, 1, 1, 1, 0]

Batch 3: [5, 1] (5 has lowest count; 1 randomly chosen from equal counts)
[1, 2, 3, 4, 5] → counts: [2, 1, 1, 1, 1]

Batch 4: [2, 3] (2, 3, 4, 5 all tied for lowest count)
[1, 2, 3, 4, 5] → counts: [2, 2, 2, 1, 1]
```

Over time, the appearance counts will remain balanced, unlike pure random selection.

## 🚀 Features

### Core Functionality
- **Fair Batch Generation**: Produces batches that prioritize numbers with the lowest appearance count
- **Customizable Parameters**: Configure range size (N), batch size (k), and starting value
- **Appearance Tracking**: Maintains counts of how often each number has been selected
- **Persistent State**: Save and load your progress using the built-in tools

### Technical Details
- **Two Save Options**:
  - **Quick Save**: Exports only the appearance count data
  - **Full Save**: Exports counts plus your current settings (N, k, start)
- **Data Validation**: Warns when loaded data doesn't match current range parameters
- **Maintenance Tools**: Clean out-of-range entries from appearance counts after parameter changes
- **Visual Analysis**: View and sort appearance counts in an interactive data table

### Example Use Cases
- 🧠 **Curriculum learning**: Ensure each training example is seen roughly the same number of times
- 🧪 **Experimental design**: Fairly distribute treatments or conditions among test subjects
- 🎮 **Game development**: Ensure players experience all levels/scenarios with balanced frequency
- 🎯 **A/B testing**: Distribute users evenly across different test variations
- 📊 **Survey sampling**: Select respondents from different demographics in a balanced way
- 🎲 **Board games**: Implement fair card/tile drawing systems that prevent unlucky streaks

## 🔍 How It Works

### Core Algorithm
1. Find the minimum appearance count across all numbers in the range
2. Identify all numbers that have this minimum count
3. Randomly shuffle this subset of numbers
4. Fill the batch with these minimally-represented numbers
5. If more numbers are needed, randomly select from remaining numbers
6. Update the appearance counts for the selected batch

This approach ensures that, over time, all numbers in the range appear approximately the same number of times, creating a balanced distribution that pure randomization cannot guarantee.

## 🖥️ Usage Guide

### Getting Started
1. Set your desired range size (N), batch size (k), and starting value
2. Click "Generate Batch" to create a new batch of numbers
3. View the batch results and updated appearance counts
4. Save your progress at any time using the save options
5. Load previously saved progress to continue where you left off

### Installation

```bash
# Clone the repository
git clone https://github.com/xga0/fair-batch-app.git
cd fair-batch-app

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open your browser to `http://localhost:7860`

## 📦 Project Information

### Requirements
- Python 3.7+
- Gradio 5.23.2
- Numpy
- Pandas

### File Structure
```
fair-batch-app/
├── app.py               # Main Gradio app
├── requirements.txt     # Dependency file
└── README.md            # This file
```

### License
This project is open source under the [MIT License](LICENSE).

### Contributions
Pull requests are welcome! Feel free to submit bug fixes, new features, or improvements to documentation.

### Credit
Created with ❤️ using [Hugging Face Spaces](https://huggingface.co/spaces/xga0/fair-batch-app) and [Gradio](https://gradio.app/)

### Contact
Questions or ideas? File an issue or reach out via GitHub.