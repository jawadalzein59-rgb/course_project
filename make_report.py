import nbformat as nbf, textwrap
nb = nbf.v4.new_notebook()
nb['cells'] = [
    nbf.v4.new_markdown_cell("# 📊 Gas Field Simulator - Final Report"),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    import numpy as np, pandas as pd, matplotlib.pyplot as plt
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
    nbf.v4.new_markdown_cell("### 1. PVT Properties"),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    M, rho_c, xa, xy, T = 17.5, 160.0, 0.90, 0.10, 310.0
    fluid = Fluid(M, rho_c, xa, xy, T)
    P = np.linspace(1, 200, 50)
    plt.figure(figsize=(9,3))
    plt.subplot(131); plt.plot(P, [fluid.z(p) for p in P]); plt.ylabel('Z'); plt.xlabel('P [atm]')
    plt.subplot(132); plt.plot(P, [fluid.ro(p) for p in P]); plt.ylabel('rho'); plt.xlabel('P')
    plt.subplot(133); plt.plot(P, [fluid.mu(p) for p in P]); plt.ylabel('mu'); plt.xlabel('P')
    plt.tight_layout(); plt.show()
    """)),
    nbf.v4.new_markdown_cell("### 2. Simulation & Dynamics (180 days)"),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    res = Reservoir(ResProps(100, 1e6, 310.0), fluid)
    shlyf = Pipe(5000, 0.200, 0.000046, fluid, 0.0)
    dcs = DCS(1.5, 5.0, 500.0)
    wells = [Well(fluid, 50, 25, 500, 0.1, Pipe(L, 0.062, 0.000046, fluid, H)) 
             for L, H in [(2000,1800),(2500,1900),(1800,1600)]]
    sim = FieldSimulator(res, wells, shlyf, dcs)
    df = sim.run(180, dt=1.0)
    fig, ax = plt.subplots(2, 2, figsize=(9,6))
    ax[0,0].plot(df['t'], df['P_res'], 'b-'); ax[0,0].set_ylabel('P_res')
    ax[0,1].plot(df['t'], df['P_man'], 'r-'); ax[0,1].set_ylabel('P_man')
    ax[1,0].plot(df['t'], df[['q1','q2','q3']]); ax[1,0].set_ylabel('q')
    ax[1,1].plot(df['t'], df['Gp'], 'g-'); ax[1,1].set_ylabel('Gp')
    for a in ax.flatten(): a.set_xlabel('Days'); a.grid(True)
    plt.tight_layout(); plt.show()
    """)),
    nbf.v4.new_markdown_cell("### 3. Calibration Metrics"),
    nbf.v4.new_code_cell(textwrap.dedent("""\
    df_f = pd.read_csv('adapt_gdi_11-2025.csv')
    q_f = df_f[['q1','q2','q3']].values.flatten()
    def obj(C):
        r = Reservoir(ResProps(100, 1e6, 310.0), fluid)
        w = [Well(fluid, 50*C[i], 25, 500, 0.1, Pipe(2000, 0.062, 0.000046, fluid, 1800)) for i in range(3)]
        s = FieldSimulator(r, w, shlyf, DCS(1.5, 5.0, 500.0))
        q_s = s.run(len(q_f))[['q1','q2','q3']].values.flatten()
        return np.sum((q_f - q_s)**2)
    opt = minimize(obj, [1,1,1], method='Nelder-Mead')
    q_sim = FieldSimulator(Reservoir(ResProps(100, 1e6, 310.0), fluid),
                          [Well(fluid, 50*opt.x[i], 25, 500, 0.1, Pipe(2000, 0.062, 0.000046, fluid, 1800)) for i in range(3)],
                          shlyf, DCS(1.5, 5.0, 500.0)).run(len(q_f))[['q1','q2','q3']].values.flatten()
    rmse = np.sqrt(np.mean((q_f-q_sim)**2))
    r2 = 1 - np.sum((q_f-q_sim)**2)/np.sum((q_f-np.mean(q_f))**2)
    print(f"RMSE: {rmse:.1f}, R2: {r2:.4f}")
    plt.plot(q_f, 'o', label='Fact'); plt.plot(q_sim, '-', label='Model'); plt.legend(); plt.grid(); plt.show()
    """))
]
with open('course_report.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("✅ course_report.ipynb created")
