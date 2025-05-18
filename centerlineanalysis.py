import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# Parametri fluido in condizioni standard
rho = 1.225  # kg/m^3
mu = 1.81e-5  # Pa·s
ni = mu / rho

# --- SELEZIONE DELLA LUNGHEZZA BAGNATA DAL MODELLO BLENDER ---

print("\nScegli la porzione da analizzare:")
print("1 - Dorso")
print("2 - Ventre")
scelta = input("Inserisci 1 o 2: ").strip()

if scelta == "1":
    path = "lunghezza_dorso.txt"
elif scelta == "2":
    path = "lunghezza_ventre.txt"
else:
    print("Scelta non valida. Uso lunghezza totale.")
    path = "centerline_length.txt"  # fallback se presente

with open(path, "r") as f:
    L = float(f.read())
print(f"\n✅ Lunghezza selezionata dal file '{path}': {L:.3f} m")


# Input da tastiera
Ra = float(input("Inserisci la rugosità media superficiale Ra (in micrometri): "))
user_trans_perc = float(input("Inserisci la percentuale di transizione da evidenziare (es. 30 per 30%): "))

# Calcolo delta (fattore correttivo) in base a Ra
if Ra <= 0.1:
    delta = 1.1
elif 0.1 < Ra <= 1:
    delta = 1.3
elif 1 < Ra <= 5:
    delta = 1.7
else:
    delta = 2.2

# Funzione per calcolare l'origine virtuale dello strato limite turbolento
def calculate_virtual_origin(Re_tr, Re_L, L, ni):
    x_T = (Re_tr * ni) / (Re_L * ni / L)
    vel = Re_L * ni / L

    delta_lam = 5 * x_T / np.sqrt(Re_tr)

    def equation(x0):
        dx = x_T - x0
        if dx <= 0:
            return np.inf
        Re_T0 = vel * dx / ni
        delta_turb = 0.37 * dx / (Re_T0**0.2)
        return delta_turb - delta_lam

    x0_guess = x_T * 0.5
    x0 = fsolve(equation, x0_guess)[0]

    return max(0, x0)

# Funzioni da richiamare per il calcolo dei coefficienti di attrito
def cf_lam(Re): return 1.32 / np.sqrt(Re)
def cf_turb(Re): return 0.072 / Re**0.2

# Intervallo logaritmi di Reynolds da mettere sulle ascisse
Re_L_values = np.logspace(5, 8, 300)
transizioni = [0.1] + list(np.round(np.linspace(0.2, 0.9, 8), 2))

plt.figure(figsize=(10, 6))
output_file = open("risultati_completi.txt", "w")

