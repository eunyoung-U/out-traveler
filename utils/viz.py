import platform
import matplotlib.pyplot as plt
import seaborn as sns


# 색상 팔레트 (0번은 격자 전용, 1~4번을 그래프 데이터 색상으로 사용)
COLOR_LIST = ["#E6F1FB", "#8FC1E8", "#1B5FA8", "#0C3D6E", "#042C53"]


def set_plot_style():
    # 한글 폰트 + 그래프 테마(배경, 격자, 글자색) 적용
    sns.set_theme(style="whitegrid")

    # 폰트 설정 (운영체제별 한글 폰트)
    font_map = {
        "Darwin": "AppleGothic",     # macOS
        "Windows": "Malgun Gothic",  # Windows
    }
    # Linux 계열(Colab, 로컬 Jupyter 등)은 NanumGothic을 기본값으로 사용
    font_name = font_map.get(platform.system(), "NanumGothic")
    plt.rcParams["font.family"] = font_name
    plt.rcParams["axes.unicode_minus"] = False  # 음수 기호(-) 깨짐 방지

    # --- 배경/격자 설정 ---
    plt.rcParams["figure.facecolor"] = "white"  # figure 배경
    plt.rcParams["axes.facecolor"] = "white"    # axes 배경
    plt.rcParams["grid.color"] = COLOR_LIST[0]  # 격자선 색상만 COLOR_LIST 사용

    # --- 텍스트/축 색상 ---
    plt.rcParams["axes.labelcolor"] = COLOR_LIST[4]
    plt.rcParams["text.color"] = COLOR_LIST[4]
    plt.rcParams["xtick.color"] = COLOR_LIST[4]
    plt.rcParams["ytick.color"] = COLOR_LIST[4]


def get_palette(n=2):
    # 데이터 시각화용 팔레트 반환
    return COLOR_LIST[1:n + 1]
