import random
import io

from matplotlib import pyplot as plt


class PageReplacementAlgorithm:
    def __init__(self, frames):
        self.frames = frames  # 物理内存块的数量
        self.memory = []  # 当前内存块的状态
        self.page_faults = 0  # 缺页的数量
        self.page_hits = 0  # 页面命中的数量
        self.replacements = 0  # 置换的数量

    def simulate(self, page_sequence, file):
        """
        模拟页面置换过程。

        参数:
        page_sequence (list): 页面请求序列。
        file: 用于输出结果的文件对象。
        """
        raise NotImplementedError("子类必须重写此方法。")

    def is_page_in_memory(self, page):
        """
        检查页面是否已在内存中。

        参数:
        page (int): 要检查的页面编号。

        返回:
        bool: 如果页面在内存中返回True，否则返回False。
        """
        return page in self.memory

    def record_page_fault(self):
        """
        记录一次缺页。
        """
        self.page_faults += 1

    def record_page_hit(self):
        """
        记录一次页面命中。
        """
        self.page_hits += 1

    def get_page_fault_rate(self):
        """
        计算缺页率。

        返回:
        float: 缺页率。
        """
        return self.page_faults / (self.page_faults + self.page_hits)

    def get_replacement_rate(self):
        """
        计算置换率。

        返回:
        float: 置换率。
        """
        return self.replacements / (self.page_faults + self.page_hits)


# FIFO (First In, First Out)先进先出算法实现
class FIFO(PageReplacementAlgorithm):
    def __init__(self, frames):
        super().__init__(frames)
        self.queue = []  # 用于跟踪页面插入顺序的FIFO队列

    def simulate(self, page_sequence, file):
        counter = 1  # 初始化序列号计数器
        for page in page_sequence:
            if not self.is_page_in_memory(page):  # 如果页面不在内存中
                self.record_page_fault()  # 记录缺页
                if len(self.memory) == self.frames:  # 如果内存已满
                    # 移除FIFO队列中最早的页面，并从内存中移除该页面
                    self.memory.remove(self.queue.pop(0))
                    self.replacements += 1  # 增加置换次数
                # 将新页面添加到内存和FIFO队列中
                self.memory.append(page)
                self.queue.append(page)
            else:  # 如果页面已在内存中
                self.record_page_hit()  # 记录页面命中
            # 将当前内存状态写入文件，每行前加上序列号
            file.write(f"{counter}: {self.__class__.__name__} - Memory state: {self.memory}\n")
            counter += 1  # 序列号递增


# LRU (Least Recently Used)最近最少使用算法实现
class LRU(PageReplacementAlgorithm):
    def __init__(self, frames):
        super().__init__(frames)
        self.page_time = {}  # 用于跟踪每个页面最后一次访问时间的字典

    def simulate(self, page_sequence, file):
        time = 0  # 初始化时间，用于记录页面访问时间
        for page in page_sequence:
            if not self.is_page_in_memory(page):
                self.record_page_fault()  # 如果页面不在内存中，记录缺页
                if len(self.memory) == self.frames:
                    # 如果内存已满，找到最久未使用的页面（访问时间最早的页面）
                    oldest_page = min(self.page_time, key=self.page_time.get)
                    self.memory.remove(oldest_page)  # 从内存中移除最久未使用的页面
                    del self.page_time[oldest_page]  # 从访问时间字典中删除该页面
                    self.replacements += 1  # 增加置换次数
                self.memory.append(page)  # 将新页面添加到内存中
                self.page_time[page] = time  # 更新新页面的访问时间
            else:
                self.record_page_hit()  # 如果页面已在内存中，记录页面命中
                self.page_time[page] = time  # 更新页面的访问时间
            # 写入文件时，加上序列号和内存状态
            file.write(f"{time + 1}: {self.__class__.__name__} - Memory state: {self.memory}\n")
            time += 1  # 时间递增，对应下一个页面请求


