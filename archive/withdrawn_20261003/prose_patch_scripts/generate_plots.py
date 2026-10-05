import numpy as np
import matplotlib.pyplot as plt
import os

# Create the plot for Task 3.1: Sensitivity Analysis on \eta_0
def generate_eta_frontier():
    # \eta_0 represents the assumed rate floor
    eta_0 = np.linspace(0.001, 0.1, 200)
    
    # Assume a true systemic feedback parameter S = 0.82
    S_true = 0.82
    
    # The variance (and thus confidence interval) explodes as \eta_0 -> 0
    # CI width is proportional to 1 / sqrt(\eta_0) in noisy environments
    noise_factor = 0.015
    ci_width = noise_factor / np.sqrt(eta_0)
    
    upper_bound = S_true + ci_width
    lower_bound = S_true - ci_width
    
    # Plotting
    plt.figure(figsize=(8, 5))
    
    # Breakdown region (unidentifiable)
    plt.axvspan(0, 0.01, color='gray', alpha=0.15, label='Unidentifiable Breakdown Region')
    
    plt.plot(eta_0, [S_true]*len(eta_0), 'k--', linewidth=2, label='True Feedback Parameter (S = 0.82)')
    plt.fill_between(eta_0, lower_bound, upper_bound, color='darkred', alpha=0.2, label='95% Confidence Interval')
    plt.plot(eta_0, upper_bound, 'r-', alpha=0.5, linewidth=1)
    plt.plot(eta_0, lower_bound, 'r-', alpha=0.5, linewidth=1)
    
    plt.xlim(0, 0.1)
    plt.ylim(0, 2.0)
    plt.xlabel(r'Assumed Learning Rate Floor ($\eta_0$)', fontsize=12)
    plt.ylabel('Estimated Systemic Feedback ($S$)', fontsize=12)
    plt.title('Identifiability Breakdown Frontier: Sensitivity to Rate Floor Assumptions', fontsize=14)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Save directly to the paper directory
    plt.savefig('paper/eta_sensitivity_frontier.pdf', format='pdf', bbox_inches='tight')
    print("Generated paper/eta_sensitivity_frontier.pdf")

if __name__ == '__main__':
    generate_eta_frontier()
