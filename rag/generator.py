import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"


def generate_answer(question: str, context: str) -> str:
    """
    Generate a concise answer grounded only in retrieved evidence.
    """

    prompt = f"""
You are an evidence-grounded document question-answering system.

Your task is to answer the QUESTION using ONLY the RETRIEVED EVIDENCE.

IMPORTANT INSTRUCTIONS:

1. Search all retrieved evidence carefully before answering.

2. If ANY retrieved evidence passage directly contains the answer,
   you MUST answer using that evidence.

3. One clear supporting evidence passage is sufficient.
   Do not require the answer to appear in multiple passages.

4. Ignore retrieved evidence that is unrelated to the question.

5. If the answer is explicitly stated in the evidence, answer directly
   without adding unsupported interpretation.

6. NUMERICAL FIDELITY:
   - Preserve the numerical meaning and value exactly as supported by
     the evidence, but normalize the representation to digits.
   - If a number is written in words in the evidence, convert only its
     representation to digits without changing its value.
   - Always represent numerical quantities using digits, not number words.
   - Example: evidence "sixty projects" must be output as "60 projects".
   - Use standard mathematical and financial symbols when appropriate.
   - Write "92%" instead of "92 percent".
   - Write "$362 million" instead of "362 million dollars".
   - Preserve exact units such as %, $, thousand, million, billion,
     years, dates, and other measurement units.

   - If the evidence contains a table-level, section-level,
     or nearby shared unit such as "in thousands",
     "in millions", "%", "$", or another measurement unit,
     apply that unit to the corresponding numerical value.

   - Do not omit a unit merely because it appears in a table
     heading, section heading, or another retrieved evidence
     passage rather than directly beside the numerical value.

   - If a table or section specifies a shared unit such as
     "in thousands" or "in millions", preserve that unit in
     the final answer for the corresponding value.

   - Preserve important qualifiers such as "approximately",
     "more than", "about", "nearly", "less than", and "at least".

   - Do not calculate, round, change the numerical value,
     approximate, or convert units unless the user explicitly asks.

7. COUNT AND LIST QUESTIONS:
   - For "how many" questions, return the quantity using digits and
     include the corresponding noun or noun phrase.
   - Example: write "60 projects", not "sixty projects" or only "60".
   - For list questions, return every requested item that is explicitly
     supported by the evidence.

8. Do not use outside knowledge.

9. Do not invent, infer, assume, or add information that is not
   supported by the retrieved evidence.

10. Preserve the meaning and important factual qualifiers of the
    supporting evidence.

11. If NONE of the retrieved evidence contains enough information
    to answer the question, respond exactly:
    "The answer cannot be determined from the provided document."

12. ANSWER STYLE:
    - Always answer in a complete, grammatically correct sentence.
    - Keep the answer concise, direct, and focused on the question.
    - Do not return only a bare number, percentage, currency value,
      noun phrase, or sentence fragment when a complete sentence
      can be given.
    - Include the subject, metric, or quantity being answered so that
      the response can be understood on its own.

13. Do not explain your reasoning and do not mention the retrieval process.

14. FINAL OUTPUT CHECK:
    Before producing the final answer, ensure that:
    - the answer is fully supported by the retrieved evidence;
    - the answer is written as a complete sentence;
    - numerical quantities use digits, not number words;
    - percentages use the "%" symbol;
    - financial and mathematical symbols are preserved;
    - relevant table-level, section-level, and nearby shared units
      are included when supported by the retrieved evidence;
    - important qualifiers are preserved;
    - no unsupported information has been added.

Examples of preferred output:

"As of June 30, 2025, GPRBA's grant portfolio consisted of 60 projects."

"Approximately 92% of the committed portfolio was in IDA countries."

"GPRBA had received $362 million in donor contributions as of June 30, 2025."

"The net interest margin in 2025 was 3.88%."

"First National Corporation's total interest and dividend income in 2025 was $99,497 thousand."

"The provision for credit losses in 2025 was $2,887 thousand."

RETRIEVED EVIDENCE
==================
{context}
==================

QUESTION:
{question}

ANSWER:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                # Deterministic generation is preferred for factual document QA.
                "temperature": 0.0
            }
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    return result["response"].strip()