# Calcolo curve
for trans_perc in [0.0] + list(transizioni) + [1.0]:
    CF_curve = []
    valid_Re = []

    for Re_L in Re_L_values:
        try:
            if trans_perc == 0.0:
                cf = cf_lam(Re_L)
                friction = 0.5 * rho * (Re_L * ni / L)**2 * cf * L * (1 + delta)
            elif trans_perc == 1.0:
                x0 = calculate_virtual_origin(1e5, Re_L, L, ni)
                Re_virtual = rho * (Re_L * ni / L) * (L - x0) / mu
                cf = cf_turb(Re_virtual)
                friction = 0.5 * rho * (Re_L * ni / L)**2 * cf * L * (1 + delta)
            else:
                Re_tr = Re_L * trans_perc
                cf_l = cf_lam(Re_tr)

                x0 = calculate_virtual_origin(Re_tr, Re_L, L, ni)
                Re_virtual_turb = rho * (Re_L * ni / L) * (L * (1 - trans_perc)) / mu
                cf_t = cf_turb(Re_virtual_turb)
                cf = cf_l * trans_perc + cf_t * (1 - trans_perc)

                xt = L * trans_perc
                friction_lam = 0.5 * rho * (Re_L * ni / L)**2 * cf_l * xt * (1 + delta)
                friction_turb = 0.5 * rho * (Re_L * ni / L)**2 * cf_t * (L - xt) * (1 + delta)
                friction = friction_lam + friction_turb

            if np.isfinite(cf) and cf > 0:
                valid_Re.append(np.log10(Re_L))
                CF_curve.append(cf)
                if not np.isclose(trans_perc, user_trans_perc / 100.0, atol=0.01):
                    if trans_perc == 0.0:
                        output_file.write(f"[FLUSSO 100% LAMINARE] Re_L = {Re_L:.2e}, Cf = {cf:.5f}, Friction = {friction:.5f} N\n")
                    elif trans_perc == 1.0:
                        output_file.write(f"[FLUSSO 100% TURBOLENTO] Re_L = {Re_L:.2e}, Cf = {cf:.5f}, Friction = {friction:.5f} N\n")
                    else:
                        output_file.write(f"[x_t/L = {trans_perc:.2f}] Re_L = {Re_L:.2e}, Cf = {cf:.5f}, Friction = {friction:.5f} N\n")

        except Exception:
            continue

    # Stampa risultati per la curva selezionata
    if np.isclose(trans_perc, user_trans_perc / 100.0, atol=0.01):
        print(f"\n--- Risultati per transizione {user_trans_perc:.0f}% ---")
        for re_val, cf_val in zip(valid_Re, CF_curve):
            print(f"log10(Re_L) = {re_val:.2f}, Cf = {cf_val:.5f}")

    label = f"{int(trans_perc * 100)}%"
    color = 'red' if np.isclose(trans_perc, user_trans_perc / 100.0, atol=0.01) else None
    lw = 2.5 if color == 'red' else 1.2
    plt.plot(valid_Re, CF_curve, label=label, color=color, linewidth=lw)

# Aggiunta input/output per singolo valore di Reynolds
user_Re = float(input("\nInserisci un valore di Reynolds specifico (es. 1e6): "))
trans_perc = user_trans_perc / 100.0

if trans_perc == 0.0:
    cf = cf_lam(user_Re)
    friction = 0.5 * rho * (user_Re * ni / L)**2 * cf * L * (1 + delta)
    print(f"\n[FLUSSO 100% LAMINARE] Re_L = {user_Re:.2e}, Cf = {cf:.5f}, Friction = {friction:.2f} N")
elif trans_perc == 1.0:
    x0 = calculate_virtual_origin(1e5, user_Re, L, ni)
    Re_virtual = rho * (user_Re * ni / L) * (L - x0) / mu
    cf = cf_turb(Re_virtual)
    friction = 0.5 * rho * (user_Re * ni / L)**2 * cf * L * (1 + delta)
    print(f"\n[FLUSSO 100% TURBOLENTO] Re_L = {user_Re:.2e}, Cf = {cf:.5f}, Friction = {friction:.2f} N")
else:
    Re_tr = user_Re * trans_perc
    cf_l = cf_lam(Re_tr)
    x0 = calculate_virtual_origin(Re_tr, user_Re, L, ni)
    Re_virtual_turb = rho * (user_Re * ni / L) * (L * (1 - trans_perc)) / mu
    cf_t = cf_turb(Re_virtual_turb)
    cf = cf_l * trans_perc + cf_t * (1 - trans_perc)
    xt = L * trans_perc
    friction_lam = 0.5 * rho * (user_Re * ni / L)**2 * cf_l * xt * (1 + delta)
    friction_turb = 0.5 * rho * (user_Re * ni / L)**2 * cf_t * (L - xt) * (1 + delta)
    friction = friction_lam + friction_turb
    print(f"\n[x_t/L = {trans_perc:.2f}] Re_L = {user_Re:.2e}, Cf = {cf:.5f}, Friction = {friction:.5f} N")

output_file.close()

# Grafico finale
plt.xlabel(r'$\log_{10}(Re_L)$', fontsize=12)
plt.ylabel(r'$C_F$', fontsize=12)
plt.title('Distribuzione del coefficiente di attrito Cf con origine virtuale', fontsize=14)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend(title=r"$x_t/L$")
plt.tight_layout()
plt.show()

print("\nSimulazione completata. Dati salvati in 'risultati_completi.txt'")

