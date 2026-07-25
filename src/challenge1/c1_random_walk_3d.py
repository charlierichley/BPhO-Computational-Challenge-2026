# 3D random walks animation with specified walk number, step size and step number using PyVista

import pyvista as pv
import matplotlib.pyplot as plt
import numpy as np

# Parameters
walk_number = 10
n = 500
s = 5
points_per_sec = 1000
points_per_frame = 3

def choose_colors(iteration_number):
    # possible colours: jet, gist_ncar, turbo
    colors = plt.cm.gist_ncar(np.linspace(0, 0.95, iteration_number))
    return colors

def random_walk(n, s):
    directions = np.random.normal(size=(n, 3))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    directions *= s

    positions = np.vstack(([0,0,0], directions))
    return np.cumsum(positions, axis=0)

# Initialising plot
pl = pv.Plotter(window_size=(1500,1200), title="3D Random Walk Animation")
colors = choose_colors(walk_number)
lines = []
for i in range(walk_number):
    points = random_walk(n, s)
    line = pv.lines_from_points([[0,0,0], [0,0,0]])
    lines.append([line, points])
    actor = pl.add_mesh(line, color=colors[i], line_width=1.5)

# Computing limits of x,y,z axes
all_points = np.vstack([l[1] for l in lines])
limit = np.max(np.abs(all_points))
limits = [-limit, limit, -limit, limit, -limit, limit]

def update(frame):
    # For each line: update the x,y,z positions
    for line, points in lines:
        new_line = pv.lines_from_points(points[:points_per_frame*frame+2])
        line.copy_from(new_line)
    pl.render()

# Animation
n_frames = n // points_per_frame + 1
pl.add_timer_event(max_steps=n_frames, duration=int(1e3 * points_per_frame/points_per_sec), callback=update)

# Adjusting graph and axes settings
pl.add_axes()
pv.global_theme.font.family = "times"
n_labels = 5
grd = pl.show_grid(xtitle="x", ytitle="y", ztitle="z", fmt="%.0f", bounds=limits, n_xlabels=n_labels, n_ylabels=n_labels, n_zlabels=n_labels)
pl.add_title(f"3D Random Walk: s={s}, n={n}, walk number={walk_number}", font_size=18)

opacity = 0.15
grd.GetXAxesGridlinesProperty().SetOpacity(opacity)
grd.GetYAxesGridlinesProperty().SetOpacity(opacity)
grd.GetZAxesGridlinesProperty().SetOpacity(opacity)
pl.set_scale(xscale=1, yscale=1, zscale=1)

pl.camera_position = "iso"
pl.camera.elevation -= 10
pl.camera.zoom(0.95)
pl.show()