# OPT (Optimal Page Replacement Algorithm)最佳页面置换算法实现
class OPT(PageReplacementAlgorithm):
    def simulate(self, page_sequence, file):
        counter = 1  # 序列号计数器，用于输出的行前缀
        for i, page in enumerate(page_sequence):
            # 遍历页面请求序列，`i` 是索引，`page` 是页面编号
            if not self.is_page_in_memory(page):
                # 如果页面不在内存中，记录一次缺页
                self.record_page_fault()
                if len(self.memory) == self.frames:
                    # 如果内存已满，找出未来最长时间内不会被访问的页面
                    longest_unused_page = self.find_longest_unused_page(page_sequence[i + 1:])
                    # 从内存中移除这个页面
                    self.memory.remove(longest_unused_page)
                    self.replacements += 1  # 增加置换次数
                # 将当前请求的页面添加到内存中
                self.memory.append(page)
            else:
                # 如果页面已经在内存中，记录一次页面命中
                self.record_page_hit()
            # 将当前内存状态写入文件，每行前加上序列号
            file.write(f"{counter}: {self.__class__.__name__} - Memory state: {self.memory}\n")
            counter += 1  # 更新序列号

    def find_longest_unused_page(self, future_sequence):
        # 在未来的页面请求序列中找出最长时间内不会被访问的页面
        last_used = -1  # 最远的未来索引
        page_to_replace = None  # 将要被替换的页面
        for page in self.memory:
            # 遍历当前内存中的页面
            if page not in future_sequence:
                # 如果页面不在未来序列中，直接返回该页面
                return page
            index = future_sequence.index(page)
            # 找到页面在未来序列中最远的索引位置
            if index > last_used:
                last_used = index
                page_to_replace = page
        # 返回最长时间内不会被访问的页面
        return page_to_replace


# LFU (Least Frequently Used Page Replacement Algorithm)最不常用页面置换算法实现
class LFU(PageReplacementAlgorithm):
    def __init__(self, frames):
        super().__init__(frames)
        self.page_frequency = {}  # 页面频率字典，用于记录每个页面的访问频率

    def simulate(self, page_sequence, file):
        counter = 1  # 序列号计数器，用于输出的行前缀
        for page in page_sequence:
            if not self.is_page_in_memory(page):
                self.record_page_fault()  # 如果页面不在内存中，记录缺页
                if len(self.memory) == self.frames:
                    # 如果内存已满，找出最少使用的页面
                    least_frequent_page = self.find_least_frequent_page()
                    self.memory.remove(least_frequent_page)  # 移除最少使用的页面
                    del self.page_frequency[least_frequent_page]  # 删除该页面的频率记录
                    self.replacements += 1  # 记录一次置换
                self.memory.append(page)  # 将新页面添加到内存中
                self.page_frequency[page] = 1  # 初始化新页面的访问频率
            else:
                self.record_page_hit()  # 如果页面已在内存中，记录页面命中
                self.page_frequency[page] += 1  # 增加页面的访问频率

            # 写入文件时，加上序列号和内存状态
            file.write(f"{counter}: {self.__class__.__name__} - Memory state: {self.memory}\n")
            counter += 1  # 序列号递增

    def find_least_frequent_page(self):
        # 找出访问频率最少的页面
        least_used = min(self.page_frequency.values())  # 获取最小的访问频率
        least_frequent_pages = [page for page in self.page_frequency if self.page_frequency[page] == least_used]
        # 在有最小访问频率的页面中，找出最早进入内存的页面
        for page in self.memory:
            if page in least_frequent_pages:
                return page  # 返回最少使用的页面


