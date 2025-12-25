import streamlit as st
import random
from typing import List, Dict

# 保留你原有的 WordItem 类（完全不变）
class WordItem:
    """单词数据类"""
    def __init__(self, text: str):
        self.text = text
        self.total_count = 0  # 总共出现次数
        self.last_seen_round = 0  # 上次出现的轮次
        self.visible = True  # 当前是否可见
        
    def to_dict(self):
        return {
            "text": self.text,
            "total_count": self.total_count,
            "last_seen": self.last_seen_round,
            "visible": self.visible
        }

# 简化 WordDisplay 为 Streamlit 兼容版本（保留随机样式）
class WordDisplay:
    def __init__(self, word: WordItem):
        self.word = word
        self.size = random.randint(30, 60)
        self.color = self._random_color()
        self.rotation = random.uniform(-15, 15)
        
    def _random_color(self):
        colors = [
            "#1e88e5", "#2e7d32", "#d32f2f",
            "#7b1fa2", "#f57c00", "#00897b",
            "#c2185b", "#3949ab", "#5d4037"
        ]
        return random.choice(colors)

# 保留你原有的核心算法（新增清除功能相关逻辑）
class VocabularyApp:
    def __init__(self):
        self.words: List[WordItem] = []
        self.current_round = 0
        self.max_display = 15
        self.word_displays: List[WordDisplay] = []
        
        # Streamlit 状态管理（临时保存，关闭页面丢失，符合你的需求）
        if "words" not in st.session_state:
            st.session_state.words = []
        if "current_round" not in st.session_state:
            st.session_state.current_round = 0
        self.words = st.session_state.words
        self.current_round = st.session_state.current_round

    def add_word(self, text: str):
        if not text.strip():
            return
        new_word = WordItem(text.strip())
        self.words.append(new_word)
        self.current_round += 1
        self._update_visibility()
        # 保存到 session_state
        st.session_state.words = self.words
        st.session_state.current_round = self.current_round

    def refresh_layout(self):
        self.current_round += 1
        self._update_visibility()
        st.session_state.current_round = self.current_round

    def clear_all_words(self):
        """一键清除所有单词"""
        self.words = []
        self.current_round = 0
        # 清空 session_state
        st.session_state.words = []
        st.session_state.current_round = 0

    def _update_visibility(self):
        # 完全保留你原有的算法逻辑
        if len(self.words) <= self.max_display:
            for word in self.words:
                word.visible = True
                if word.visible:
                    word.total_count += 1
                    word.last_seen_round = self.current_round
            return
        
        sorted_words = sorted(self.words, key=lambda x: x.total_count)
        for i, word in enumerate(sorted_words):
            if i < self.max_display:
                word.visible = True
                word.total_count += 1
                word.last_seen_round = self.current_round
            else:
                rounds_since_last = self.current_round - word.last_seen_round
                if word.total_count <= 5 and rounds_since_last >= 2:
                    word.visible = True
                elif word.total_count <= 10 and rounds_since_last >= 3:
                    word.visible = True
                elif word.total_count > 10 and rounds_since_last >= 5:
                    word.visible = True
                else:
                    word.visible = False
                if word.visible:
                    word.total_count += 1
                    word.last_seen_round = self.current_round

    def get_visible_word_displays(self):
        visible_words = [w for w in self.words if w.visible]
        return [WordDisplay(word) for word in visible_words]

# Streamlit UI 渲染（修复清除按钮样式，兼容所有版本）
def main():
    st.set_page_config(page_title="A4纸背单词", layout="wide")
    app = VocabularyApp()

    # 顶部输入区域
    st.title("A4纸背单词")
    # 调整布局：输入框+添加按钮+清除按钮
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        word_input = st.text_input("输入新单词", placeholder="输入英文单词后按回车", label_visibility="collapsed")
    with col2:
        add_btn = st.button("添加并刷新", type="primary")
    with col3:
        # 修复：用 markdown 自定义红色清除按钮，兼容所有 Streamlit 版本
        # 隐藏原生按钮，通过 markdown 触发点击事件
        clear_btn_clicked = st.button("一键清除所有单词", type="secondary")
        # 自定义按钮样式（覆盖原生样式）
        st.markdown("""
            <style>
            div[data-testid="stButton"] > button:last-child {
                background-color: #d32f2f;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 0.5rem 1rem;
                width: 100%;
            }
            div[data-testid="stButton"] > button:last-child:hover {
                background-color: #b71c1c;
                cursor: pointer;
            }
            </style>
        """, unsafe_allow_html=True)

    # 添加单词逻辑
    if add_btn or (word_input and st.session_state.get("last_input") != word_input):
        if word_input:
            app.add_word(word_input)
            st.session_state.last_input = word_input

    # 清除单词逻辑
    if clear_btn_clicked:
        app.clear_all_words()
        # 清除输入框缓存
        st.session_state.last_input = ""
        # 刷新页面（可选，让效果更直观）
        st.rerun()

    # 刷新按钮
    if st.button("手动刷新布局"):
        app.refresh_layout()
        st.rerun()

    # 统计信息
    total = len(app.words)
    visible = len([w for w in app.words if w.visible])
    hidden = total - visible
    st.caption(f"总单词数: {total} | 显示: {visible} | 隐藏: {hidden}")

    # 单词显示区域（模拟随机布局，保留你的核心样式）
    word_displays = app.get_visible_word_displays()
    if word_displays:
        # 用列布局模拟随机位置，同时保留字体大小、颜色、旋转
        cols = st.columns(5)
        for i, display in enumerate(word_displays):
            with cols[i % 5]:
                st.markdown(
                    f"""
                    <div style="
                        font-size: {display.size}px;
                        color: {display.color};
                        transform: rotate({display.rotation}deg);
                        margin: 20px;
                        text-align: center;
                        font-weight: bold;
                    ">
                        {display.word.text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()