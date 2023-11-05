import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import io
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from PageReplacementAlgorithm import generate_page_sequence, plot_performance, FIFO, LRU, OPT, LFU, SimpleCLOCK, \
    EnhancedCLOCK


def is_valid_frame_number(self, frame_number):
    # 验证物理块数是否已选择且有效（在这里我们假设有效值在2到8之间）
    try:
        frames = int(frame_number)
        return frames in self.frame_counts
    except ValueError:  # 如果frame_number不能转换为整数，则返回False
        return False


def on_invalid_frame_number(self):
    messagebox.showerror("无效输入", "请选择一个有效的物理块数。")


def is_valid_size(user_input):
    # 用户输入必须是非零的整数，且小于200
    if user_input.isdigit():
        size = int(user_input)
        return size > 0 and size <= 200
    return False


def on_invalid():
    messagebox.showerror("请设置页面序列大小", "请输入一个非零的整数，且不超过200。")


class PageReplacementApp:
    def run_simulation(self):
        # 获取输入的页面序列大小
        sequence_input = self.sequence_size_entry.get()
        if not is_valid_size(sequence_input):
            on_invalid()
            return  # 不继续执行，等待用户更正输入

        # 在检查页面序列大小输入有效后，检查物理块数
        frames_input = self.frame_number.get()
        if not is_valid_frame_number(self, frames_input):
            on_invalid_frame_number(self)
            return  # 不继续执行，等待用户更正输入
        sequence_size = int(sequence_input)
        upper_bound = 10
        # 动态生成页面序列并显示
        page_sequence = generate_page_sequence(sequence_size, upper_bound)
        self.sequence_display.delete(1.0, tk.END)  # 清除之前的内容
        sequence_str = ' '.join(str(p) for p in page_sequence)
        self.sequence_display.insert(tk.END, sequence_str)

        # 获取选择的物理块数和算法，并运行模拟
        frames = int(self.frame_number.get())
        # 获取选择的算法
        algorithm_name = self.algorithm.get()

        # 检查是否选择了算法
        if not algorithm_name:
            messagebox.showerror("未选择算法", "请先选择一个页面置换算法。")
            return
        algorithm_class = globals()[algorithm_name]
        algorithm = algorithm_class(frames)
        output_file = io.StringIO()
        algorithm.simulate(page_sequence, output_file)

        display = self.process_displays[algorithm_name]  # 获取相应算法的文本框
        display.delete(1.0, tk.END)  # 清除旧的置换过程
        display.insert(tk.END, output_file.getvalue())  # 显示新的置换过程
        # 更新 self.results 字典
        if algorithm_name not in self.results:
            self.results[algorithm_name] = {'page_fault_rates': [], 'replacement_rates': []}

        self.results[algorithm_name]['page_fault_rates'].append(algorithm.get_page_fault_rate())
        self.results[algorithm_name]['replacement_rates'].append(algorithm.get_replacement_rate())

    def run_all_simulations(self):
        # 验证页面序列大小输入
        sequence_input = self.sequence_size_entry.get()
        if not is_valid_size(sequence_input):
            on_invalid()
            return  # 页面序列大小输入无效，不继续执行

        sequence_size = int(sequence_input)
        page_upper_bound = 10
        page_sequence = generate_page_sequence(sequence_size, page_upper_bound)

        # 显示动态生成的页面序列
        self.sequence_display.delete(1.0, tk.END)
        sequence_str = ' '.join(str(p) for p in page_sequence)
        self.sequence_display.insert(tk.END, sequence_str)

        # 验证物理块数
        frames_input = self.frame_number.get()
        if not frames_input or not is_valid_frame_number(self, frames_input):
            on_invalid_frame_number(self)
            return  # 物理块数输入无效，不继续执行

        frames = int(frames_input)

        # 初始化或清空 self.results 中的数据
        self.results = {alg: {'page_fault_rates': [], 'replacement_rates': []} for alg in self.algorithms}

        # 运行所有算法的模拟
        for frame_count in self.frame_counts:
            for alg_name in self.algorithms:
                algorithm_class = globals()[alg_name]
                algorithm = algorithm_class(frame_count)
                output_file = io.StringIO()
                algorithm.simulate(page_sequence, output_file)

                # 保存每个算法在当前帧数下的性能数据
                self.results[alg_name]['page_fault_rates'].append(algorithm.get_page_fault_rate())
                self.results[alg_name]['replacement_rates'].append(algorithm.get_replacement_rate())

                # 显示算法的置换过程
                display = self.process_displays[alg_name]
                display.delete(1.0, tk.END)
                display.insert(tk.END, output_file.getvalue())

        # 设置 simulations_run 标志为 True，表示已经运行了模拟
        self.simulations_run = True

    def plot_all_performance(self):
        # 在尝试绘制性能图表之前检查是否已经运行了所有模拟
        if not self.simulations_run:
            messagebox.showerror("操作无效", "请先执行所有算法的模拟。")
            return  # 如果没有运行模拟，则不继续执行
        selected_frame = int(self.frame_number.get())  # 从下拉列表中获取用户选择的帧数

        # 创建一个新的Tkinter窗口
        plot_window = tk.Toplevel(self.master)
        plot_window.title("Performance Plots")

        # 创建一个matplotlib图形
        fig, axs = plt.subplots(2, 1, figsize=(12, 6))

        # 调整子图之间的垂直间距
        fig.subplots_adjust(hspace=0.4)  # 调整这个值以增加间隔

        # 在第一个子图中绘制缺页率
        for alg_name, data in self.results.items():
            # 获取与所选帧数相对应的结果
            index = self.frame_counts.index(selected_frame)
            page_fault_rate = data['page_fault_rates'][index]
            bar = axs[0].bar(alg_name, page_fault_rate)
            # 在柱状图上方添加文本
            axs[0].text(bar[0].get_x() + bar[0].get_width() / 2, bar[0].get_height(),
                        f'{page_fault_rate:.2f}', ha='center', va='bottom')

        # axs[0].set_xlabel('Algorithms')
        axs[0].set_ylabel('Page Fault Rate')
        axs[0].set_title(f'Page Fault Rate Comparison for {selected_frame} Frames')

        # 在第二个子图中绘制置换率
        for alg_name, data in self.results.items():
            # 获取与所选帧数相对应的结果
            index = self.frame_counts.index(selected_frame)
            replacement_rate = data['replacement_rates'][index]
            bar = axs[1].bar(alg_name, replacement_rate)
            # 在柱状图上方添加文本
            axs[1].text(bar[0].get_x() + bar[0].get_width() / 2, bar[0].get_height(),
                        f'{replacement_rate:.2f}', ha='center', va='bottom')

        # axs[1].set_xlabel('Algorithms')
        axs[1].set_ylabel('Replacement Rate')
        axs[1].set_title(f'Replacement Rate Comparison for {selected_frame} Frames')

        # 将matplotlib图形嵌入到Tkinter窗口中
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.get_tk_widget().pack()
        canvas.draw()

        plot_window.mainloop()  # 这是为了确保新窗口能够独立运行

    def __init__(self, master):
        self.master = master
        self.master.title("页面置换算法模拟")
        self.algorithms = ['FIFO', 'LRU', 'OPT', 'LFU', 'SimpleCLOCK', 'EnhancedCLOCK']
        self.results = {alg: {'page_fault_rates': [], 'replacement_rates': []} for alg in self.algorithms}
        self.frame_counts = [2, 3, 4, 5, 6, 7, 8]  # 定义 frame_counts 作为类属性
        self.simulations_run = False  # 添加一个新属性来跟踪是否已运行模拟

        # 物理块数下拉列表
        ttk.Label(master, text="选择物理块数:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.frame_number = ttk.Combobox(master, values=self.frame_counts)
        # self.frame_number.set('选择物理块数')  # 设置一个提示性的默认值
        self.frame_number.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # 算法选择下拉列表
        ttk.Label(master, text="选择算法:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.algorithm = ttk.Combobox(master, values=('FIFO', 'LRU', 'OPT', 'LFU', 'SimpleCLOCK', 'EnhancedCLOCK'))
        self.algorithm.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        # 页面序列大小输入
        ttk.Label(master, text="设置页面序列大小:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.sequence_size_entry = ttk.Entry(master)
        self.sequence_size_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        # 运行按钮
        self.run_button = ttk.Button(master, text="运行模拟", command=self.run_simulation)
        self.run_button.grid(row=0, column=1, columnspan=2, padx=10, pady=5)

        # 执行所有算法的按钮
        self.run_all_button = ttk.Button(master, text="执行所有算法", command=self.run_all_simulations)
        self.run_all_button.grid(row=1, column=1, columnspan=2, padx=10, pady=5)

        # 查看性能曲线图的按钮
        self.plot_button = ttk.Button(master, text="查看性能曲线图", command=self.plot_all_performance)
        self.plot_button.grid(row=2, column=1, columnspan=2, padx=10, pady=5)

        # 显示置换过程的文本框
        self.process_displays = {}  # 创建一个字典来存储每个算法的文本框
        for i, alg in enumerate(['FIFO', 'LRU', 'OPT', 'LFU', 'SimpleCLOCK', 'EnhancedCLOCK'], start=6):
            ttk.Label(master, text=f"{alg} 算法:").grid(row=i, column=0, padx=10, pady=5, sticky='nw')
            display = scrolledtext.ScrolledText(master, height=6, width=80)
            display.grid(row=i, column=1, padx=10, pady=5)
            self.process_displays[alg] = display

        # 页面序列显示的文本框
        ttk.Label(master, text="页面序列:").grid(row=12, column=0, padx=10, pady=5, sticky='nw')
        self.sequence_display = scrolledtext.ScrolledText(master, height=4, width=80)
        self.sequence_display.grid(row=12, column=1, padx=10, pady=5)

        # 添加证明原创的标签，设置字体为宋体，颜色为红色
        originality_label = ttk.Label(master, text="海南大学21级计科李季鸿20213002624原创程序", foreground="red")
        originality_label.grid(row=13, column=1, padx=10, pady=5, sticky='e')  # 根据需要调整位置


# 创建窗口和应用
root = tk.Tk()
app = PageReplacementApp(root)
root.mainloop()
