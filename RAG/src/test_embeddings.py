"""
Test BGE-M3 for Malayalam semantic understanding
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import EMBEDDING_MODEL
print(f"Testing model: {EMBEDDING_MODEL}")

from chromadb.utils import embedding_functions

# Initialize BGE-M3
embed_func = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name=EMBEDDING_MODEL
)

# Malayalam semantic test
test_cases = [
    {
        "question": "ശിലായുഗത്തെ എങ്ങനെ തരം തിരിക്കാം?",
        "relevant": "ശിലായുഗം മനുഷ്യ ചരിത്രത്തിന്റെ ആദ്യകാല ഘട്ടമാണ്. പാലിയോലിത്തിക്, മെസോലിത്തിക്, നിയോലിത്തിക് എന്നീ മൂന്ന് ഘട്ടങ്ങളായി തരം തിരിക്കപ്പെടുന്നു.",
        "irrelevant": "കേരളത്തിലെ വ്യവസായ വികസനം പ്രധാനമാണ്. ഇന്ന് കേരളം വിവിധ വ്യവസായ മേഖലകളിൽ മുന്നിൽ നിൽക്കുന്നു."
    },
    {
        "question": "കമ്പ്യൂട്ടർ പ്രോഗ്രാമിംഗ് എന്താണ്?",
        "relevant": "കമ്പ്യൂട്ടർ പ്രോഗ്രാമിംഗ് എന്നത് കമ്പ്യൂട്ടറിന് നിർദ്ദേശങ്ങൾ നൽകുന്ന പ്രക്രിയയാണ്. പൈത്തൺ, ജാവ, സി++ എന്നിവ പ്രധാന പ്രോഗ്രാമിംഗ് ഭാഷകളാണ്.",
        "irrelevant": "മലയാളം ഒരു ദ്രാവിഡ ഭാഷയാണ്. ഇത് കേരളത്തിലെ ഔദ്യോഗിക ഭാഷയാണ്."
    }
]

print("\n🧪 Testing BGE-M3 Semantic Understanding in Malayalam")
print("="*60)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: '{test['question'][:30]}...'")
    
    # Get embeddings
    embeddings = embed_func([test['relevant'], test['irrelevant'], test['question']])
    relevant_emb = embeddings[0]
    irrelevant_emb = embeddings[1]
    question_emb = embeddings[2]
    
    # Calculate similarities
    def cosine_similarity(a, b):
        dot = sum(x*y for x, y in zip(a, b))
        norm_a = sum(x*x for x in a) ** 0.5
        norm_b = sum(y*y for y in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
    
    sim_relevant = cosine_similarity(question_emb, relevant_emb)
    sim_irrelevant = cosine_similarity(question_emb, irrelevant_emb)
    
    print(f"  Similarity with RELEVANT text:    {sim_relevant:.4f}")
    print(f"  Similarity with IRRELEVANT text:  {sim_irrelevant:.4f}")
    print(f"  Difference: {sim_relevant - sim_irrelevant:.4f}")
    
    # Evaluation
    if sim_relevant - sim_irrelevant > 0.3:
        print("  ✅ EXCELLENT: Can distinguish Malayalam semantics!")
    elif sim_relevant - sim_irrelevant > 0.1:
        print("  ⚠️  ACCEPTABLE: Some semantic understanding")
    else:
        print("  ❌ POOR: Cannot distinguish meaning")

print("\n" + "="*60)
print("📊 EXPECTED RESULTS WITH BGE-M3:")
print("• Relevant text similarity: >0.7")
print("• Irrelevant text similarity: <0.3")
print("• Difference: >0.4")
print("="*60)