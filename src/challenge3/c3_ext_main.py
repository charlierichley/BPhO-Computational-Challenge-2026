from c3_ext_functions import *

# Choosing temperature and method of integration
T = 4000
integration_methods = ["Trapezium Rule", "Simpson's Rule", "Adaptive Simpson"]
method = integration_methods[2]

# Initialising plot
plt.style.use("dark_background")
plt.rcParams['toolbar'] = 'None'
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title(f"Planck Spectrum - {method}")

# Creating Planck Spectrum curve
points_curve = return_points(d_lamda_curve, T, lamda_min_curve, lamda_max_curve)
points_curve = np.column_stack((points_curve[0], points_curve[1]))
curve_color = "#ff5a5a"
points_curve[:,0] *= 1e9
curve, = ax.plot(points_curve[:,0], points_curve[:,1], alpha=1, color=curve_color, linewidth=1, zorder=30)

# Obtaining function for the chosen integration method
methods = {"Trapezium Rule": trapezium_rule, "Simpson's Rule": simpsons_rule, "Adaptive Simpson": adaptive_simpson}
method_func = methods[method]

# Numerical integration points
points_integrate = return_points(d_lamda_integrate, T, lamda_min_integrate, lamda_max_integrate)
points_integrate = np.column_stack((points_integrate[0], points_integrate[1]))
points_integrate[:, 0] *= 1e9

if method_func == trapezium_rule:
    # Trapezium points for visualisation
    points_trap = return_points(d_lamda_trap, T, lamda_min_trap, lamda_max_trap)
    points_trap = np.column_stack((points_trap[0], points_trap[1]))
    points_trap[:, 0] *= 1e9

    x = points_trap[:, 0]
    y = points_trap[:, 1]
    length = len(x)

    # Obtaining integral value from more accurate points over a larger range than what is being plotted
    measured_value = trapezium_rule(points_integrate)

    # Parameters for plotting
    past_frames = set()
    trap_color = "#FFFFFF"
    alpha_vert = 0.15
    alpha_diag = 0.5
    alpha_fill = 0.6

    def update(frame):
        if frame in past_frames:
            return
        past_frames.add(frame)
        i = frame

        # Filling inside the trapezium
        fill = ax.fill([x[i], x[i], x[i+1], x[i+1]], [0, y[i], y[i+1], 0], color=trap_color, alpha=alpha_fill, zorder=10, edgecolor='none')

        # Vertical and diagonal lines of the trapezium
        l1 = ax.plot([x[i], x[i]], [0, y[i]], color=trap_color, alpha=alpha_vert, zorder=10) # left vertical line
        l2 = ax.plot([x[i+1], x[i+1]], [0, y[i+1]], color=trap_color, alpha=alpha_vert, zorder=10) # right vertical line
        l3 = ax.plot([x[i], x[i+1]], [y[i], y[i+1]], color=trap_color, alpha=alpha_diag, zorder=10) # slanted edge

        return fill + l1 + l2 + l3

    CONST_TRAPEZIA = 0.25
    trapezia_per_second = CONST_TRAPEZIA * length
    ani = animation.FuncAnimation(fig=fig, func=update, frames=length-1, interval=1e3/trapezia_per_second, repeat=False)

if method_func == simpsons_rule:
    # Simpson's rule points for viusalisation (not the same as those used for integration)
    points_simp = return_points(d_lamda_simp, T, lamda_min_simp, lamda_max_simp)
    points_simp = np.column_stack((points_simp[0], points_simp[1]))
    points_simp[:, 0] *= 1e9

    x = points_simp[:, 0]
    y = points_simp[:, 1]
    length = len(x)

    # Simpson's rule only works with odd number of points
    if length % 2 == 0: # Must remove the final point
        x = x[:-1]
        y = y[:-1]
        points_integrate = points_integrate[:-1]
        ax.set_xlim(right=x[-1])

    # Obtaining integral value from more accurate points over a larger range than what is being plotted
    measured_value = simpsons_rule(points_integrate)

    fill_color = "#ffffff"
    line_width = 0.3
    past_frames = set()

    def update(frame):
        if frame in past_frames:
            return
        past_frames.add(frame)
        i = 2 * frame

        # At each frame, take current and next two [x,y] pairs and polyfit a quadratic between the three points
        x_curve, y_curve = fill_interval([x[i], x[i+2]], T)

        fill = ax.fill_between(x_curve, 0, y_curve, alpha=0.5, color=fill_color, linewidth=line_width)
        return [fill]

    CONST_CURVE = 0.15
    curve_per_second = CONST_CURVE * length

    ani = animation.FuncAnimation(fig=fig, func=update, frames=int((length-1)/2), interval=1e3/curve_per_second, repeat=False)

