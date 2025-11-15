"""
LLM Fine-tuning Module
Handles fine-tuning of language models on medical datasets.
"""

import os
import torch
from typing import Dict, List, Optional
import logging
from pathlib import Path
import json

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
from peft import (
    get_peft_model,
    LoraConfig,
    TaskType,
    prepare_model_for_kbit_training
)

logger = logging.getLogger(__name__)


class MedicalLLMFineTuner:
    """
    Fine-tunes large language models on medical datasets using parameter-efficient methods.
    """

    def __init__(self, config: Dict):
        """
        Initialize the fine-tuning module.

        Args:
            config: Fine-tuning configuration
        """
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Fine-tuner initialized on device: {self.device}")

    def load_base_model(self, model_name: Optional[str] = None):
        """
        Load the base language model for fine-tuning.

        Args:
            model_name: Name of the base model (from HuggingFace)
        """
        if model_name is None:
            model_name = self.config['fine_tuning']['base_model']

        logger.info(f"Loading base model: {model_name}")

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            # Set padding token if not already set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_8bit=True  # Use 8-bit quantization for efficiency
            )

            logger.info("Base model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading base model: {e}")
            raise

    def prepare_peft_model(self):
        """
        Prepare model for parameter-efficient fine-tuning using LoRA.
        """
        logger.info("Preparing model for PEFT (LoRA)")

        # Prepare model for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)

        # LoRA configuration
        lora_config = LoraConfig(
            r=16,  # LoRA rank
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],  # Target attention layers
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )

        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)

        # Print trainable parameters
        self.model.print_trainable_parameters()

        logger.info("PEFT model prepared")

    def load_training_data(self, data_path: str):
        """
        Load and prepare training dataset.

        Args:
            data_path: Path to training data (JSONL format)

        Returns:
            Processed dataset
        """
        logger.info(f"Loading training data from {data_path}")

        # Load dataset
        dataset = load_dataset('json', data_files=data_path)

        # Tokenize dataset
        def tokenize_function(examples):
            # Format: instruction + response
            texts = []
            for i in range(len(examples['instruction'])):
                text = f"### Instruction:\n{examples['instruction'][i]}\n\n### Response:\n{examples['response'][i]}"
                texts.append(text)

            return self.tokenizer(
                texts,
                padding="max_length",
                truncation=True,
                max_length=512
            )

        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset["train"].column_names
        )

        logger.info(f"Loaded {len(tokenized_dataset['train'])} training examples")

        return tokenized_dataset

    def fine_tune(
        self,
        train_dataset_path: str,
        output_dir: Optional[str] = None,
        val_dataset_path: Optional[str] = None
    ):
        """
        Fine-tune the model on medical data.

        Args:
            train_dataset_path: Path to training dataset
            output_dir: Directory to save fine-tuned model
            val_dataset_path: Optional path to validation dataset
        """
        if output_dir is None:
            output_dir = self.config['fine_tuning']['output_dir']

        logger.info("Starting fine-tuning process")

        # Load base model if not already loaded
        if self.model is None:
            self.load_base_model()
            self.prepare_peft_model()

        # Load training data
        train_dataset = self.load_training_data(train_dataset_path)

        # Load validation data if provided
        val_dataset = None
        if val_dataset_path:
            val_dataset = self.load_training_data(val_dataset_path)

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.config['fine_tuning']['epochs'],
            per_device_train_batch_size=self.config['fine_tuning']['batch_size'],
            gradient_accumulation_steps=4,
            learning_rate=self.config['fine_tuning']['learning_rate'],
            fp16=True,
            logging_steps=10,
            save_strategy="epoch",
            evaluation_strategy="epoch" if val_dataset else "no",
            warmup_steps=100,
            save_total_limit=3,
            load_best_model_at_end=True if val_dataset else False,
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset["train"],
            eval_dataset=val_dataset["train"] if val_dataset else None,
            data_collator=data_collator,
        )

        # Train
        logger.info("Training started...")
        trainer.train()

        # Save model
        logger.info(f"Saving fine-tuned model to {output_dir}")
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        logger.info("Fine-tuning complete!")

    def evaluate_model(self, test_dataset_path: str) -> Dict:
        """
        Evaluate the fine-tuned model.

        Args:
            test_dataset_path: Path to test dataset

        Returns:
            Evaluation metrics
        """
        logger.info("Evaluating model...")

        test_dataset = self.load_training_data(test_dataset_path)

        trainer = Trainer(
            model=self.model,
            tokenizer=self.tokenizer,
        )

        metrics = trainer.evaluate(test_dataset["train"])

        logger.info(f"Evaluation metrics: {metrics}")
        return metrics

    def generate_response(self, instruction: str, max_length: int = 512) -> str:
        """
        Generate response using the fine-tuned model.

        Args:
            instruction: Input instruction
            max_length: Maximum response length

        Returns:
            Generated response
        """
        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the response part
        response = response.split("### Response:\n")[-1]

        return response
