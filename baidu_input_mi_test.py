import os

class WordLibrary:
    def __init__(self, word, rank):
        self.word = word
        self.rank = rank


class WordLibraryList(list):
    pass


class BaiduShoujiEng:
    def export_line(self, wl):
        return f"{wl.word}\t{wl.rank - 54999}"  # 词频减去54999

    def export(self, wl_list):
        output_lines = []
        for wl in wl_list:
            output_lines.append(self.export_line(wl))
        return output_lines

    def import_line(self, line):
        wp = line.strip().split('\t')
        if len(wp) != 2:
            return None  # 确保格式正确
        word = wp[0]
        rank = int(wp[1])
        wl = WordLibrary(word, rank)
        return WordLibraryList([wl])

    def import_from_file(self, input_file):
        wl_list = WordLibraryList()
        with open(input_file, 'r', encoding='utf-8') as file:
            for line in file:
                imported = self.import_line(line)
                if imported:
                    wl_list.extend(imported)
        return wl_list

    def export_to_file(self, wl_list, output_file):
        with open(output_file, 'w', encoding='utf-8') as file:
            for line in self.export(wl_list):
                file.write(line + '\n')


# 示例用法
if __name__ == "__main__":
    input_file = input("请输入输入文件的完整路径：")
    
    # 获取输入文件的目录和文件名
    input_dir = os.path.dirname(input_file)
    input_name = os.path.basename(input_file)
    output_name = os.path.splitext(input_name)[0] + "_output.txt"  # 添加后缀
    output_file = os.path.join(input_dir, output_name)

    baidu_shouji_eng = BaiduShoujiEng()

    # 从文件导入
    wl_list = baidu_shouji_eng.import_from_file(input_file)

    # 导出到新文件
    baidu_shouji_eng.export_to_file(wl_list, output_file)

    print(f"导入自 {input_file}，并导出到 {output_file}.")
