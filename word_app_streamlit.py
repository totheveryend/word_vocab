import streamlit as st
import random
from typing import List

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

class VocabularyApp:
    def __init__(self):
        self.words: List[WordItem] = []
        self.current_round = 0
        self.max_display = 15
        
        # 初始化session_state（仅非小部件状态，避免冲突）
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
        st.session_state.words = self.words
        st.session_state.current_round = self.current_round

    def refresh_layout(self):
        self.current_round += 1
        self._update_visibility()
        st.session_state.current_round = self.current_round

    def clear_all_words(self):
        self.words = []
        self.current_round = 0
        st.session_state.words = []
        st.session_state.current_round = 0

    def _update_visibility(self):
        if len(self.words) <= self.max_display:
            for word in self.words:
                word.visible = True
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
        # 打乱顺序，确保显示位置随机变化
        random.shuffle(visible_words)
        # 重新生成随机样式，避免样式固定
        return [WordDisplay(word) for word in visible_words]

def main():
    st.set_page_config(page_title="A4纸背单词", layout="wide")
    app = VocabularyApp()

    # 顶部输入区域
    st.title("A4纸背单词")
    col1, col2, col3 = st.columns([4, 1, 1])
    
    # 核心修复：输入框清空方案（不修改小部件绑定状态，无报错）
    with col1:
        # 方案：使用按钮触发添加后，输入框通过「重新渲染」清空（无状态冲突）
        word_input = st.text_input(
            "输入新单词", 
            placeholder="输入英文单词后点击添加",
            label_visibility="collapsed"
        )
    
    with col2:
        add_btn = st.button("添加并刷新", type="primary")
    with col3:
        clear_btn_clicked = st.button("一键清除所有单词", type="secondary")
        # 自定义红色按钮样式
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
            }
            </style>
        """, unsafe_allow_html=True)

    # 1. 添加单词逻辑（解决输入框清空，无状态报错）
    if add_btn and word_input.strip():
        # 执行添加操作
        app.add_word(word_input.strip())
        # 关键：通过「跳转自身」实现输入框清空（无状态冲突，兼容高版本）
        # 利用 Streamlit 按钮点击后重新渲染页面，输入框恢复默认空值
        st.rerun()  # 高版本 Streamlit 支持，无废弃警告

    # 2. 清除所有单词逻辑
    if clear_btn_clicked:
        app.clear_all_words()
        st.rerun()

    # 3. 手动刷新布局逻辑
    refresh_btn = st.button("手动刷新布局")
    if refresh_btn:
        app.refresh_layout()
        st.rerun()

    # 统计信息
    total = len(app.words)
    visible = len([w for w in app.words if w.visible])
    hidden = total - visible
    st.caption(f"总单词数: {total} | 显示: {visible} | 隐藏: {hidden}")

    # 4. 单词显示区域（核心修复：保留完整单词，不换行、不省略，适配iPad）
    word_displays = app.get_visible_word_displays()
    if word_displays:
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
                        white-space: nowrap; /* 核心：禁止文本自动换行（必须保留） */
                        min-width: 150px; /* 优化：加大最小宽度，适配长单词，避免挤压 */
                        padding: 0 10px; /* 优化：左右内边距，让单词更舒展 */
                    ">
                        {display.word.text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()