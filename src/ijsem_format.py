import pandas as pd
import sys
import os

def generate_ijsem_table(input_file, output_file=None):
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    try:
        df = pd.read_csv(input_file, sep='\t', index_col=0)
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Transpose so samples are columns and traits are rows
    df = df.T
    
    # Define a helper function to convert numeric to sign
    def to_sign(val):
        return '+' if float(val) > 0 else '-'

    # Apply sign conversion to everything first
    # Use map for pandas >= 2.1.0, otherwise applymap
    if hasattr(df, 'map'):
        signed_df = df.map(to_sign)
    else:
        signed_df = df.applymap(to_sign)
    
    # Identify variability based on SIGNS
    is_variable = signed_df.nunique(axis=1) > 1
    variable_traits = signed_df[is_variable].sort_index()
    invariant_traits = signed_df[~is_variable]
    
    # Group invariants
    pos_invariant = invariant_traits[invariant_traits.iloc[:, 0] == '+'].index.tolist()
    neg_invariant = invariant_traits[invariant_traits.iloc[:, 0] == '-'].index.tolist()
    
    pos_invariant.sort()
    neg_invariant.sort()
    
    # Generate Markdown Content
    lines = []
    lines.append("### Predicted phenotypes of samples\n")
    
    if not variable_traits.empty:
        header = "| Characteristic | " + " | ".join(variable_traits.columns) + " |"
        sep = "| :--- | " + " | ".join([":---:"] * len(variable_traits.columns)) + " |"
        lines.append(header)
        lines.append(sep)
        
        for trait, row in variable_traits.iterrows():
            lines.append(f"| {trait} | " + " | ".join(row.values) + " |")
    else:
        lines.append("*No variable traits found among the samples.*\n")
        
    lines.append("\n---\n")
    
    if pos_invariant:
        lines.append(f"**Positive results were found for:** {', '.join(pos_invariant)}.\n")
    else:
        lines.append("**Positive results were found for:** none.\n")
        
    lines.append("")
    
    if neg_invariant:
        lines.append(f"**Negative results were found for:** {', '.join(neg_invariant)}.\n")
    else:
        lines.append("**Negative results were found for:** none.\n")

    markdown_content = "\n".join(lines)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"--> IJSEM-style table generated at: {output_file}")
    else:
        print(markdown_content)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate IJSEM-style Markdown table from Traitar2 predictions")
    parser.add_argument("input", help="Path to predictions_majority-vote_combined.txt")
    parser.add_argument("-o", "--output", help="Path to save the Markdown file")
    args = parser.parse_args()
    generate_ijsem_table(args.input, args.output)
