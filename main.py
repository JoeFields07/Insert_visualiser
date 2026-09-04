#conda activate visualiser_env
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, CheckButtons
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class TurningToolVisualizer:
    def __init__(self):
        self.fig = plt.figure(figsize=(13, 7.5))
        self.fig.canvas.manager.set_window_title("Insert Geometry Visualizer")
        self.ax = self.fig.add_axes([0.03, 0.05, 0.55, 0.90], projection='3d')
        
        # Default ISO Parameters
        self.insert_type = 'C'
        self.alpha_n = 0.0      # Rake Angle (deg)
        self.fn = 1.0           # Feed per revolution (mm/rev)
        self.lambda_s = 0.0     # Inclination Angle (deg)
        self.kr = 95.0          # Major Cutting Edge Angle κr (deg)
        self.ap = 2.5           # Depth of Cut ap (mm)
        self.thickness = 4.76   # Insert Thickness (mm)
        self.ic = 12.7          # Inscribed Circle (mm)

        # Stored camera orientation parameters
        self.current_elev = 0
        self.current_azim = 90
        self.current_roll = -90
        self.is_first_run = True

        # Flags to control visibility of different components
        self.wp_visible         = True
        self.cut_point_visible  = False
        self.feed_arrow_visible = False
        self.feed_DoC_visible   = False
        self.friction_visible   = False
        self.cut_force_visible  = False

        self._setup_ui_controls()
        self.update(None)


    def _setup_ui_controls(self):
        """Define the UI layout and configure the buttons"""
        color_bg = 'lightgoldenrodyellow'
        
        ax_shape = self.fig.add_axes([0.68, 0.82, 0.24, 0.12], facecolor=color_bg)
        self.radio_shape = RadioButtons(ax_shape, ('C (80° Rhombic)', 'D (55° Rhombic)', 'S (Square)', 'T (Triangle)'), active=0)
        self.radio_shape.on_clicked(self._on_shape_change)

        ax_options = self.fig.add_axes([0.8, 0.05, 0.16, 0.18], facecolor=color_bg)
        self.check_options = CheckButtons(ax_options, ('Workpiece', 'Cut Point', 'Feed Arrow', 'Feed DoC', 'Friction Forces', 'Cut Forces'), 
                                        actives=[self.wp_visible, self.cut_point_visible, self.feed_arrow_visible, self.feed_DoC_visible, self.friction_visible, self.cut_force_visible],
                                        label_props={'size': ['medium']*6},
                                        frame_props={'s': [180] * 6}, 
                                        check_props={'s': [180] * 6})
        self.check_options.on_clicked(self._on_option_change)

        ax_ap = self.fig.add_axes([0.68, 0.72, 0.24, 0.025], facecolor=color_bg)
        self.slider_ap = Slider(ax_ap, 'Radial Depth aₚ', 0.0, 6.0, valinit=self.ap, valfmt='%.1f mm')
        self.slider_ap.on_changed(self.update)

        ax_fn = self.fig.add_axes([0.68, 0.63, 0.24, 0.025], facecolor=color_bg)
        self.slider_fn = Slider(ax_fn, 'Feed/rev f_n', 0.0, 2, valinit=self.fn, valfmt='%.2f mm')
        self.slider_fn.on_changed(self.update)
        
        ax_alpha = self.fig.add_axes([0.68, 0.54, 0.24, 0.025], facecolor=color_bg)
        self.slider_alpha = Slider(ax_alpha, 'Rake Angle αₙ', -15.0, 15.0, valinit=self.alpha_n, valfmt='%.1f°')
        self.slider_alpha.on_changed(self.update)

        ax_lambda = self.fig.add_axes([0.68, 0.45, 0.24, 0.025], facecolor=color_bg)
        self.slider_lambda = Slider(ax_lambda, 'Inclination λₛ', -15.0, 15.0, valinit=self.lambda_s, valfmt='%.1f°')
        self.slider_lambda.on_changed(self.update)

        ax_kr = self.fig.add_axes([0.68, 0.36, 0.24, 0.025], facecolor=color_bg)
        self.slider_kr = Slider(ax_kr, 'Major Edge Angle κᵣ', 0.0, 110.0, valinit=self.kr, valfmt='%.1f°')
        self.slider_kr.on_changed(self.update)


    def _on_shape_change(self, label):
        """Trigger to change which insert is shown"""
        self.insert_type = label[0]
        self.update(None)


    def _on_option_change(self, labels):
        """Trigger to change visibility of components"""
        status = self.check_options.get_status()
        self.wp_visible         = status[0]
        self.cut_point_visible  = status[1]
        self.feed_arrow_visible = status[2]
        self.feed_DoC_visible   = status[3]
        self.friction_visible   = status[4]
        self.cut_force_visible  = status[5]
        self.update(None)


    def _generate_insert_and_forces(self):
        thickness = self.thickness
        ic = self.ic
        
        #Insert base geometry (Nose tip at [0, 0, 0], cutting edge vertical in -X)
        if self.insert_type in ['C', 'D', 'V', 'E', 'M', 'S']:
            angle_map = {'C': 80.0, 'D': 55.0, 'E': 75.0, 'M': 86.0, 'V': 35.0, 'S': 90.0}
            eps = np.radians(angle_map.get(self.insert_type, 80.0))     #insert angle in radians
            
            half_w = ic / (2.0 * np.cos(eps / 2.0))     # half the tool width
            d_center = ic / (2.0 * np.sin(eps / 2.0))   # distance from tool tip to centre
            edge_length = np.sqrt(half_w ** 2 + d_center ** 2)
            
            ins_top = np.array([
                [0.0, 0.0, 0.0],                        # nose Tip
                [-edge_length, 0.0, 0.0],               # right Corner
                [-edge_length * np.cos(eps) - edge_length, 0.0, -edge_length * np.sin(eps)],  # back Tip
                [-edge_length * np.cos(eps), 0.0, -edge_length * np.sin(eps)],               # left Corner (-ve Z)  
            ])

        elif self.insert_type == 'T':  # Triangle
            side = ic * np.sqrt(3.0)                    # side length of triangle
            ins_top = np.array([
                [0.0, 0.0, 0.0],
                [-side, 0.0, 0.0],
                [-side/2, 0.0, -side* np.sin(np.pi/3)],
            ])

        ins_bot = ins_top.copy() 
        ins_bot[:, 1] = -thickness                      # copy top coordinates and shift down

        ins_arrows = np.array([
                [0.0, -15.0, 0.0],              # perpendicular friction force (N)
                [0.0, 0.0, -15.0],              # friction in Z (Rake - F in 2D)
                [-15.0, 0.0, 0.0],              # friction in X (radial)
        ])
        return ins_top, ins_bot, ins_arrows


    @staticmethod
    def _rotation_matrix(axis, angle_deg):
        """Creates a rotation matrix for an axis rotation"""
        rad = np.radians(angle_deg)
        c, s = np.cos(rad), np.sin(rad)
        if axis == 'x':
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == 'y':
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == 'z':
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


    def _transform_mesh(self, points):
        """Rotate the points by the current angles"""
        angle_map = {'C': 80.0, 'D': 55.0, 'S': 90.0, 'T': 60.0, 'V': 35.0} # Lookup nose angle for active shape
        eps_deg = angle_map.get(self.insert_type, 80.0)

        kr_rad = np.radians(self.kr)
        lambda_rad = np.radians(self.lambda_s)
        alpha_rad = np.radians(self.alpha_n)

        # Rake Matrix (Rx)
        Rx = np.array([
            [1, 0, 0],
            [0,  np.cos(alpha_rad), np.sin(alpha_rad)],
            [0, -np.sin(alpha_rad), np.cos(alpha_rad)]
        ])

        # Inclination Matrix (Rz)
        Rz = np.array([
            [np.cos(lambda_rad), -np.sin(lambda_rad), 0],
            [np.sin(lambda_rad),  np.cos(lambda_rad), 0],
            [0, 0, 1]
        ])

        # KAPR Rotation (Ry)
        theta_y = np.pi/2- kr_rad       #adjust/flip cutting angle to match WP
        Ry = np.array([
            [ np.cos(theta_y), 0, np.sin(theta_y)],
            [ 0,               1, 0              ],
            [-np.sin(theta_y), 0, np.cos(theta_y)]
        ])

        # Composite orthonormal transformation
        R_total = Ry @ Rz @ Rx

        return np.dot(points, R_total.T)


    def update(self, val):
        # Capture user view parameters (elev, azim, roll)
        if not self.is_first_run and hasattr(self, 'ax') and self.ax.elev is not None:
            self.current_elev = self.ax.elev
            self.current_azim = self.ax.azim
            self.current_roll = getattr(self.ax, 'roll', 0)

        self.ax.clear()

        self.ap = self.slider_ap.val
        self.fn = self.slider_fn.val
        self.alpha_n = self.slider_alpha.val
        self.lambda_s = self.slider_lambda.val
        self.kr = self.slider_kr.val

        # Geometry Assembly
        ins_top, ins_bot, ins_arrows = self._generate_insert_and_forces()
    
        ins_top_t = self._transform_mesh(ins_top)
        ins_bot_t = self._transform_mesh(ins_bot)
        ins_arrows_t = self._transform_mesh(ins_arrows)

        # Target location of cutting tip: at radial engagement (ap) on the X-axis
        target_tip_pos = np.array([self.ap, 0.0, 0.0])

        # Current position of the transformed insert tip
        current_tip_pos = ins_top_t[0].copy()

        # Translation vector applied to everything
        shift_vector = target_tip_pos - current_tip_pos

        ins_top_t += shift_vector
        ins_bot_t += shift_vector

        # Render 3D Insert Polyhedron
        faces = [ins_top_t, ins_bot_t]
        n_pts = len(ins_top_t)
        for i in range(n_pts):
            next_i = (i + 1) % n_pts
            faces.append([ins_top_t[i], ins_top_t[next_i], ins_bot_t[next_i], ins_bot_t[i]])

        self.ax.add_collection3d(Poly3DCollection(faces, facecolors='gold', edgecolors='k', alpha=0.95))

        # Workpiece Surface Mesh
        r_stock = 25.0
        if self.wp_visible:
            r_turned = max(1.0, r_stock - self.ap)
            theta = np.linspace(0, 2*np.pi, 30)

            z_uncut = np.linspace(0, 30, 10)        #body in feed axis
            theta_g, z_uncut_g = np.meshgrid(theta, z_uncut)
            x_uncut = r_stock- r_stock * np.cos(theta_g) 
            y_uncut = r_stock * np.sin(theta_g)
            self.ax.plot_surface(x_uncut, y_uncut, z_uncut_g, color='deepskyblue', alpha=0.2, edgecolor='none')

            z_turned = np.linspace(-30, 0, 10)
            _, z_turned_g = np.meshgrid(theta, z_turned)
            x_turned = r_stock - r_turned * np.cos(theta_g)
            y_turned = r_turned * np.sin(theta_g)
            self.ax.plot_surface(x_turned, y_turned, z_turned_g, color='cyan', alpha=0.35, edgecolor='none')

        # Annotations 
        if self.cut_point_visible:
            self.ax.scatter([self.ap], [0], [0], color='red', s=60, zorder=10, label='Cutting Point')
            self.ax.plot([self.ap, ins_top_t[1][0]], [0, ins_top_t[1][1]], [0, ins_top_t[1][2]], 
                         color='red', linewidth=2, zorder=10, label='Cutting Edge')

        if self.feed_arrow_visible:
            self.ax.quiver(r_stock, 0, -15, 0, 0, 15, color='magenta', linewidth=2.5, arrow_length_ratio=0.25, label='Feed Direction (+Z)')

        # DoC graphic
        if self.feed_DoC_visible:
            half_theta = np.linspace(0, np.pi, 30)      #feed DoC indicator won't go all way round
            z_feedDoC = np.linspace(-self.fn, 0, 10)
            half_theta_g, z_feedDoC_g = np.meshgrid(half_theta, z_feedDoC)
            x_feedDoC = r_stock - r_stock * np.cos(half_theta_g)
            y_feedDoC = r_stock * np.sin(half_theta_g)
            self.ax.plot_surface(x_feedDoC, y_feedDoC, z_feedDoC_g, color='red', alpha=0.35, edgecolor='none',label='Next material removed')

        # Friction force arrows
        if self.friction_visible:
            self.ax.quiver(self.ap, 0, 0, ins_arrows_t[0][0], ins_arrows_t[0][1], ins_arrows_t[0][2],  
                                color='red', linewidth=2.5, arrow_length_ratio=0.25, label='Normal Friction (N)')
            self.ax.quiver(self.ap, 0, 0, ins_arrows_t[1][0], ins_arrows_t[1][1], ins_arrows_t[1][2],  
                                color='darkred', linewidth=2.5, arrow_length_ratio=0.25, label='Rake Friction (Fz)')
            self.ax.quiver(self.ap, 0, 0, ins_arrows_t[2][0], ins_arrows_t[2][1], ins_arrows_t[2][2],  
                                color='orangered', linewidth=2.5, arrow_length_ratio=0.25, label='Radial Friction (Fx)')

        # Measured force arrows
        if self.cut_force_visible:
            self.ax.quiver(self.ap, 0, 0, 0, -15, 0, color='aquamarine', linewidth=2.5, arrow_length_ratio=0.25, label='Cutting Force (Fc)')
            self.ax.quiver(self.ap, 0, 0, 0, 0, -15, color='limegreen',  linewidth=2.5, arrow_length_ratio=0.25, label='Feed Force (Ft)')
            self.ax.quiver(self.ap, 0, 0, -15, 0, 0, color='darkgreen', linewidth=2.5, arrow_length_ratio=0.25, label='Radial Force (Fr)')

        # Fixed Axis Bounds
        self.ax.set_xlim3d([-20, 50])
        self.ax.set_ylim3d([-30, 30])
        self.ax.set_zlim3d([-30, 30])
        self.ax.set_box_aspect([1, 1, 1])

        self.ax.set_xlabel('X (Radial)')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z (Feed)')
        self.ax.legend(loc='upper right')

        # 7. Restore exact user elev, azim, and roll
        self.ax.view_init(elev=self.current_elev, azim=self.current_azim, roll=self.current_roll)

        self.is_first_run = False
        self.fig.canvas.draw_idle()


if __name__ == '__main__':
    visualizer = TurningToolVisualizer()
    plt.show()