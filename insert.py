# Not considering all ISO combinations
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ANGLE_MAP = {'C': 80.0, 'D': 55.0, 'V': 35.0, 'S': 90.0, 'T': 60.0}
RELIEF_MAP = {'N': 0.0, 'B': 5.0, 'C': 7.0, 'D': 15.0, 'E': 20.0, 'F': 25.0, 'P': 11.0}
THICK_MAP = {'01': 1.59, '02': 2.38, '03': 3.18, '04': 4.76, '05': 5.56, '06': 6.35}
NOSE_MAP = {'01': 0.1, '02': 0.2, '04': 0.4, '08': 0.8, '12': 1.2, '16': 1.6}

class Insert:
    def __init__(self, ISO: str):
        self.fig = plt.figure(figsize=(13, 7.5))        #for visualization
        self.fig.canvas.manager.set_window_title("Insert Geometry Visualizer")
        self.ax = self.fig.add_axes([0.03, 0.05, 0.55, 0.90], projection='3d')

        self.ISO = ISO
        # Default ISO Parameters
        self.insert_type = ISO[0]
        self.eps = ANGLE_MAP.get(ISO[0])   # Insert Angle (deg)
        self.relief = RELIEF_MAP.get(ISO[1])        # Relief Angle (deg)
        self.thickness = THICK_MAP.get(ISO[6:8])    # Thickness (mm)
        self.nose_radius = NOSE_MAP.get(ISO[8:10])
        self.ic = 12.7                              # Inscribed Circle (mm)
        self.points = None

    def _define_insert(self):
        if self.insert_type in ['C', 'D', 'V', 'E', 'M', 'S']:
            half_w = self.ic / (2.0 * np.cos(self.eps / 2.0))     # half the tool width
            d_center = self.ic / (2.0 * np.sin(self.eps / 2.0))   # distance from tool tip to centre
            
            ins_top = np.array([
                        [0.0, 0.0, d_center],        # nose Tip
                        [half_w, 0.0, 0.0],        # right Corner
                        [0.0, 0.0, -d_center],        # back Tip
                        [-half_w, 0.0, 0.0],        # left Corner (-ve Z)  
                    ])
        
        elif self.insert_type == 'T':  # Triangle
            d_center = self.ic / 2.0                      # inscribed diameter
            side = self.ic * np.sqrt(3)             # side length of triangle
            ins_top = np.array([
                [0.0, 0.0, d_center],
                [side / 2.0, 0.0, -d_center / 2.0],                # right corner
                [-side / 2.0 , 0.0, -d_center / 2.0],
            ])

        ins_bot = ins_top.copy()    #TODO add clearance bit here
        #shift all points towards the middle using relief angle and thickness
        inset = self.thickness * np.tan(np.radians(self.relief))

        for i in range(len(ins_bot)):
            # 2D direction from vertex to center (0,0)
            xz_vec = -ins_top[i, [0, 2]]
            unit_vec = xz_vec / np.linalg.norm(xz_vec)
            # Push X and Y inward toward the centroid
            ins_bot[i, [0, 2]] += unit_vec * inset
            # Drop Y by the thickness amount
            ins_bot[i, 1] -= self.thickness

        self.points = [ins_top, ins_bot]

    def plot_insert(self):
        n_pts = len(self.points)
        faces = self.points
        #for i in range(n_pts):
            #next_i = (i + 1) % n_pts
            #faces.append([ins_top_t[i], ins_top_t[next_i], ins_bot_t[next_i], ins_bot_t[i]])
        self.ax.add_collection3d(Poly3DCollection(faces, facecolors='gold', edgecolors='k', alpha=0.95))

        
if __name__ == '__main__':
    visualizer = Insert("CNMG120408")
    visualizer._define_insert()
    visualizer.plot_insert()
    plt.show()
