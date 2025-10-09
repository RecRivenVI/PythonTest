import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ----- 参数定义 -----
g = 9.81   # 重力加速度
L1, L2 = 1.0, 1.0   # 摆长
m1, m2 = 1.0, 1.0   # 质量
dt = 0.02           # 时间步长

# 初始角度：两摆差 0.0001 弧度
theta1_1 = np.pi / 2
theta2_1 = np.pi / 2
theta1_2 = theta1_1 + 1e-4
theta2_2 = theta2_1

omega1_1 = omega2_1 = omega1_2 = omega2_2 = 0.0

# ----- 方程定义 -----
def derivs(state):
    theta1, omega1, theta2, omega2 = state
    delta = theta2 - theta1
    den1 = (m1 + m2) * L1 - m2 * L1 * np.cos(delta)**2
    den2 = (L2 / L1) * den1

    domega1 = ((m2 * L1 * omega1**2 * np.sin(delta) * np.cos(delta)
               + m2 * g * np.sin(theta2) * np.cos(delta)
               + m2 * L2 * omega2**2 * np.sin(delta)
               - (m1 + m2) * g * np.sin(theta1)) / den1)

    domega2 = ((-L2 * omega2**2 * np.sin(delta) * np.cos(delta)
               + (m1 + m2) * (g * np.sin(theta1) * np.cos(delta)
               - L1 * omega1**2 * np.sin(delta)
               - g * np.sin(theta2))) / den2)
    return np.array([omega1, domega1, omega2, domega2])

# ----- 模拟函数 -----
def step(state):
    k1 = derivs(state)
    k2 = derivs(state + dt * k1 / 2)
    k3 = derivs(state + dt * k2 / 2)
    k4 = derivs(state + dt * k3)
    return state + dt * (k1 + 2*k2 + 2*k3 + k4) / 6

# ----- 初始化 -----
state1 = np.array([theta1_1, omega1_1, theta2_1, omega2_1])
state2 = np.array([theta1_2, omega1_2, theta2_2, omega2_2])

x1s, y1s, x2s, y2s = [], [], [], []

# ----- 动画绘图 -----
fig, ax = plt.subplots()
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.2, 2.2)
ax.set_aspect('equal')
ax.set_title("混沌双摆模拟（初始角度差 0.0001°）")

line1, = ax.plot([], [], 'o-', lw=2, color='blue', label="摆 A")
line2, = ax.plot([], [], 'o-', lw=2, color='red', alpha=0.6, label="摆 B")
trace1, = ax.plot([], [], '-', lw=1, color='cyan', alpha=0.5)
trace2, = ax.plot([], [], '-', lw=1, color='orange', alpha=0.5)
ax.legend()

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    trace1.set_data([], [])
    trace2.set_data([], [])
    return line1, line2, trace1, trace2

def update(frame):
    global state1, state2
    state1 = step(state1)
    state2 = step(state2)

    t1a, t2a = state1[0], state1[2]
    t1b, t2b = state2[0], state2[2]

    x1a, y1a = L1 * np.sin(t1a), -L1 * np.cos(t1a)
    x2a, y2a = x1a + L2 * np.sin(t2a), y1a - L2 * np.cos(t2a)

    x1b, y1b = L1 * np.sin(t1b), -L1 * np.cos(t1b)
    x2b, y2b = x1b + L2 * np.sin(t2b), y1b - L2 * np.cos(t2b)

    x1s.append(x2a)
    y1s.append(y2a)
    x2s.append(x2b)
    y2s.append(y2b)

    line1.set_data([0, x1a, x2a], [0, y1a, y2a])
    line2.set_data([0, x1b, x2b], [0, y1b, y2b])
    trace1.set_data(x1s, y1s)
    trace2.set_data(x2s, y2s)
    return line1, line2, trace1, trace2

ani = FuncAnimation(fig, update, init_func=init, frames=1000, interval=20, blit=True)
plt.show()
