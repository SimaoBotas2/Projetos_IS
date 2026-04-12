import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd


# Read the markdown file and parse both VMs and Containers sections
def read_markdown_table(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by section headers
    vm_section = content.split('VMs Andre')[1].split('Container Andre')[0]
    container_section = content.split('Container Andre')[1]
    
    dfs = []
    
    for section, type_label in [(vm_section, 'VM'), (container_section, 'Container')]:
        # Extract table rows (lines starting with |)
        lines = [line for line in section.split('\n') if line.startswith('|')]
        # Skip header and separator rows
        lines = [line for line in lines[2:] if line.strip() != '']
        
        rows = []
        for line in lines:
            # Split by | and clean up
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and cells[0] != '---':
                rows.append(cells)
        
        if rows:
            df_temp = pd.DataFrame(rows, columns=['Records', 'Format', 'Operation', 'Size (bytes)', 'Time (s)', 'Throughput (bytes/sec)', 'Memory Used (MB)'])
            df_temp['Type'] = type_label
            dfs.append(df_temp)
    
    df = pd.concat(dfs, ignore_index=True)
    
    # Convert numeric columns
    numeric_cols = ['Size (bytes)', 'Time (s)', 'Throughput (bytes/sec)', 'Memory Used (MB)']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
    
    return df

df = read_markdown_table('Results_table.md')
vms = df[df['Type'] == 'VM']
containers = df[df['Type'] == 'Container']

# Compare metrics
print("=== VMS vs CONTAINERS ===\n")
for col in df.select_dtypes(include=['float64', 'int64']).columns:
    print(f"{col}:")
    print(f"  VMs - Mean: {vms[col].mean():.2f}, Std: {vms[col].std():.2f}")
    print(f"  Containers - Mean: {containers[col].mean():.2f}, Std: {containers[col].std():.2f}\n")

# Generate output.md with percentage differences
with open('output.md', 'w', encoding='utf-8') as f:
    f.write("# Diferenças Percentuais: Containers vs VMs\n\n")
    f.write("Percentual de diferença calculado como: `((Container - VM) / VM) * 100`\n\n")
    
    formats = df['Format'].unique()
    numeric_cols = ['Size (bytes)', 'Time (s)', 'Throughput (bytes/sec)', 'Memory Used (MB)']
    
    for fmt in formats:
        f.write(f"## {fmt}\n\n")
        
        records_list = sorted(df[df['Format'] == fmt]['Records'].unique())
        
        for record in records_list:
            f.write(f"### {record} Registos\n\n")
            
            for operation in ['Serialization', 'Deserialization']:
                f.write(f"#### {operation}\n\n")
                f.write("| Métrica | VM | Container | Diferença % |\n")
                f.write("|---------|----|-----------|-----------|\n")
                
                df_vm = df[(df['Type'] == 'VM') & (df['Format'] == fmt) & 
                          (df['Records'] == record) & (df['Operation'] == operation)]
                df_container = df[(df['Type'] == 'Container') & (df['Format'] == fmt) & 
                                 (df['Records'] == record) & (df['Operation'] == operation)]
                
                for col in numeric_cols:
                    if not df_vm.empty and not df_container.empty:
                        vm_val = df_vm[col].values[0]
                        container_val = df_container[col].values[0]
                        
                        if vm_val != 0:
                            pct_diff = ((container_val - vm_val) / vm_val) * 100
                            f.write(f"| {col} | {vm_val:.2f} | {container_val:.2f} | {pct_diff:+.2f}% |\n")
                
                f.write("\n")
    
    # Overall statistics
    f.write("## Resumo Geral\n\n")
    f.write("| Métrica | VM Média | Container Média | Diferença % |\n")
    f.write("|---------|----------|-----------------|----------|\n")
    
    for col in numeric_cols:
        vm_mean = vms[col].mean()
        container_mean = containers[col].mean()
        
        if vm_mean != 0:
            pct_diff = ((container_mean - vm_mean) / vm_mean) * 100
            f.write(f"| {col} | {vm_mean:.2f} | {container_mean:.2f} | {pct_diff:+.2f}% |\n")
    
    # Overall statistics by operation
    f.write("\n## Resumo Geral por Operação\n\n")
    for operation in ['Serialization', 'Deserialization']:
        f.write(f"### {operation}\n\n")
        f.write("| Métrica | VM Média | Container Média | Diferença % |\n")
        f.write("|---------|----------|-----------------|----------|\n")
        
        vms_op = vms[vms['Operation'] == operation]
        containers_op = containers[containers['Operation'] == operation]
        
        for col in numeric_cols:
            vm_mean = vms_op[col].mean()
            container_mean = containers_op[col].mean()
            
            if vm_mean != 0:
                pct_diff = ((container_mean - vm_mean) / vm_mean) * 100
                f.write(f"| {col} | {vm_mean:.2f} | {container_mean:.2f} | {pct_diff:+.2f}% |\n")
        
        f.write("\n")

print("\n[+] Ficheiro output.md criado com sucesso!")


# Create comparison box plots
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
col_counter = 1
for col in numeric_cols:
    plt.figure()
    plt.boxplot([vms[col], containers[col]], tick_labels=['VMs', 'Containers'])
    plt.ylabel(col)
    plt.title(f'Comparison: {col}')
    # Sanitize filename by removing special characters
    safe_filename = col.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
    plt.savefig(f'comparison_{col_counter}_{safe_filename}.png')
    plt.close()
    col_counter += 1

# Create bar plots by file format with VM and Container comparison
formats = df['Format'].unique()
numeric_cols = ['Size (bytes)', 'Time (s)', 'Throughput (bytes/sec)', 'Memory Used (MB)']

for fmt in formats:
    df_fmt = df[df['Format'] == fmt]
    
    for col in numeric_cols:
        plt.figure(figsize=(14, 6))
        
        # Create labels combining Records and Operation
        records_unique = sorted(df_fmt['Records'].unique())
        x_labels = []
        vm_values = []
        container_values = []
        
        bar_width = 0.35
        x_positions = []
        pos = 0
        
        for record in records_unique:
            for operation in ['Serialization', 'Deserialization']:
                # Get VM data
                df_vm = df_fmt[(df_fmt['Records'] == record) & (df_fmt['Operation'] == operation) & (df_fmt['Type'] == 'VM')]
                # Get Container data
                df_container = df_fmt[(df_fmt['Records'] == record) & (df_fmt['Operation'] == operation) & (df_fmt['Type'] == 'Container')]
                
                if not df_vm.empty:
                    vm_values.append(df_vm[col].values[0])
                else:
                    vm_values.append(0)
                
                if not df_container.empty:
                    container_values.append(df_container[col].values[0])
                else:
                    container_values.append(0)
                
                x_labels.append(f"{record}\n{operation}")
                x_positions.append(pos)
                pos += 1
        
        # Create bar plot with side-by-side bars
        x_pos = range(len(x_labels))
        bars1 = plt.bar([x - bar_width/2 for x in x_pos], vm_values, bar_width, label='VM', color='#1f77b4')
        bars2 = plt.bar([x + bar_width/2 for x in x_pos], container_values, bar_width, label='Container', color='#ff7f0e')
        
        plt.xticks(x_pos, x_labels, fontsize=9)
        plt.ylabel(col, fontsize=11)
        plt.title(f'{fmt} - {col}', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.legend(loc='upper left', fontsize=10)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.0f}', ha='center', va='bottom', fontsize=7)
        
        # Sanitize filename
        safe_col = col.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
        plt.tight_layout()
        plt.savefig(f'barplot_{fmt}_{safe_col}.png', dpi=100)
        plt.close()