if method_func == adaptive_simpson:
    # Parameters for calculating / plotting
    tolerance_integrate = 1e-8
    tolerance_plot = 10
    line_width = 0.3
    alpha_curve = 0.5
    curve_zorder = 100

    fill_color = "#ffffff"
    past_frames = set()

    measured_value = adaptive_simpson(B, lamda_min_integrate * 1e-9, lamda_max_integrate * 1e-9, T, tolerance=tolerance_integrate)

    lamda_adap = return_points(d_lamda_adap, T, lamda_min_adap, lamda_max_adap, is_adap_plot=True)
    active_intervals = [[lamda_adap[i], lamda_adap[i+1]] for i in range(len(lamda_adap)- 1)]

    def update(frame):
        if frame in past_frames:
            return
        past_frames.add(frame)

        # No more intervals to update
        if active_intervals == []:
            ani.event_source.stop()
            return []

        # Plot initial curves
        if frame == 0:
            for index, interval in enumerate(active_intervals):
                x_curve, y_curve = fill_interval(interval, T)

                fill = ax.fill_between(x_curve, 0, y_curve, alpha=alpha_curve, color=fill_color, linewidth=line_width, zorder=curve_zorder)
                active_intervals[index] = [interval, fill]
            return

        # Not on initial frame - must update old curves
        else:
            new_active_intervals = []
            for index, lst in enumerate(active_intervals):
                # Determine if current interval's integral error is acceptable
                interval, old_fill = lst
                lamda_a, lamda_b = interval

                f_a = B(lamda_a, T, is_adap_integrate=True)
                f_b = B(lamda_b, T, is_adap_integrate=True)

                whole = simpson_basic(B, T, lamda_a * 1e-9, f_a, lamda_b * 1e-9, f_b)

                lamda_mid = (lamda_a + lamda_b) / 2
                f_mid = B(lamda_mid, T, is_adap_integrate=True)
                area_a = simpson_basic(B, T, lamda_a * 1e-9, f_a, lamda_mid * 1e-9, f_mid)
                area_b = simpson_basic(B, T, lamda_mid * 1e-9, f_mid, lamda_b * 1e-9, f_b)
                delta = area_a + area_b - whole

                is_acceptable = is_acceptable_adaptive(delta, tolerance_plot)

                # If interval has to split, display new curves for new intervals and remove old curve
                if is_acceptable == False:
                    lower_interval = [lamda_a, lamda_mid]
                    upper_interval = [lamda_mid, lamda_b]

                    x_curve_lower, y_curve_lower = fill_interval(lower_interval, T)
                    x_curve_upper, y_curve_upper = fill_interval(upper_interval, T)

                    fill_lower = ax.fill_between(x_curve_lower, 0, y_curve_lower, alpha=alpha_curve, color=fill_color, linewidth=line_width, zorder=curve_zorder)
                    fill_upper = ax.fill_between(x_curve_upper, 0, y_curve_upper, alpha=alpha_curve, color=fill_color, linewidth=line_width, zorder=curve_zorder)

                    new_active_intervals.append([lower_interval, fill_lower])
                    new_active_intervals.append([upper_interval, fill_upper])
                    old_fill.remove()

            # Copying new list by value not reference
            active_intervals[:] = new_active_intervals
            return

    # Old curve_per_second default: 1.18, but now changed to 1.5
    curve_per_second = 1.5
    ani = animation.FuncAnimation(fig=fig, func=update, frames=int(1e9), interval=1e3 / curve_per_second, repeat=False)

# Comparing the actual integral vs the measured integral
I_measured = measured_value
I_actual = sigma_const * (T**4) / np.pi
percentage_error = percent_error(I_measured, I_actual)

# Adding a box to display I_measured and I_actual
I_measured_str = sci_notation(I_measured)
I_actual_str = sci_notation(I_actual)
annotation = ax.text(0.59, 0.81,
                     f"$I_{{measured}}$ = {I_measured_str}"
                     f"\n$I_{{actual}}$ = {I_actual_str}"
                     f"\nPercentage Error: {percentage_error:.3g}%",
                     transform=ax.transAxes, bbox=dict(facecolor="black", edgecolor="white", alpha=0.8))

# Adjusting axes limits and adding labels
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0), useMathText=True)
ax.set_xlabel("Wavelength / nm")
ax.set_ylabel("Spectral radiance / $Wsr^{-1}m^{-2}/nm$")
plt.title(f"Numerical Integration of Planck Spectrum - {method}", fontweight="bold")
plt.show()