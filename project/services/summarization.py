
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

print("Loading summarizer model (flan-t5-base)...")
MODEL_NAME = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
print("✓ Summarizer loaded")


def summarize_chunk(text):
    """Summarize a single chunk of text."""
    prompt = "summarize the following lecture section clearly:\n" + text
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=120,
        min_length=60,
        num_beams=4,
        repetition_penalty=2.0,
        no_repeat_ngram_size=3,
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def chunk_text(text, chunk_size=600):
    """Split text into word-count chunks."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


def summarize_long(text):
    """Hierarchical two-pass summarization for long transcripts."""
    print("Splitting transcript into chunks...")
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")

    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"  Summarizing chunk {i + 1}/{len(chunks)}...")
        chunk_summaries.append(summarize_chunk(chunk))

    combined = " ".join(chunk_summaries)
    print("Creating final summary...")
    return summarize_chunk(combined)
