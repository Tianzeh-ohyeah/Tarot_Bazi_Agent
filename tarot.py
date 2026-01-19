import os
import random
import tkinter as tk
from tkinter import ttk
import threading
import time
import math
from datetime import datetime
from google import genai
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# --- 1. 核心修复：API 环境适配 ---
# 它会自动在你当前文件夹找 .env 文件并读取里面的变量
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"SDK 初始化失败: {e}")

def get_intelligent_model_pool():
    """动态探测可用模型并按性能排序"""
    try:
        models = client.models.list()
        pool = []
        # 严格黑名单：排除掉配额常年为 0 的特殊模型
        black_list = ["computer-use", "embedding", "tts", "imagen", "aqa", "vision"]
        
        for m in models:
            m_name = m.name.lower()
            # 必须包含 gemini，且不在黑名单中，且必须是 flash 或 pro
            if "gemini" in m_name and not any(x in m_name for x in black_list):
                if any(v in m_name for v in ["flash", "pro"]):
                    full_name = m.name if m.name.startswith("models/") else f"models/{m.name}"
                    pool.append(full_name)
        
        # 定义 2026 算力优先级
        def model_priority(name):
            n = name.lower()
            if "3-flash" in n: return 10
            if "2.0-flash" in n: return 8
            if "1.5-pro" in n: return 6
            if "1.5-flash" in n: return 4
            return 0

        pool.sort(key=model_priority, reverse=True)
        # 只保留最有把握的前 3 个模型，避免无效 fallback 耗尽配额
        return pool[:3] if pool else ["models/gemini-1.5-flash"]
    except:
        return ["models/gemini-3-flash", "models/gemini-1.5-flash"]

# 全局算力状态
MODEL_POOL = get_intelligent_model_pool()
MODEL_LOCK = threading.Lock()
CURRENT_MODEL_INDEX = 0

# --- 3. 资源定义 ---
def get_dynamic_lunar_params():
    """根据当前算命时刻，动态推算流年干支和紫微四化，拒绝 Hardcode"""
    now = datetime.now()
    year = now.year
    # 干支计算逻辑 (简化算法)
    gan = ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"]
    zhi = ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"]
    c_gan = gan[year % 10]
    c_zhi = zhi[year % 12]
    # 紫微四化逻辑（核心算力参数）
    si_hua_map = {
        "甲": "廉贞化禄、破军化权、武曲化科、太阳化忌",
        "乙": "天机化禄、天梁化权、紫微化科、太阴化忌",
        "丙": "天同化禄、天机化权、文昌化科、廉贞化忌",
        "丁": "太阴化禄、天同化权、天机化科、巨门化忌",
        "戊": "贪狼化禄、太阴化权、右弼化科、天机化忌",
        "己": "武曲化禄、贪狼化权、天梁化科、文曲化忌",
        "庚": "太阳化禄、武曲化权、太阴化科、天同化忌",
        "辛": "巨门化禄、太阳化权、文曲化科、文昌化忌",
        "壬": "天梁化禄、紫微化权、左辅化科、武曲化忌",
        "癸": "破军化禄、巨门化权、太阴化科、贪狼化忌"
    }
    return {
        "lunar_year": f"{c_gan}{c_zhi}",
        "si_hua": si_hua_map.get(c_gan, ""),
        "cur_date": now.strftime("%Y-%m-%d %H:%M")
    }

# --- 2. 资源定义：全量塔罗牌库 ---
MAJOR = ["愚者", "魔术师", "女教皇", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]
SUITS = ["权杖", "圣杯", "宝剑", "星币"]
NUMS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "侍从", "骑士", "皇后", "国王"]
FULL_DECK = MAJOR + [f"{s}{n}" for s in SUITS for n in NUMS]
ZODIAC_HOURS = ["子时 (23:00-01:00)", "丑时 (01:00-03:00)", "寅时 (03:00-05:00)", "卯时 (05:00-07:00)", "辰时 (07:00-09:00)", "巳时 (09:00-11:00)", "午时 (11:00-13:00)", "未时 (13:00-15:00)", "申时 (15:00-17:00)", "酉时 (17:00-19:00)", "戌时 (19:00-21:00)", "亥时 (21:00-23:00)"]

