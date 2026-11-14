"""
==============================================================================
🧠 FB PAGE BM AUTOMATED - RESILIENT LLM FINE-TUNING SUITE
Target: Google Colab (Free T4 or L4 GPU) / Linux Server with GPU
Dual Engine: Unsloth (Speed Engine) + Hugging Face PEFT 4-Bit (Universal Fallback)
Model: Llama-3.2 (3B Instruct) or Qwen-2.5 (3B Instruct)
==============================================================================
Copy & paste this entire script into a single Google Colab cell and press Run.
==============================================================================
"""

import os
import sys
import subprocess
import importlib

print("======================================================================")
print("📦 [STEP 1] INSTALLING UNSLOTH, UNSLOTH_ZOO & HUGGING FACE DEPENDENCIES...")
print("======================================================================")

# Install packages with unsloth_zoo included
deps = [
    "unsloth",
    "unsloth_zoo",
    "peft",
    "bitsandbytes",
    "trl",
    "accelerate",
    "datasets",
    "transformers",
    "huggingface_hub"
]

print(f"Installing: {', '.join(deps)}...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + deps, check=False)
importlib.invalidate_caches()

import torch
from datasets import Dataset

has_gpu = torch.cuda.is_available()
gpu_name = torch.cuda.get_device_name(0) if has_gpu else "CPU"
print(f"✅ PyTorch: {torch.__version__} | GPU: {gpu_name}")

print("\n======================================================================")
print("🚀 [STEP 2] LOADING 4-BIT QUANTIZED MODEL...")
print("======================================================================")

max_seq_length = 2048
model_name = "unsloth/Llama-3.2-3B-Instruct-bnb-4bit"

# Dual Engine Auto-Detection
USE_UNSLOTH = False
try:
    from unsloth import FastLanguageModel
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
    USE_UNSLOTH = True
    print(f"✅ Loaded via Unsloth Engine: {model_name} (Ultra-Fast Mode)!")
except Exception as e:
    print(f"⚠️ Unsloth initialization bypass ({e}); using Universal Hugging Face PEFT 4-Bit Engine...")
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct" if "Llama" in model_name else "Qwen/Qwen2.5-3B-Instruct", trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    peft_config = LoraConfig(
        r=16,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)
    print(f"✅ Loaded via Universal Hugging Face PEFT Engine: {model_name}!")

print("\n======================================================================")
print("📊 [STEP 3] PREPARING TRAINING DATASET (KHMER & ENGLISH ADS)...")
print("======================================================================")

alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

training_samples = [
    {
        "instruction": "Create a high-converting Facebook Ad caption in Khmer with a powerful curiosity hook.",
        "input": "Product: Angkor Quant AI Trading Assistant. Target: Retail traders wanting to avoid liquidation.",
        "output": "🔥 កំពូលយុទ្ធសាស្ត្រ Quant Trading ជំនាន់ថ្មី 2026! 🚀\nតើអ្នកធ្លាប់ឆ្ងល់ទេ ហេតុអ្វីបានជា 90% នៃ Trader តែងតែបាត់បង់ដើមទុនក្នុងពេលទីផ្សារបោក?\nឈប់ដេញចាប់តម្លៃតាមអារម្មណ៍! ប្រព័ន្ធ Angkor Quant AI បំពាក់នូវ Breakeven Armor និង 360° Trap Clearance ការពារដើមទុន ១០០%។ 💡💎\n👉 ចុចទីនេះដើម្បីទទួលបានដំណោះស្រាយភ្លាមៗ!"
    },
    {
        "instruction": "Auto-respond to a customer comment inquiring about price on a Facebook Boosted Post.",
        "input": "Comment: តម្លៃប៉ុន្មានបង? ចង់ទិញ",
        "output": "សួស្តីបង! អរគុណសម្រាប់ការចាប់អារម្មណ៍ 🙏 ខ្ញុំបានផ្ញើព័ត៌មានលម្អិត តម្លៃ និងប្រូម៉ូសិនពិសេសជូនក្នុង Messenger Inbox រួចរាល់ហើយបាទ! សូមបងពិនិត្យមើលប្រអប់សារឥឡូវនេះបាន 📩✨"
    },
    {
        "instruction": "Generate a pain-point direct-response Facebook ad copy in English.",
        "input": "Product: E-commerce Automation Suite. Target: Store owners tired of burning ad budget.",
        "output": "⚠️ Still burning thousands on Facebook Ads with 0.8X ROAS? Stop throwing money at cold audiences!\nOur Autonomous AI pacer tests creative hooks with $5 test budgets, automatically scales winners to 4.5X ROAS, and kills losing ad sets before you lose a single dollar. 📈⚡\n👉 Click the link below to get your free 14-day case study!"
    },
    {
        "instruction": "Classify if this Facebook ad copy violates Meta Advertising Standards.",
        "input": "Copy: Get rich overnight! 100% guaranteed profit in 24 hours without any risk!",
        "output": "VIOLATION_DETECTED: Misleading Financial Claims & Guaranteed Profits Policy. Immediate account ban risk. Recommendation: Rephrase to focus on systematic backtesting and risk management."
    }
]

formatted_data = []
for s in training_samples * 150:  # 600 training pairs
    text = alpaca_prompt.format(s["instruction"], s["input"], s["output"]) + tokenizer.eos_token
    formatted_data.append({"text": text})

dataset = Dataset.from_list(formatted_data)
print(f"✅ Training dataset prepared: {len(dataset)} instruction pairs.")

print("\n======================================================================")
print("🏋️ [STEP 4] EXECUTING TRAINING (ESTIMATED: 5-8 MINS ON GPU)...")
print("======================================================================")

from trl import SFTTrainer
from transformers import TrainingArguments

# Auto-detect precision based on GPU architecture (NVIDIA L4/A100 use bf16, T4 uses fp16)
try:
    from unsloth import is_bfloat16_supported
    supports_bf16 = is_bfloat16_supported()
except Exception:
    supports_bf16 = torch.cuda.is_bf16_supported() if (has_gpu and hasattr(torch.cuda, "is_bf16_supported")) else False

use_fp16 = not supports_bf16
use_bf16 = supports_bf16
print(f"🎯 Precision Mode: bf16={use_bf16} | fp16={use_fp16} (Optimized for {gpu_name})")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=1,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=60,
        learning_rate=2e-4,
        fp16=use_fp16,
        bf16=use_bf16,
        logging_steps=10,
        optim="adamw_8bit" if has_gpu else "adamw_torch",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=42,
        output_dir="outputs",
    ),
)

trainer.train()
print("🎉 Model fine-tuning completed successfully!")

print("\n======================================================================")
print("🧪 [STEP 5] LIVE TEST GENERATION...")
print("======================================================================")

if USE_UNSLOTH:
    FastLanguageModel.for_inference(model)

test_prompt = alpaca_prompt.format(
    "Create a high-converting Facebook Ad caption in Khmer with a powerful curiosity hook.",
    "Product: Gold Trading Algorithm with 90% Win Rate",
    ""
)
inputs = tokenizer([test_prompt], return_tensors="pt").to("cuda" if has_gpu else "cpu")
outputs = model.generate(**inputs, max_new_tokens=150, use_cache=True)
print("\nGenerated Caption:")
print(tokenizer.batch_decode(outputs)[0])

print("\n======================================================================")
print("💾 [STEP 6] EXPORTING MODEL WEIGHTS...")
print("======================================================================")

output_dir = "fb_ad_llm_lora"
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"✅ LoRA weights exported to directory '{output_dir}'!")
print("======================================================================")