# SimpleCLOCK (Simple CLOCK Page Replacement Algorithm)简单时钟页面置换算法实现
class SimpleCLOCK(PageReplacementAlgorithm):
    def __init__(self, frames):
        super().__init__(frames)
        self.use_bit = {i: False for i in range(frames)}  # 用位字典，记录每个帧是否被访问过
        self.hand = 0  # 时钟指针，指示当前检查的帧

    def simulate(self, page_sequence, file):
        counter = 1  # 序列号计数器，用于输出的行前缀
        for page in page_sequence:
            # 遍历页面请求序列
            if not self.is_page_in_memory(page):
                # 如果页面不在内存中，记录一次缺页
                self.record_page_fault()
                # 使用时钟算法进行页面置换
                while self.use_bit[self.hand]:
                    # 如果当前帧的用位为真，置为假，并移动指针
                    self.use_bit[self.hand] = False
                    self.hand = (self.hand + 1) % self.frames
                if len(self.memory) == self.frames:
                    # 如果内存已满，则替换页面
                    self.memory[self.hand] = page
                    self.replacements += 1  # 增加置换次数
                else:
                    # 如果内存未满，则添加页面
                    self.memory.append(page)
                # 设置新页面的用位为真
                self.use_bit[self.hand] = True
            else:
                # 如果页面已在内存中，记录页面命中，并设置用位为真
                self.record_page_hit()
                page_index = self.memory.index(page)
                self.use_bit[page_index] = True

            # 写入文件时，加上序列号和内存状态
            file.write(f"{counter}: {self.__class__.__name__} - Memory state: {self.memory}\n")
            counter += 1  # 序列号递增


# EnhancedCLOCK (Enhanced CLOCK Page Replacement Algorithm)增强时钟页面置换算法实现
class EnhancedCLOCK(PageReplacementAlgorithm):
    def __init__(self, frames):
        super().__init__(frames)
        self.use_bit = {i: False for i in range(frames)}  # 用位字典，用于标记每个帧是否被访问过
        self.modify_bit = {i: False for i in range(frames)}  # 修改位字典，用于标记每个帧自上次访问以来是否被修改过
        self.hand = 0  # 时钟指针，用于指示当前检查的帧

    def simulate(self, page_sequence, file):
        counter = 1  # 序列号计数器，用于输出的行前缀
        for page in page_sequence:
            # 遍历页面请求序列
            if not self.is_page_in_memory(page):
                self.record_page_fault()  # 如果页面不在内存中，记录缺页
                replaced = False
                while not replaced:
                    # 进行页面置换
                    if not self.use_bit[self.hand] and not self.modify_bit[self.hand]:
                        # 如果当前帧的用位和修改位都为假，则替换该帧
                        if len(self.memory) == self.frames:
                            self.memory[self.hand] = page
                            self.replacements += 1  # 记录一次置换
                        else:
                            self.memory.append(page)
                        self.modify_bit[self.hand] = False  # 重置修改位
                        replaced = True  # 设置替换标志为真
                    else:
                        # 如果用位为真，则清除用位，并继续检查下一帧
                        self.use_bit[self.hand] = False
                    self.hand = (self.hand + 1) % self.frames  # 移动时钟指针
                self.use_bit[self.hand] = True  # 新加入或替换的页面设置用位为真
            else:
                self.record_page_hit()  # 如果页面已在内存中，记录页面命中
                page_index = self.memory.index(page)
                self.use_bit[page_index] = True  # 页面被访问，设置用位为真

            # 写入文件时，加上序列号和内存状态
            file.write(f"{counter}: {self.__class__.__name__} - Memory state: {self.memory}\n")
            counter += 1  # 序列号递增


# 生成一个随机页面序列函数
def generate_page_sequence(size, upper_bound):
    """
    生成一个随机页面序列。

    参数:
    size (int): 页面序列的大小，即序列中将有多少个页面。
    upper_bound (int): 页面编号的上限，用于确定随机性的范围。

    返回:
    list: 代表页面序列的整数列表。
    """
    # 使用列表推导式生成一个随机页面序列，其中页面编号从1到upper_bound
    return [random.randint(1, upper_bound) for _ in range(size)]


