import re

# 1. Open your current TTL file
input_filename = "bhagavad_gita.ttl"
output_filename = "bhagavad_gita_fixed.ttl"

print("Repairing file... please wait.")

with open(input_filename, "r", encoding="utf-8") as f:
    content = f.read()

# FIX 1: Change the Property Definition at the top
# Changes range from xsd:int to xsd:string so it accepts "16-18"
content = content.replace(
    ":hasVerseNumber rdf:type owl:DatatypeProperty ;\n    rdfs:domain [ rdf:type owl:Restriction ;\n        owl:onProperty owl:topObjectProperty ;\n        owl:someValuesFrom :Verse\n    ] ;\n    rdfs:range xsd:int .",
    ":hasVerseNumber rdf:type owl:DatatypeProperty ;\n    rdfs:domain [ rdf:type owl:Restriction ;\n        owl:onProperty owl:topObjectProperty ;\n        owl:someValuesFrom :Verse\n    ] ;\n    rdfs:range xsd:string ."
)

# FIX 2: Automagically find all hyphenated numbers (like "16-18") that are marked as integer
# and change them to string.
# Pattern: looks for "12-34"^^xsd:integer
pattern = r'("[0-9]+-[0-9]+")\^\^xsd:integer'
# Replace with: "12-34"^^xsd:string
fixed_content = re.sub(pattern, r'\1^^xsd:string', content)

# FIX 3: Also fix the specific lines you showed in the log if they vary slightly
fixed_content = fixed_content.replace("^^xsd:int", "^^xsd:string")
fixed_content = fixed_content.replace("^^xsd:integer", "^^xsd:string")

# Save to a new file
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(fixed_content)

print(f"✅ Fixed! Created new file: {output_filename}")
print("You can now use this new file in your main script.")