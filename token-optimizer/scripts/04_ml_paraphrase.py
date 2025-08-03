#!/usr/bin/env python3
"""
Stage 4: ML-based Paraphrasing
Uses small models to paraphrase text more concisely
"""

import sys
import argparse
from pathlib import Path
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, AutoTokenizer
import warnings

warnings.filterwarnings("ignore")


class MLParaphraser:
    def __init__(self, model_name="t5-small", device=None):
        """Initialize with a small paraphrasing model"""
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Loading model {model_name} on {self.device}...", file=sys.stderr)

        if "t5" in model_name:
            self.model = T5ForConditionalGeneration.from_pretrained(model_name).to(self.device)
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
            self.model_type = "t5"
        else:
            # Fallback to T5 if model not recognized
            self.model = T5ForConditionalGeneration.from_pretrained("t5-small").to(self.device)
            self.tokenizer = T5Tokenizer.from_pretrained("t5-small")
            self.model_type = "t5"

        self.model.eval()

        # For token counting
        self.gpt_tokenizer = AutoTokenizer.from_pretrained("gpt2")

    def paraphrase_text(self, text, max_length_ratio=0.8, num_beams=4):
        """Paraphrase text to be more concise"""
        # Split into manageable chunks (T5 has input limit)
        max_chunk_length = 400
        chunks = self._split_text_into_chunks(text, max_chunk_length)

        paraphrased_chunks = []

        for chunk in chunks:
            if not chunk.strip():
                continue

            # Prepare input based on model type
            if self.model_type == "t5":
                # Task prefix for paraphrasing/summarization
                input_text = f"paraphrase: {chunk}"
            else:
                input_text = chunk

            # Tokenize
            inputs = self.tokenizer.encode(
                input_text, return_tensors="pt", max_length=512, truncation=True
            ).to(self.device)

            # Calculate target length
            input_length = len(self.tokenizer.encode(chunk))
            target_length = int(input_length * max_length_ratio)

            # Generate paraphrase
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=target_length,
                    min_length=int(target_length * 0.5),
                    num_beams=num_beams,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    length_penalty=0.8,  # Prefer shorter outputs
                    do_sample=False,
                )

            paraphrased = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # For T5, sometimes it returns the task prefix, remove it
            if paraphrased.startswith("paraphrase:"):
                paraphrased = paraphrased[len("paraphrase:") :].strip()

            paraphrased_chunks.append(paraphrased)

        return " ".join(paraphrased_chunks)

    def compress_with_llmlingua_fallback(self, text):
        """Try to use LLMLingua if available, otherwise use T5"""
        try:
            from llmlingua import PromptCompressor

            # Initialize LLMLingua compressor
            compressor = PromptCompressor(
                model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
                use_llmlingua2=True,
                device_map=self.device,
            )

            # Compress the text
            compressed = compressor.compress_prompt(
                text,
                instruction="",
                question="",
                target_token=int(len(text.split()) * 0.7),  # Target 70% of original
                condition_compare=True,
                condition_in_question="after",
                rank_method="longllmlingua",
                use_sentence_level_filter=True,
                context_budget="+100",
                dynamic_context_compression_ratio=0.4,
            )

            return compressed["compressed_prompt"]

        except ImportError:
            print("LLMLingua not available, using T5 paraphrasing...", file=sys.stderr)
            return self.paraphrase_text(text)
        except Exception as e:
            print(f"LLMLingua failed: {e}, using T5 paraphrasing...", file=sys.stderr)
            return self.paraphrase_text(text)

    def _split_text_into_chunks(self, text, max_length):
        """Split text into chunks at sentence boundaries"""
        sentences = (
            text.replace("! ", "!<SPLIT>")
            .replace("? ", "?<SPLIT>")
            .replace(". ", ".<SPLIT>")
            .split("<SPLIT>")
        )

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(self.tokenizer.encode(sentence))

            if current_length + sentence_length > max_length and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def get_compression_stats(self, original, compressed):
        """Calculate compression statistics"""
        orig_tokens = len(self.gpt_tokenizer.encode(original))
        comp_tokens = len(self.gpt_tokenizer.encode(compressed))

        return {
            "original_length": len(original),
            "compressed_length": len(compressed),
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "char_reduction": (1 - len(compressed) / len(original)) * 100,
            "token_reduction": (1 - comp_tokens / orig_tokens) * 100,
        }


def main():
    parser = argparse.ArgumentParser(description="ML-based text paraphraser for compression")
    parser.add_argument("input", nargs="?", help="Input file or - for stdin")
    parser.add_argument("-o", "--output", help="Output file or - for stdout")
    parser.add_argument(
        "-m", "--model", default="t5-small", help="Model to use (default: t5-small)"
    )
    parser.add_argument(
        "-r",
        "--ratio",
        type=float,
        default=0.8,
        help="Target length ratio (default: 0.8 = 80% of original)",
    )
    parser.add_argument(
        "-l", "--llmlingua", action="store_true", help="Try to use LLMLingua if available"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show compression statistics")

    args = parser.parse_args()

    # Read input
    if args.input and args.input != "-":
        with open(args.input, "r") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Initialize paraphraser
    paraphraser = MLParaphraser(model_name=args.model)

    # Process text
    if args.llmlingua:
        compressed_text = paraphraser.compress_with_llmlingua_fallback(text)
    else:
        compressed_text = paraphraser.paraphrase_text(text, max_length_ratio=args.ratio)

    # Write output
    if args.output and args.output != "-":
        with open(args.output, "w") as f:
            f.write(compressed_text)
    else:
        print(compressed_text)

    # Show statistics if verbose
    if args.verbose:
        stats = paraphraser.get_compression_stats(text, compressed_text)
        print("\n--- ML Compression Statistics ---", file=sys.stderr)
        print(
            f"Original: {stats['original_length']} chars, {stats['original_tokens']} tokens",
            file=sys.stderr,
        )
        print(
            f"Compressed: {stats['compressed_length']} chars, {stats['compressed_tokens']} tokens",
            file=sys.stderr,
        )
        print(f"Character reduction: {stats['char_reduction']:.1f}%", file=sys.stderr)
        print(f"Token reduction: {stats['token_reduction']:.1f}%", file=sys.stderr)


if __name__ == "__main__":
    main()
