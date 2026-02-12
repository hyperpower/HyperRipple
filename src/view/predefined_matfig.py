from matplotlib.figure import Figure


def blank_fig_with_dashed_grid():
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.set_facecolor('none')  # 设置背景透明
    ax.grid(True, linestyle='--', color='gray', alpha=0.7)  # 添加虚线网格
    return fig