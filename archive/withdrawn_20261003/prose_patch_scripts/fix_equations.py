import re

def fix_latex_equations(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Fix line 1089
    eq1_old = r'''\begin{equation}
 m_{i,t+1}=(1-\eta_i)m_{i,t}+\eta_i x_t,\qquad
 x_{t+1}=a x_t+\sum_i q_i m_{i,t}+\lambda u_t+w_{t+1},
 \label{eq:audited_recursion}
\end{equation}'''
    eq1_new = r'''\begin{align}
 m_{i,t+1} &= (1-\eta_i)m_{i,t}+\eta_i x_t, \nonumber\\
 x_{t+1} &= a x_t+\sum_i q_i m_{i,t}+\lambda u_t+w_{t+1},
 \label{eq:audited_recursion}
\end{align}'''
    content = content.replace(eq1_old, eq1_new)

    # Fix line 1132
    eq2_old = r'''\begin{equation}
 Y_j=x_{j,T_j},\qquad
 X_j=(1,x_{j,T_j-1},m_{j,1,T_j-1},\ldots,m_{j,d,T_j-1}),
 \quad Y_j=X_j\beta+w_{j,T_j},
 \label{eq:terminal_regression}
\end{equation}'''
    eq2_new = r'''\begin{align}
 Y_j &= x_{j,T_j}, \nonumber\\
 X_j &= (1,x_{j,T_j-1},m_{j,1,T_j-1},\ldots,m_{j,d,T_j-1}), \nonumber\\
 Y_j &= X_j\beta+w_{j,T_j},
 \label{eq:terminal_regression}
\end{align}'''
    content = content.replace(eq2_old, eq2_new)

    # Fix line 1371
    eq3_old = r'''\[
 x_{t+1}=(1-\kappa\phi)x_t+q_f y_{f,t}+q_s y_{s,t}+\kappa\varepsilon_t,
 \qquad y_{i,t+1}=(1-\eta_i)y_{i,t}+\eta_i x_{t+1}.
\]'''
    eq3_new = r'''\begin{align*}
 x_{t+1} &= (1-\kappa\phi)x_t+q_f y_{f,t}+q_s y_{s,t}+\kappa\varepsilon_t, \\
 y_{i,t+1} &= (1-\eta_i)y_{i,t}+\eta_i x_{t+1}.
\end{align*}'''
    content = content.replace(eq3_old, eq3_new)

    # Fix line 1997
    eq4_old = r''' &=\left((z-a)-(-\mathbf1_n^\top)\left((z-1+\eta)I_n\right)^{-1}(-\eta q)\right)^{-1}\\'''
    eq4_new = r''' &=\left((z-a)-(-\mathbf1_n^\top)\frac{(-\eta q)}{z-1+\eta}\right)^{-1}\\'''
    content = content.replace(eq4_old, eq4_new)

    # Fix line 2028
    eq5_old = r''' J v &= \begin{bmatrix} a & \mathbf{1}_n^\top \\ \eta q & (1-\eta)I_n \end{bmatrix} \begin{bmatrix} 0 \\ w \end{bmatrix} = \begin{bmatrix} \mathbf{1}_n^\top w \\ (1-\eta)w \end{bmatrix} = \begin{bmatrix} 0 \\ (1-\eta)w \end{bmatrix} = (1-\eta) v.'''
    eq5_new = r''' J v &= \begin{bmatrix} a & \mathbf{1}_n^\top \\ \eta q & (1-\eta)I_n \end{bmatrix} \begin{bmatrix} 0 \\ w \end{bmatrix} \nonumber\\
 &= \begin{bmatrix} \mathbf{1}_n^\top w \\ (1-\eta)w \end{bmatrix} = \begin{bmatrix} 0 \\ (1-\eta)w \end{bmatrix} = (1-\eta) v.'''
    content = content.replace(eq5_old, eq5_new)

    with open(filepath, 'w') as f:
        f.write(content)

fix_latex_equations('paper/Machine_Markets_Final_Integrated_Paper.tex')