class OracleSystem:
    def __init__(self, master):
        self.master = master
        master.title("TZ 多维算力决策系统 v2026")
        master.geometry("1100x950")
        master.configure(bg="#000000")
        
        self.C_GOLD = "#D4AF37"
        self.C_BG = "#000000"
        self.C_INPUT_BG = "#0A0A0F" 
        self.C_TEXT = "#FFFFFF"     
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=self.C_INPUT_BG, background="#222", foreground=self.C_TEXT, arrowcolor=self.C_GOLD)

        self.setup_ui()
        self.animate_stars()

    def setup_ui(self):
        self.master.grid_rowconfigure(0, weight=30) 
        self.master.grid_rowconfigure(1, weight=40) 
        self.master.grid_rowconfigure(2, weight=30) 
        self.master.grid_columnconfigure(0, weight=1)

        self.input_area = tk.Frame(self.master, bg=self.C_BG, padx=40, pady=5)
        self.input_area.grid(row=0, sticky="nsew")
        
        tk.Label(self.input_area, text="🔱 核心命理维度采集 🔱", fg=self.C_GOLD, bg=self.C_BG, font=("Microsoft YaHei", 12, "bold")).pack(pady=(10, 5))

        # --- 第一行：基础属性 (加回了出生地) ---
        f1 = tk.Frame(self.input_area, bg=self.C_BG); f1.pack(fill="x", pady=5)
        tk.Label(f1, text="名讳:", fg=self.C_TEXT, bg=self.C_BG).pack(side="left")
        self.name_ent = tk.Entry(f1, width=8, bg=self.C_INPUT_BG, fg=self.C_TEXT, insertbackground=self.C_GOLD)
        self.name_ent.pack(side="left", padx=5); self.name_ent.insert(0, "无名氏")

        self.gender_cb = ttk.Combobox(f1, values=["乾 (男)", "坤 (女)"], width=6, state="readonly")
        self.gender_cb.set("乾 (男)"); self.gender_cb.pack(side="left", padx=10)
        
        self.calendar_cb = ttk.Combobox(f1, values=["公历", "农历"], width=5, state="readonly")
        self.calendar_cb.set("公历"); self.calendar_cb.pack(side="left", padx=5)

        tk.Label(f1, text=" 出生地:", fg=self.C_TEXT, bg=self.C_BG).pack(side="left")
        self.place_ent = tk.Entry(f1, width=12, bg=self.C_INPUT_BG, fg=self.C_TEXT, insertbackground=self.C_GOLD)
        self.place_ent.pack(side="left", padx=5); self.place_ent.insert(0, "北京")

        # --- 第二行：生辰 ---
        f2 = tk.Frame(self.input_area, bg=self.C_BG); f2.pack(fill="x", pady=5)
        tk.Label(f2, text="时间:", fg=self.C_TEXT, bg=self.C_BG).pack(side="left")
        self.year_cb = ttk.Combobox(f2, values=[str(y) for y in range(1940, 2027)], width=6); self.year_cb.set("1996"); self.year_cb.pack(side="left", padx=2)
        self.month_cb = ttk.Combobox(f2, values=[f"{m:02d}" for m in range(1, 13)], width=4); self.month_cb.set("03"); self.month_cb.pack(side="left", padx=2)
        self.day_cb = ttk.Combobox(f2, values=[f"{d:02d}" for d in range(1, 32)], width=4); self.day_cb.set("05"); self.day_cb.pack(side="left", padx=2)
        self.hour_cb = ttk.Combobox(f2, values=ZODIAC_HOURS, width=18, state="readonly"); self.hour_cb.set("巳时"); self.hour_cb.pack(side="left", padx=10)

        # --- 第三行：诉求 ---
        f3 = tk.Frame(self.input_area, bg=self.C_BG); f3.pack(fill="x", pady=(10, 0))
        tk.Label(f3, text="心中祈愿:", fg=self.C_GOLD, bg=self.C_BG, font=("Microsoft YaHei", 11, "bold")).pack(side="left")
        self.quest_ent = tk.Entry(f3, bg="#0F0F1A", fg=self.C_TEXT, insertbackground=self.C_GOLD, font=("Microsoft YaHei", 12), borderwidth=1)
        self.quest_ent.pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=8); self.quest_ent.insert(0, "测算近期的事业财运发展")

        # 画布与按钮
        self.canvas = tk.Canvas(self.master, bg=self.C_BG, highlightthickness=0)
        self.canvas.grid(row=1, sticky="nsew")
        self.run_btn = tk.Button(self.canvas, text="✦ 开启算力合参 ✦", command=self.start_workflow, bg=self.C_GOLD, fg="black", font=("Microsoft YaHei", 14, "bold"), padx=50, pady=15, relief="flat")
        self.canvas_btn_window = self.canvas.create_window(550, 200, window=self.run_btn)

        # 输出区
        output_frame = tk.Frame(self.master, bg=self.C_BG, padx=40, pady=15)
        output_frame.grid(row=2, sticky="nsew")
        self.out_text = tk.Text(output_frame, wrap="word", bg="#050505", fg="#F0F0F0", font=("Microsoft YaHei", 11), padx=30, pady=20, spacing2=8)
        self.out_text.pack(fill="both", expand=True)
        self.out_text.tag_config("gold_tag", foreground="#D4AF37", font=("Microsoft YaHei", 12, "bold"))
        self.out_text.tag_config("system_tag", foreground="#888888", font=("Consolas", 10))

    def safe_generate_with_fallback(self, prompt, model_pool, delay=0):
        """具备防熔断机制的生成器"""
        if delay > 0: time.sleep(delay)
        
        last_error = ""
        for model_name in model_pool:
            try:
                # 显式设置较短的超时，防止挂死
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text, model_name
            except Exception as e:
                last_error = str(e)
                # 如果是配额问题，直接休眠并尝试池中下一个稳健模型
                if "429" in last_error:
                    time.sleep(1.5) 
                continue 
        
        return f"【维度坍缩】: 当前算力节点繁忙(429)。请稍后 30 秒再次开启推演。", "None"

    def start_workflow(self):
        self.out_text.delete("1.0", tk.END)
        self.run_btn.config(state="disabled", text="正在推演量子场...")
        
        # --- 核心修复：在此处打包 info 字典时必须包含 'calendar' ---
        info = {
            "name": self.name_ent.get(),
            "gender": self.gender_cb.get(),
            "calendar": self.calendar_cb.get(),
            "place": self.place_ent.get(),
            "birth": f"{self.year_cb.get()}-{self.month_cb.get()}-{self.day_cb.get()}",
            "hour": self.hour_cb.get(),
            "question": self.quest_ent.get()
        }
        threading.Thread(target=self._run_agents, args=(info,), daemon=True).start()

    def _run_agents(self, info):
        try:
            # 获取动态流年与环境参数
            model_pool = get_intelligent_model_pool() 
            current_model = model_pool[0]  # 用于最终显示的默认标签
            lunar = get_dynamic_lunar_params()
            sample_cards = random.sample(FULL_DECK, 3)
            card_names = [f"{c}({random.choice(['正位', '逆位'])})" for c in sample_cards]
            
            # --- 第一阶段：专家组会诊（元神校准 + 多维判定） ---
            # 消耗 1 次额度，完成原有的前 4 个步骤
            self._write(f">> 算力矩阵激活 | 首选算力: {current_model}\n", "system_tag")
            self._write(f">> 正在进行元神校准与专家组联合会诊...\n", "system_tag")

            # --- 第二步：构造“强制扣题”的增强上下文 ---
            # 把 AI 自己算的元神喂回去
            refined_context = (
                f"【核心参数输入】：\n"
                f"- 命主：{info['name']} ({info['gender']})，出生地：{info['place']}\n"
                f"- 生辰：{info['birth']} {info['hour']}（历法：{info['calendar']}）\n"
                f"- 外部环境：当前日期 {lunar['cur_date']}，流年 {lunar['lunar_year']}（四化：{lunar['si_hua']}）\n"
                f"- 灵性变量：塔罗牌阵 {card_names}\n\n"

                f"【系统推演任务】：请针对诉求【{info['question']}】，执行以下严密的命理逻辑计算：\n\n"

                f"1. **精准排盘与自校验 (逻辑根基)**：\n"
                f"   - **时空校准**：首先根据出生地【{info['place']}】推算其经度偏移，将北京时间转化为“真太阳时”以确定准确时辰。\n"
                f"   - **姓名能量对冲**：分析名讳【{info['name']}】的五行属性。判定该名字对八字原局是起到了‘化解冲突’、‘增强气势’还是‘平衡五行’的作用。并在[根基判定]中体现此加成。\n"
                f"   - **干支推导**：已知1998年5月19日为丙子日，请以此为基准逻辑推演命主出生当日的干支（日柱/元神），并核对是否涉及节气交替导致的月份或年份变更。\n"
                f"   - **输出要求**：必须以‘【逻辑定性】：元神[XX]金木水火土，日柱[XX]，时柱[XX]’作为开头。\n\n"

                f"2. **多维深度判定 (6:3:1 权重分发)**：\n"
                f"   - **[维度一：气数判定 (60%权重)]**：分析元神与流年 {lunar['lunar_year']} 的生克平衡。判定此时流年是喜用加持还是忌神对冲。这是决定成败的核心底层能量。\n"
                f"   - **[维度二：时空变数 (30%权重)]**：结合紫微斗数流年四化【{lunar['si_hua']}】，分析该问题所在宫位（如财帛宫或官禄宫）的损益情况，判断现实中的变动概率。\n"
                f"   - **[维度三：灵性映照 (10%权重)]**：解析塔罗牌 {card_names} 揭示的心理暗示。判定命主当下的潜意识驱动力是助力还是阻碍。\n\n"

                f"3. **输出协议**：\n"
                f"   - 禁止模棱两可，必须清晰列出以上三个判定的具体结论。\n"
                f"   - 总字数控制在 500 字左右，逻辑严密，为后续主祭司的命运裁决提供硬核数据支持。"
            )

            # 第一次调用：完成所有维度的原始计算
            expert_raw_data, m1 = self.safe_generate_with_fallback(refined_context, model_pool)
            
            # 提取元神结论展示给用户，增加确定感
            logic_line = expert_raw_data.split('\n')[0] if '【' in expert_raw_data else "元神校准完成"
            self._write(f"【算力溯源: {m1}】: {logic_line}\n", "gold_tag")

            # --- 第二阶段：终极总结与命运剧本创作 (核心请求 2) ---
            self._write(f">> 移交主祭司执行 [逻辑验证] 与 [剧本演化]...\n", "system_tag")

            # --- 步骤 2：主祭司终极合参 (执行 6:3:1 权重裁决) ---
            self._write(f">> 正在根据 6:3:1 权重执行最终映射判定...\n", "system_tag")
            
            p4 = (f"你是【最高决策主祭司】。用户当前最关心的问题是：【{info['question']}】。\n\n"
                  f"### 📋 专家组判定依据：\n{expert_raw_data}\n\n"
                  f"### ⚖️ 裁决逻辑（必须强制执行）：\n"
                  f"1. **权重合参**：根基(60%)、现实(30%)、心理(10%)。若[根基判定]显示‘稳/吉’，而用户问题涉及‘是否会变/是否有灾’，则必须判定为‘稳/无忧’，即便现实变数中有小干扰，也应解释为磨炼而非结果。\n"
                  f"2. **流年对冲**：结合 {lunar['lunar_year']} 年的特性，判断其对【{info['question']}】是起到‘推波助澜’还是‘阻碍摧毁’的作用。\n\n"
                  f"3. **变量定序**：必须遵循‘命大于卦’原则。塔罗牌阵仅代表命主当下的[心力状态]，绝不可因一张坏牌就全盘否定八字根基（60%）和姓名化解力。若根基稳固，即便牌阵显示‘危机’，也必须定论为‘有惊无险’而非‘彻底终结’。"
                  f"### 🖋️ 最终命运剧本输出协议：\n"
                  f"1. **确认本尊**：开头先以元神定性（如：‘作为XX日主的你...’）。\n"
                  f"2. **判决回应**：第一段必须用极度确定的语气，针对【{info['question']}】给出一个定论。\n"
                  f"3. **时空叙事**：以‘在接下来的时空里...’开头。描述在 {lunar['lunar_year']} 年这个结论如何通过具体事件显现。\n"
                  f"4. **指引避忌**：针对结论，给出一个必须做的动作和一个必须避开的雷区。\n"
                  f"限制 500 字，禁止废话，必须高度扣题。")
            
            final_report, m2 = self.safe_generate_with_fallback(p4, model_pool)

            self._write(f"\n【运算完成】终极判决由算力节点 {m2} 签发。\n", "system_tag")
            self.master.after(0, lambda: self._final_display({}, final_report, info))

        except Exception as e:
            self._write(f"\n[算力中断]: {e}")
            self.master.after(0, lambda: self.run_btn.config(state="normal", text="✦ 重新开启推演 ✦"))

    def _final_display(self, results, a4_out, info):
        lunar = get_dynamic_lunar_params()
        self.out_text.delete("1.0", tk.END)
        self.out_text.insert(tk.END, f"尊敬的 {info['name']} 阁下：\n报告已生成。\n{'—' * 60}\n\n")
        self.paragraph_write(a4_out)
        self.run_btn.config(state="normal", text="✦ 开启新一轮推演 ✦")

    def paragraph_write(self, text):
        def _anim():
            for char in text:
                # 使用 after 将 UI 更新抛回主线程
                self.master.after(0, lambda c=char: (self.out_text.insert(tk.END, c), self.out_text.see(tk.END)))
                time.sleep(0.01)
        threading.Thread(target=_anim, daemon=True).start()

    def _write(self, msg, tag=None):
        self.master.after(0, lambda: (self.out_text.insert(tk.END, msg, tag), self.out_text.see(tk.END)))

    def animate_stars(self):
        self.canvas.delete("s")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 10: w, h = 1100, 380
        cx, cy = w/2, h/2
        t = time.time()
        for i in range(130):
            r = 10 + (i * 2.8)
            angle = t * (0.015 + i*0.0002) + i
            x, y = cx + r * 2.0 * math.cos(angle), cy + r * math.sin(angle)
            self.canvas.create_oval(x, y, x+1.5, y+1.5, fill=random.choice([self.C_GOLD, "white", "#333"]), outline="", tags="s")
        self.master.after(40, self.animate_stars)

if __name__ == "__main__":
    root = tk.Tk()
    app = OracleSystem(root)
    root.mainloop()