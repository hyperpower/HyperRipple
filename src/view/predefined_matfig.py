from matplotlib.figure import Figure


def blank_fig_with_dashed_grid():
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.set_facecolor('none')  # 设置背景透明
    ax.set_aspect('equal')  # 保持宽高比
    ax.set_xlim(0, 100)
    ax.set_ylim(100, 0) # reverse y-axis to match image coordinates  
    fig.tight_layout(pad=1)  # 去除边距
    ax.grid(True, linestyle='--', color='gray', alpha=0.7)  # 添加虚线网格
    return fig