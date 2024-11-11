import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# 读取 CSV 文件
df = pd.read_csv('screenshots_info.csv', encoding='utf-8-sig')
df['截图时间'] = pd.to_datetime(df['截图时间'])  # 修改为对应截图时间的列

# 设备颜色映射
colors = {
    '自己': 'lightblue',   # 自己的颜色
    '老妈': 'darkgreen'    # 老妈的颜色
}

# 初始化 Dash 应用
app = Dash(__name__)

# 创建应用布局
app.layout = html.Div([
    html.H1("截图时间轴"),  # 修改标题为“截图时间轴”

    # 用户选择显示选项
    dcc.RadioItems(
        id='user-selection',
        options=[
            {'label': '自己', 'value': '自己'},
            {'label': '老妈', 'value': '老妈'},
            {'label': '全部', 'value': '全部'}
        ],
        value='全部',  # 默认显示全部
        labelStyle={'display': 'inline-block'}
    ),

    # 选择合并或分离显示
    dcc.RadioItems(
        id='merge-selection',
        options=[
            {'label': '合并所有设备', 'value': 'merge'},
            {'label': '分离显示设备', 'value': 'separate'}
        ],
        value='separate',  # 默认分离显示设备
        labelStyle={'display': 'inline-block'}
    ),

    # 选择 hover 模式
    dcc.RadioItems(
        id='hover-mode',
        options=[
            {'label': 'x', 'value': 'x'},
            {'label': 'x unified', 'value': 'x unified'},
            {'label': 'closest', 'value': 'closest'}
        ],
        value='closest',  # 默认 hover 模式设置为 closest
        labelStyle={'display': 'inline-block'}
    ),

    # 用于绘制图表的区域
    dcc.Graph(id='timeline-graph', style={'height': '80vh'})  # 设置初始高度为 80vh
])

@app.callback(
    Output('timeline-graph', 'figure'),
    Input('user-selection', 'value'),
    Input('merge-selection', 'value'),
    Input('hover-mode', 'value')
)
def update_graph(selected_user, merge_option, hover_mode):
    # 根据用户选择过滤数据
    if selected_user != '全部':
        filtered_df = df[df['用户'] == selected_user]
    else:
        filtered_df = df

    # 创建 Plotly 图表
    fig = go.Figure()

    # 获取所有独特的用户和设备
    unique_devices = filtered_df[['用户', '设备型号']].drop_duplicates()

    # 计算设备数量
    num_devices = len(unique_devices)

    # 统一的 y 位置间隔
    y_positions = list(range(num_devices))

    # 创建一个设备标签到 y 位置的映射
    device_map = {f"{row[0]} - {row[1]}": y for y, row in zip(y_positions, unique_devices.itertuples(index=False, name=None))}

    # 绘制点
    if merge_option == 'merge':
        # 合并所有设备的点
        for user, user_df in filtered_df.groupby('用户'):
            fig.add_trace(go.Scattergl(
                x=user_df['截图时间'],  # 修改为截图时间
                y=[0] * len(user_df),  # 所有点在 y=0 上
                mode='markers',
                name=user,
                marker=dict(size=10, color=colors[user]),  # 根据用户选择颜色
                text=[f"{row['用户']} - {row['设备型号']}<br>文件名称: {row['文件名称']}" for _, row in user_df.iterrows()],  # 修改为显示文件名称
                hovertemplate=( 
                    '<b>%{text}</b><br><br>' +
                    '截图时间: %{x|%Y-%m-%d %H:%M:%S}<br>' +
                    '<extra></extra>'
                )
            ))
    else:
        # 分离显示设备
        for user, user_df in filtered_df.groupby('用户'):
            for device, device_df in user_df.groupby('设备型号'):
                fig.add_trace(go.Scattergl(
                    x=device_df['截图时间'],  # 修改为截图时间
                    y=[device_map[f"{user} - {device}"]] * len(device_df),  # 根据设备的 y 位置
                    mode='markers',
                    name=f"{user} - {device}",
                    marker=dict(size=10, color=colors[user]),  # 根据用户选择颜色
                    text=[f"{row['用户']} - {row['设备型号']}<br>文件名称: {row['文件名称']}" for _, row in device_df.iterrows()],  # 修改为显示文件名称
                    hovertemplate=( 
                        '<b>%{text}</b><br><br>' +
                        '截图时间: %{x|%Y-%m-%d %H:%M:%S}<br>' +
                        '设备: %{y}<br>' +
                        '<extra></extra>'
                    )
                ))

    # 设置 x 轴格式
    fig.update_xaxes(
        title_text='截图时间',  # 修改 x 轴标题
        tickformat='%Y-%m',
        ticklabelmode="period",
        dtick='M1',
        ticklen=10,
        tickangle=-45,
        showgrid=True,
        gridcolor='lightgray'
    )

    # 设置 y 轴
    yticks = list(device_map.values())
    yticklabels = list(device_map.keys())
    fig.update_yaxes(
        title_text='设备',
        tickvals=yticks,
        ticktext=yticklabels,
        showgrid=True,
        gridcolor='lightgray'
    )

    # 添加标题，设置 hover 模式
    fig.update_layout(
        title='截图时间轴',  # 修改标题
        hovermode=hover_mode,  # 在这里设置 hovermode
        xaxis_showgrid=True,
        yaxis_showgrid=True,
        legend_title_text='用户',
        plot_bgcolor='white'
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
