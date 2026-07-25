#!/usr/bin/env python3
"""
FAITHH Grounding Fine-Tune — QLoRA Training Script v2

Fine-tunes a base LLM to follow grounding rules:
- Cite git log commits accurately
- Reference only files in the project structure
- Refuse to fabricate when context is missing
- Use RAG chunks faithfully

Supported base models:
  - unsloth/Meta-Llama-3.1-8B-Instruct  (8B, ~8GB VRAM)
  - unsloth/Qwen2.5-14B-Instruct        (14B, ~12GB VRAM)

Uses Unsloth for 2x speedup and 60% less VRAM on RTX 3090.

Usage:
    CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 TORCHDYNAMO_DISABLE=1 \
    python train.py [--base-model unsloth/Qwen2.5-14B-Instruct] \
                    [--data data/grounding_train_v2.jsonl] \
                    [--epochs 3] [--output output/qwen25-grounded]

Hardware: RTX 3090 (24GB VRAM) — fits 14B QLoRA comfortably.
"""

import argparse
import os
import sys

# Ensure we can import project modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(SCRIPT_DIR, "data", "grounding_train_v2.jsonl")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "output", "qwen25-grounded")


def main():
    parser = argparse.ArgumentParser(description="FAITHH Grounding QLoRA Training")
    parser.add_argument("--base-model", default="unsloth/Qwen2.5-14B-Instruct",
                        help="Base model from HuggingFace (Unsloth-optimized)")
    parser.add_argument("--data", default=DEFAULT_DATA, help="Training data JSONL")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--batch-size", type=int, default=1, help="Per-device batch size")
    parser.add_argument("--grad-accum", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--max-seq-len", type=int, default=4096, help="Max sequence length")
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora-alpha", type=int, default=16, help="LoRA alpha")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument("--ollama-name", default="",
                        help="Ollama model name (auto-generated if empty)")
    parser.add_argument("--export-gguf", action="store_true", default=True,
                        help="Export to GGUF for Ollama after training")
    parser.add_argument("--quant", default="q4_k_m", help="GGUF quantization level")
    parser.add_argument("--dry-run", action="store_true", help="Print config and exit")
    args = parser.parse_args()

    # Validate data exists
    if not os.path.exists(args.data):
        print(f"❌ Training data not found: {args.data}")
        print(f"   Run: python generate_training_data.py first")
        sys.exit(1)

    # Count examples
    with open(args.data) as f:
        n_examples = sum(1 for _ in f)

    config = {
        "base_model": args.base_model,
        "data": args.data,
        "n_examples": n_examples,
        "epochs": args.epochs,
        "lr": args.lr,
        "batch_size": args.batch_size,
        "grad_accum": args.grad_accum,
        "effective_batch": args.batch_size * args.grad_accum,
        "max_seq_len": args.max_seq_len,
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "output": args.output,
        "export_gguf": args.export_gguf,
        "quant": args.quant,
    }

    print("=" * 60)
    print("FAITHH Grounding Fine-Tune — QLoRA")
    print("=" * 60)
    for k, v in config.items():
        print(f"  {k:20s}: {v}")
    print("=" * 60)

    if args.dry_run:
        print("\n🏃 Dry run — exiting.")
        return

    # ============================================================
    # Step 1: Load model with Unsloth
    # ============================================================
    print("\n📦 Loading model with Unsloth...")
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.base_model,
        max_seq_length=args.max_seq_len,
        dtype=None,         # Auto-detect (bf16 on RTX 3090)
        load_in_4bit=True,  # QLoRA — 4-bit quantization
    )

    # ============================================================
    # Step 2: Add LoRA adapters
    # ============================================================
    print("🔧 Adding LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0,     # Optimized — 0 is faster
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        bias="none",
        use_gradient_checkpointing="unsloth",  # 30% less VRAM
        random_state=42,
    )

    # Print trainable params
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"   Trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # ============================================================
    # Step 3: Load and format training data
    # ============================================================
    print(f"\n📊 Loading training data from {args.data}...")
    from datasets import load_dataset
    from unsloth.chat_templates import get_chat_template, standardize_sharegpt

    # Auto-detect chat template from model name
    model_lower = args.base_model.lower()
    if "qwen" in model_lower:
        chat_tmpl = "qwen-2.5"
    elif "llama" in model_lower:
        chat_tmpl = "llama-3.1"
    else:
        chat_tmpl = "chatml"  # safe default
    print(f"   Chat template: {chat_tmpl}")
    tokenizer = get_chat_template(tokenizer, chat_template=chat_tmpl)

    dataset = load_dataset("json", data_files=args.data, split="train")
    dataset = standardize_sharegpt(dataset)

    def formatting_prompts_func(examples):
        texts = []
        for convo in examples["conversations"]:
            text = tokenizer.apply_chat_template(
                convo, tokenize=False, add_generation_prompt=False
            )
            texts.append(text)
        return {"text": texts}

    dataset = dataset.map(formatting_prompts_func, batched=True)
    print(f"   Loaded {len(dataset)} examples")

    # ============================================================
    # Step 4: Train
    # ============================================================
    print(f"\n🚀 Training for {args.epochs} epochs...")
    from trl import SFTTrainer
    from transformers import TrainingArguments

    os.makedirs(args.output, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=args.max_seq_len,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=args.batch_size,
            gradient_accumulation_steps=args.grad_accum,
            warmup_steps=5,
            num_train_epochs=args.epochs,
            learning_rate=args.lr,
            fp16=False,
            bf16=True,   # RTX 3090 supports bf16
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=42,
            output_dir=args.output,
            report_to="none",
        ),
    )

    # Train
    stats = trainer.train()
    print(f"\n✅ Training complete!")
    print(f"   Loss: {stats.training_loss:.4f}")
    print(f"   Runtime: {stats.metrics.get('train_runtime', 0):.0f}s")

    # Save LoRA adapter
    adapter_path = os.path.join(args.output, "lora_adapter")
    model.save_pretrained(adapter_path)
    tokenizer.save_pretrained(adapter_path)
    print(f"   LoRA adapter saved to {adapter_path}")

    # ============================================================
    # Step 5: Export to GGUF (for Ollama)
    # ============================================================
    if args.export_gguf:
        print(f"\n📦 Exporting to GGUF ({args.quant})...")
        gguf_path = os.path.join(args.output, "gguf")

        model.save_pretrained_gguf(
            gguf_path,
            tokenizer,
            quantization_method=args.quant,
        )
        print(f"   GGUF saved to {gguf_path}")

        # Create Ollama Modelfile
        modelfile_path = os.path.join(args.output, "Modelfile")
        gguf_file = None
        for f in os.listdir(gguf_path):
            if f.endswith(".gguf"):
                gguf_file = os.path.join(gguf_path, f)
                break

        if gguf_file:
            with open(modelfile_path, "w") as f:
                f.write(f'FROM {gguf_file}\n')
                f.write('PARAMETER temperature 0.7\n')
                f.write('PARAMETER top_p 0.9\n')
                f.write('PARAMETER num_ctx 4096\n')
                f.write('SYSTEM """You are FAITHH (Friendly AI Teaching & Helping Hub), '
                        'Jonathan\'s personal AI assistant. Follow grounding rules strictly: '
                        'only cite files, commits, and facts that appear in your context. '
                        'If information is missing, say so honestly rather than fabricating."""\n')

            # Determine ollama name
            ollama_name = args.ollama_name
            if not ollama_name:
                if "qwen" in args.base_model.lower():
                    ollama_name = "qwen25-grounded"
                elif "llama" in args.base_model.lower():
                    ollama_name = "llama31-grounded"
                else:
                    ollama_name = "faithh-grounded"

            print(f"   Modelfile: {modelfile_path}")
            print(f"\n   To load into Ollama:")
            print(f"   ollama create {ollama_name} -f {modelfile_path}")

    print("\n🎉 Done! Fine-tuning complete.")


if __name__ == "__main__":
    main()
