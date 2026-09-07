from rag.generator import generate_answer


context = """
FIRST NATIONAL CORPORATION

Results of Operations

2025
Interest and dividend income: $99,497 thousand
Interest expense: $26,251 thousand
Net interest income: $73,246 thousand

2024
Net interest income: $52,452 thousand
"""


question = "What was the net interest income in 2025?"

answer = generate_answer(question, context)

print("\nQuestion:")
print(question)

print("\nGenerated Answer:")
print(answer)