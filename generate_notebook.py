import nbformat as nbf
import textwrap

nb = nbf.v4.new_notebook()

cells = [
    nbf.v4.new_markdown_cell("# 📊 Курсовой проект: Симулятор газового промысла\n*Дисциплина: Алгоритмизация и программирование*\n\nНиже представлен полный анализ системы: PVT, IPR/VLP, рабочая точка, динамика добычи, анализ ДКС и калибровка."),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from scipy.optimize import fsolve, minimize
    from src.fluid import Fluid
    from src.reservoir import ResProps, Reservoir
    from src.pipe import Pipe
    from src.well import Well
    from src.compressor import DCS
    from src.simulator import FieldSimulator
    import warnings; warnings.filterwarnings('ignore')
    plt.style.use('seaborn-v0_8-whitegrid')
    %matplotlib inline
    """)),
    nbf.v4.new_markdown_cell("### 🧪 1. PVT-модель флюида\nРасчёт Z-фактора, плотности, вязкости и фактора объёма газа."),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    # Параметры флюида (типовые)
    M, rho_c, xa, xy, T_fluid = 17.5, 160.0, 0.90, 0.10, 310.0
    fluid = Fluid(M, rho_c, xa, xy, T_fluid)

    P_range = np.linspace(1, 200, 50)
    Z_vals = [fluid.z(p) for p in P_range]
    bg_vals = [fluid.bg(p) for p in P_range]
    mu_vals = [fluid.mu(p) for p in P_range]
    rho_real = [fluid.ro(p) for p in P_range]
    rho_ideal = [(p*101325*(M/1000))/(8.314*T_fluid) for p in P_range]

    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs[0,0].plot(P_range, Z_vals, 'b-', lw=2); axs[0,0].set_ylabel('Z-фактор'); axs[0,0].set_xlabel('P [атм]')
    axs[0,1].plot(P_range, rho_real, 'r-', label='Real', lw=2)
    axs[0,1].plot(P_range, rho_ideal, 'k--', label='Ideal', lw=1.5)
    axs[0,1].set_ylabel('ρ [кг/м³]'); axs[0,1].set_xlabel('P [атм]'); axs[0,1].legend()
    axs[1,0].plot(P_range, bg_vals, 'g-', lw=2); axs[1,0].set_ylabel('B_g [м³/м³]'); axs[1,0].set_xlabel('P [атм]')
    axs[1,1].plot(P_range, mu_vals, 'm-', lw=2); axs[1,1].set_ylabel('μ [сП]'); axs[1,1].set_xlabel('P [атм]')
    plt.tight_layout(); plt.show()
    """)),
    nbf.v4.new_markdown_cell("### 🕳️ 2. Модель пласта и скважин (IPR & VLP)\nКривая притока (IPR) и кривая подъёма (VLP) для скважины №1."),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    # Параметры скважины 1 (типовые)
    k, h, re, rw = 50, 25, 500, 0.1
    L_tub, D_tub, H_tub, rough = 2000, 0.062, 1800, 0.000046
    tub1 = Pipe(L_tub, D_tub, rough, fluid, H_tub)
    w1 = Well(fluid, k, h, re, rw, tub1)

    P_res = 100
    P_bhp = np.linspace(1, P_res, 50)
    q_ipr = [w1.q(P_res, p) for p in P_bhp]
    q_vlp = []
    for p in P_bhp:
        st = tub1.dp(p, 10) # dummy q for plot
        q_vlp.append(st.q_std) # placeholder for visual

    # Корректная VLP: обратный перебор по дебиту
    q_test = np.linspace(10, 2000, 100)
    pwh_vlp = []
    for q in q_test:
        st = tub1.dp(P_res, q) # approx
        pwh_vlp.append(max(st.P_out, 1))

    plt.figure(figsize=(8,5))
    plt.plot(q_ipr, P_bhp, 'b-', label='IPR (Inflow)', lw=2)
    plt.plot(q_test, pwh_vlp, 'r--', label='VLP (Outflow)', lw=2)
    plt.xlabel('Debit [ст.м³/сут]'); plt.ylabel('Pressure [атм]')
    plt.title('IPR vs VLP (Well 1)'); plt.legend(); plt.grid(True); plt.show()
    """)),
    nbf.v4.new_markdown_cell("### 🎯 3. Рабочая точка системы\nРешение системы нелинейных уравнений для баланса давлений и дебитов."),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    P_res_init, V_res = 100, 1e6
    res = Reservoir(ResProps(P_res_init, V_res, T_fluid), fluid)

    shlyf = Pipe(5000, 0.200, 0.000046, fluid, 0.0)
    dcs = DCS(1.5, 5.0, 500.0)
    wells = [w1, w1, w1] # Using w1 for all 3 as per typical setup

    sim = FieldSimulator(res, wells, shlyf, dcs)
    states = sim.solve(P_res_init)
    print(f"Рабочая точка при P_res={P_res_init} атм:")
    for k,v in states.items():
        print(f"  {k}: P_in={v.P_in:.1f}, P_out={v.P_out:.1f}, q={v.q_std:.1f}")
    """)),
    nbf.v4.new_markdown_cell("### 📈 4. Динамика разработки (180 суток)\nМоделирование истощения пласта и изменения дебитов во времени."),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    res.resprops.P = P_res_init # reset
    df = sim.run(180, dt=1.0)
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs[0,0].plot(df['t'], df['P_res'], 'b-', lw=2); axs[0,0].set_ylabel('P_res [атм]')
    axs[0,1].plot(df['t'], df['P_man'], 'r-', lw=2); axs[0,1].set_ylabel('P_man [атм]')
    axs[1,0].plot(df['t'], df['q1'], label='Well 1', lw=1.5)
    axs[1,0].plot(df['t'], df['q2'], label='Well 2', lw=1.5)
    axs[1,0].plot(df['t'], df['q3'], label='Well 3', lw=1.5); axs[1,0].legend(); axs[1,0].set_ylabel('q [ст.м³/сут]')
    axs[1,1].plot(df['t'], df['Gp'], 'g-', lw=2); axs[1,1].set_ylabel('Gp [тыс.ст.м³]')
    for ax in axs.flatten(): ax.set_xlabel('Time [days]'); ax.grid(True)
    plt.tight_layout(); plt.show()
    """)),
    nbf.v4.new_markdown_cell("### ⚙️ 5. Влияние степени сжатия ДКС (CR)\nСравнение динамики при CR = 1.0, 1.5, 2.0, 3.0."),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    cr_vals = [1.0, 1.5, 2.0, 3.0]
    plt.figure(figsize=(8,5))
    for cr in cr_vals:
        dcs_test = DCS(cr, 5.0, 500.0)
        res_test = Reservoir(ResProps(P_res_init, V_res, T_fluid), fluid)
        sim_test = FieldSimulator(res_test, wells, shlyf, dcs_test)
        df_test = sim_test.run(180, dt=1.0)
        plt.plot(df_test['t'], df_test['P_res'], label=f'CR={cr}', lw=2)
    plt.xlabel('Time [days]'); plt.ylabel('P_res [атм]'); plt.legend(); plt.grid(True); plt.show()
    """)),
    nbf.v4.new_markdown_cell("### 🔍 6. Калибровка по промысловым данным\nПодбор коэффициента продуктивности под `adapt_gdi_11-2025.csv`. Расчёт RMSE и R²."),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    df_fact = pd.read_csv('adapt_gdi_11-2025.csv')
    q_fact = df_fact[['q1','q2','q3']].values.flatten()
    days_fact = np.arange(len(q_fact))

    def objective(C_mult):
        res_cal = Reservoir(ResProps(P_res_init, V_res, T_fluid), fluid)
        w_cal = [Well(fluid, k*C_mult[0], h, re, rw, tub1),
                 Well(fluid, k*C_mult[1], h, re, rw, tub1),
                 Well(fluid, k*C_mult[2], h, re, rw, tub1)]
        sim_cal = FieldSimulator(res_cal, w_cal, shlyf, DCS(1.5, 5.0, 500.0))
        df_cal = sim_cal.run(max(days_fact)+1, dt=1.0)
        q_sim = df_cal[['q1','q2','q3']].values.flatten()[:len(q_fact)]
        return np.sum((q_fact - q_sim)**2)

    res_opt = minimize(objective, [1.0, 1.0, 1.0], method='Nelder-Mead')
    print(f"Оптимальные множители продуктивности: {res_opt.x}")

    # Final calibrated simulation
    res_fin = Reservoir(ResProps(P_res_init, V_res, T_fluid), fluid)
    w_fin = [Well(fluid, k*res_opt.x[i], h, re, rw, tub1) for i in range(3)]
    sim_fin = FieldSimulator(res_fin, w_fin, shlyf, DCS(1.5, 5.0, 500.0))
    df_fin = sim_fin.run(max(days_fact)+1, dt=1.0)
    q_sim_fin = df_fin[['q1','q2','q3']].values.flatten()[:len(q_fact)]

    rmse = np.sqrt(np.mean((q_fact - q_sim_fin)**2))
    ss_res = np.sum((q_fact - q_sim_fin)**2)
    ss_tot = np.sum((q_fact - np.mean(q_fact))**2)
    r2 = 1 - (ss_res / ss_tot)
    print(f"RMSE: {rmse:.2f}, R²: {r2:.4f}")

    plt.figure(figsize=(8,5))
    plt.plot(q_fact, 'o', label='Факт', alpha=0.7); plt.plot(q_sim_fin, '-', label='Модель', lw=2)
    plt.xlabel('Шаг измерения'); plt.ylabel('Дебит [ст.м³/сут]'); plt.legend(); plt.grid(True); plt.show()
    """))
]

nb['cells'] = cells
with open('курсовая.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("✅ курсовая.ipynb успешно создан!")
