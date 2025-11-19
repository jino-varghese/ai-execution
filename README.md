# Text-to-Image Model Training

This repository contains a comprehensive Jupyter notebook for training a text-to-image model using Hugging Face's Diffusers library.

## Overview

The notebook demonstrates how to fine-tune a Stable Diffusion model on a custom dataset to generate images from text descriptions.

## Features

- **Pre-trained Model**: Uses Stable Diffusion v1.5 as the base model
- **Small Dataset Training**: Optimized for training on limited datasets
- **Memory Efficient**: Includes gradient checkpointing and mixed precision training
- **Complete Pipeline**: From data loading to image generation
- **Visualization**: Includes training loss plots and generated image comparisons

## Requirements

The notebook automatically installs all required dependencies:

```bash
- diffusers
- transformers
- accelerate
- datasets
- torch
- torchvision
- xformers (optional)
- bitsandbytes (optional)
- wandb (optional)
- pillow
- matplotlib
```

## Hardware Requirements

- **Minimum**:
  - GPU: NVIDIA GPU with 8GB+ VRAM (e.g., RTX 2070, GTX 1080 Ti)
  - RAM: 16GB system RAM

- **Recommended**:
  - GPU: NVIDIA GPU with 16GB+ VRAM (e.g., RTX 3090, A100)
  - RAM: 32GB+ system RAM

- **CPU-only**: Possible but very slow (not recommended for training)

## Usage

### Quick Start

1. Open the notebook:
```bash
jupyter notebook train_text_to_image_model.ipynb
```

2. Run all cells sequentially

3. The notebook will:
   - Install dependencies
   - Load the Pokemon dataset (small example dataset)
   - Fine-tune the model for 10 epochs
   - Generate sample images
   - Save the trained model

### Customization

#### Using Your Own Dataset

Replace the dataset in the configuration cell:

```python
config = {
    "dataset_name": "your-dataset-name",  # Change this
    "max_train_samples": 100,  # Adjust sample size
    ...
}
```

Your dataset should have:
- An `image` column with PIL images
- A `text` column with text descriptions

#### Adjusting Training Parameters

Modify the config dictionary:

```python
config = {
    "batch_size": 1,           # Increase if you have more VRAM
    "num_epochs": 10,          # More epochs = better quality (usually)
    "learning_rate": 1e-5,     # Learning rate
    "resolution": 512,         # Image resolution (512 or 768)
    "max_train_samples": 100,  # Dataset size limit
    ...
}
```

## Notebook Structure

1. **Environment Setup** - Install dependencies and import libraries
2. **Configuration** - Set training parameters
3. **Dataset Preparation** - Load and preprocess data
4. **Model Setup** - Load pre-trained Stable Diffusion components
5. **Training Setup** - Configure optimizer and data loaders
6. **Training Loop** - Train the model
7. **Save Model** - Save the fine-tuned model
8. **Inference** - Generate images from text prompts
9. **Evaluation** - Compare with base model
10. **Interactive Generation** - Custom prompt generation

## Output

The notebook creates a `text-to-image-model/` directory containing:

- `checkpoint-epoch-X/` - Training checkpoints
- `final_model/` - Final UNet weights
- `pipeline/` - Complete Stable Diffusion pipeline
- `training_loss.png` - Training loss plot
- `generated_images.png` - Sample generated images
- `model_comparison.png` - Base vs fine-tuned comparison
- `generated_X.png` - Individual generated images

## Example Results

After training, you can generate images like:

```python
prompts = [
    "a cute pokemon with big eyes",
    "a fire type pokemon",
    "a water type pokemon swimming",
]

generated_images = generate_images(prompts)
```

## Tips for Better Results

1. **Dataset Quality**: Use high-quality images with accurate captions
2. **Dataset Size**: More data (500-1000+ images) typically yields better results
3. **Training Time**: Increase epochs for better quality (20-50 epochs)
4. **Learning Rate**: Start with 1e-5, adjust if needed
5. **Resolution**: Higher resolution (768) requires more VRAM but better quality
6. **Prompt Engineering**: Be specific and descriptive in your prompts

## Troubleshooting

### Out of Memory Error

- Reduce `batch_size` to 1
- Reduce `resolution` to 256 or 384
- Enable `gradient_accumulation_steps`
- Use xformers for memory-efficient attention

### Poor Quality Images

- Train for more epochs
- Use a larger, higher-quality dataset
- Adjust learning rate
- Check caption quality in dataset

### Slow Training

- Enable mixed precision (`fp16`)
- Use a GPU instead of CPU
- Reduce `num_inference_steps` during generation
- Enable xformers

## Advanced Usage

### Using LoRA for Efficient Training

For even more memory-efficient training, consider using LoRA (Low-Rank Adaptation):

```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["to_q", "to_v"],
    lora_dropout=0.1,
)
```

### Training on Custom Images

Create a folder structure:
```
my_dataset/
├── image1.jpg
├── image2.jpg
└── metadata.csv
```

metadata.csv:
```csv
file_name,text
image1.jpg,description of image 1
image2.jpg,description of image 2
```

Then load with:
```python
from datasets import load_dataset
dataset = load_dataset("imagefolder", data_dir="my_dataset")
```

## License

This code uses pre-trained Stable Diffusion models which have specific license terms. Please review:
- Stable Diffusion License: https://huggingface.co/runwayml/stable-diffusion-v1-5

## Resources

- [Diffusers Documentation](https://huggingface.co/docs/diffusers)
- [Stable Diffusion](https://stability.ai/stable-diffusion)
- [Hugging Face Datasets](https://huggingface.co/docs/datasets)

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Acknowledgments

- Hugging Face for the Diffusers library
- Stability AI for Stable Diffusion
- The open-source ML community