# 测试不同的页面置换算法函数
def test_page_replacement_algorithms(algorithms, page_sequence, frame_counts, file):
    """
    测试不同的页面置换算法。

    参数:
    algorithms (list): 要测试的页面置换算法类的列表。
    page_sequence (list): 用于模拟的页面序列。
    frame_counts (list): 用于测试每种算法的帧数列表。
    file: 用于将输出写入的文件对象。

    返回:
    dict: 以算法名称为键，页面缺页率列表为值的字典。
    """
    # 初始化结果字典，用于存储每种算法的页面缺页率
    results = {alg.__name__: [] for alg in algorithms}
    # 遍历不同的帧数
    for frames in frame_counts:
        # 对每种算法进行测试
        for alg_class in algorithms:
            alg = alg_class(frames)  # 创建算法实例
            alg.simulate(page_sequence, file)  # 模拟页面置换过程
            # 记录当前帧数下算法的页面缺页率
            results[alg_class.__name__]['page_fault_rates'].append(alg.get_page_fault_rate())
            results[alg_class.__name__]['replacement_rates'].append(alg.get_replacement_rate())
    # 返回包含所有算法页面缺页率的字典
    return results


# 绘制各种页面置换算法的性能函数
def plot_performance(results, frame_counts):
    """
    绘制各种页面置换算法的性能。

    参数:
    results (dict): 一个字典，键是算法名称，值是包含缺页率和置换率的字典。
    frame_counts (list): 测试的帧数列表。

    说明:
    此函数将根据提供的算法结果和帧数，绘制出每种算法的缺页率和置换率性能曲线图。
    图中将展示不同帧数下的缺页率和置换率，以便比较不同算法的性能。
    """
    # 设置支持中文的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为SimHei
    plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

    # 创建一个画布和两个子图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # 在第一个子图中绘制缺页率曲线
    for alg_name, rates in results.items():
        ax1.plot(frame_counts, rates['page_fault_rates'], label=f"{alg_name}")

    ax1.set_xlabel('物理块数')
    ax1.set_ylabel('缺页率')
    ax1.set_title('缺页率比较')
    ax1.legend()

    # 在第二个子图中绘制置换率曲线
    for alg_name, rates in results.items():
        ax2.plot(frame_counts, rates['replacement_rates'], label=f"{alg_name}")

    ax2.set_xlabel('物理块数')
    ax2.set_ylabel('置换率')
    ax2.set_title('置换率比较')
    ax2.legend()

    # 调整子图布局
    plt.tight_layout()
    # 显示图表
    plt.show()


# 运行仿真和绘图的主函数模块
if __name__ == "__main__":
    # 设置页面序列的大小和页面编号的上限
    sequence_size = 100  # 页面序列的大小
    page_upper_bound = 10  # 页面编号的上限

    # 定义要测试的页面置换算法类列表
    algorithms = [FIFO, LRU, OPT, LFU, SimpleCLOCK, EnhancedCLOCK]  # 可以添加其他算法类

    # 定义要测试的物理帧数列表
    frame_counts = [2, 3, 4, 5, 6, 7, 8]

    # 初始化一个字典来收集结果
    results = {alg.__name__: {'page_fault_rates': [], 'replacement_rates': []} for alg in algorithms}

    # 打开（或创建）一个文件用于记录算法的输出结果
    with open('algorithm_output.txt', 'w') as output_file:
        # 对每个算法和帧数进行测试
        for alg_class in algorithms:
            for frames in frame_counts:
                alg = alg_class(frames)
                page_sequence = generate_page_sequence(sequence_size, page_upper_bound)
                with io.StringIO() as file:  # 使用 StringIO 对象来收集模拟输出
                    alg.simulate(page_sequence, file)  # 运行模拟
                    # 写入模拟输出到实际文件
                    output_file.write(f"Algorithm: {alg_class.__name__}, Frames: {frames}\n")
                    output_file.write(file.getvalue() + "\n")
                # 记录缺页率和置换率
                results[alg_class.__name__]['page_fault_rates'].append(alg.get_page_fault_rate())
                # 假设算法类有一个方法来获取置换率
                results[alg_class.__name__]['replacement_rates'].append(alg.get_replacement_rate())

    # 根据测试结果绘制算法性能曲线图
    plot_performance(results, frame_counts)