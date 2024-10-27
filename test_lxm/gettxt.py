def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line.strip().endswith('\t是'):
                parts = line.split('\t')
                if len(parts) > 1:
                    first_part = parts[0]
                    outfile.write(first_part + '\n')

# 使用方法示例：
input_filename = 'output_zh_50.txt'  # 输入文件名
output_filename = 'output_yes.txt'  # 输出文件名
process_file(input_filename, output_filename)