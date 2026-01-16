""" Global Parameters File"""

# simulation
uranium_start = 350
neutrons_start = 10

bounding_parameter = 13
fission_prob_hardcoded_parameter = 0.1
threshold_factor_uranium = 0.01

simulation_speed = 5*10**-8  # smaller -> more precise (+ latency)
interaction_cooldown_parameter = simulation_speed * 100 # parameter for how long a particle has to wait until it can interact again. debuggung purposes only

radius_multiplicator = 10**10   # same effect as "pressing" everything tighter together
speed_magnitude_new_products = 1.5 * 10**6
neutron_speed_magnitude = 10 ** 7 # speed in m/s of neutrons being created by fission
neutron_init_speed = 10 ** 7 # initial neutrons speed (should be around 10**5 m/s but very slow start if under 10**7 m/s)





# fusion prob function
sigma_0 = 580  # Fission cross-section for thermal neutrons in barns
sigma_thermal = 580  # Maximum fission cross-section for thermal neutrons in barns
E_0 = 0.025  # Reference energy in eV (typical for thermal neutrons)
alpha = 0.8  # Empirical constant (typically between 0.5 and 1)

