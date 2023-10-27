# 将文件内容读取为字符串
file_path = './samples/2201.00001v1.txt'  # 替换成你的文件路径

with open(file_path, 'r', encoding='utf-8') as file:
    file_contents = file.read()

contents = file_contents.split("\u000C")

text = contents[0]

print(contents[0])


print(u"\u000C")