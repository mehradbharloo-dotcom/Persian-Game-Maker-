import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QSplitter, QFrame, QOpenGLWidget
from OpenGL.GL import *

class SceneView(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(480, 360)
        self.objects = [{'name': 'مکعب', 'x': 0.0, 'y': 0.0, 'z': 0.0}]
        self.yaw, self.pitch, self.zoom = -35.0, 25.0, 1.0
        self.last_pos = None

    def initializeGL(self):
        glClearColor(0.12, 0.14, 0.18, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, max(1, w), max(1, h))

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        aspect = float(max(1, self.width())) / float(max(1, self.height()))
        half = 7.0 / max(0.35, self.zoom)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if aspect >= 1.0:
            glOrtho(-half * aspect, half * aspect, -half, half, -100.0, 100.0)
        else:
            glOrtho(-half, half, -half / aspect, half / aspect, -100.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, -0.8, -8.0)
        glRotatef(self.pitch, 1.0, 0.0, 0.0)
        glRotatef(self.yaw, 0.0, 1.0, 0.0)
        self.draw_grid()
        for i, item in enumerate(self.objects):
            glPushMatrix()
            glTranslatef(item['x'], item['y'], item['z'])
            self.draw_cube(i == 0)
            glPopMatrix()
        glFlush()

    def draw_grid(self):
        glDisable(GL_DEPTH_TEST)
        glColor3f(0.27, 0.30, 0.35)
        glBegin(GL_LINES)
        for v in range(-10, 11):
            glVertex3f(float(v), -1.0, -10.0); glVertex3f(float(v), -1.0, 10.0)
            glVertex3f(-10.0, -1.0, float(v)); glVertex3f(10.0, -1.0, float(v))
        glEnd()
        glEnable(GL_DEPTH_TEST)

    def draw_cube(self, selected=False):
        faces = [
            [( -.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)],
            [(.5,-.5,-.5),(-.5,-.5,-.5),(-.5,.5,-.5),(.5,.5,-.5)],
            [(.5,-.5,.5),(.5,-.5,-.5),(.5,.5,-.5),(.5,.5,.5)],
            [(-.5,-.5,-.5),(-.5,-.5,.5),(-.5,.5,.5),(-.5,.5,-.5)],
            [(-.5,.5,.5),(.5,.5,.5),(.5,.5,-.5),(-.5,.5,-.5)],
            [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,-.5,.5),(-.5,-.5,.5)]
        ]
        colors = [(0.20,0.62,0.95),(0.18,0.48,0.78),(0.16,0.55,0.85),(0.12,0.40,0.70),(0.35,0.72,1.0),(0.10,0.32,0.60)] if selected else [(0.75,0.48,0.22)] * 6
        glBegin(GL_QUADS)
        for color, face in zip(colors, faces):
            glColor3f(*color)
            for vertex in face: glVertex3f(*vertex)
        glEnd()

    def add_cube(self):
        n = len(self.objects) + 1
        name = 'مکعب ' + str(n)
        self.objects.append({'name': name, 'x': float((n-1)%3)*1.5, 'y': 0.0, 'z': float((n-1)//3)*1.5})
        self.update()
        return name

    def mousePressEvent(self, event): self.last_pos = event.pos()
    def mouseMoveEvent(self, event):
        if self.last_pos is not None and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_pos
            self.yaw += delta.x() * 0.6
            self.pitch = max(-85.0, min(85.0, self.pitch + delta.y() * 0.6))
            self.last_pos = event.pos()
            self.update()
    def wheelEvent(self, event):
        self.zoom = max(0.35, min(3.0, self.zoom + event.angleDelta().y()/120.0*0.12))
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Persian Game Maker | بازی‌ساز فارسی')
        self.resize(1120, 720)
        self.setMinimumSize(850, 560)
        self.setLayoutDirection(Qt.RightToLeft)
        root = QWidget(); layout = QVBoxLayout(root)
        layout.setContentsMargins(10,10,10,10); layout.setSpacing(8)
        header = QHBoxLayout()
        brand = QLabel('Persian Game Maker'); brand.setObjectName('brand')
        header.addWidget(brand); header.addStretch(1); header.addWidget(QLabel('محیط ساخت بازی سه‌بعدی'))
        layout.addLayout(header)
        toolbar = QHBoxLayout()
        add_btn = QPushButton('＋ افزودن مکعب'); add_btn.clicked.connect(self.add_cube)
        reset_btn = QPushButton('بازنشانی دوربین'); reset_btn.clicked.connect(self.reset_camera)
        toolbar.addWidget(add_btn); toolbar.addWidget(reset_btn); toolbar.addStretch(1)
        toolbar.addWidget(QLabel('نسخه آزمایشی ۰.۱')); layout.addLayout(toolbar)
        split = QSplitter(Qt.Horizontal)
        side = QFrame(); side.setObjectName('sidePanel'); side.setMinimumWidth(190)
        side_layout = QVBoxLayout(side); side_layout.addWidget(QLabel('اشیای صحنه'))
        self.object_list = QListWidget(); self.object_list.addItem('مکعب'); side_layout.addWidget(self.object_list)
        side_layout.addWidget(QLabel('راهنما:'))
        hint = QLabel('• چرخ ماوس: بزرگ‌نمایی\n• کشیدن با کلیک چپ: چرخاندن دید\n• افزودن مکعب: ساخت شیء جدید')
        hint.setWordWrap(True); hint.setObjectName('muted'); side_layout.addWidget(hint)
        self.viewport = SceneView()
        split.addWidget(side); split.addWidget(self.viewport); split.setSizes([230,850])
        layout.addWidget(split, 1)
        status = QLabel('آماده | صحنه سه‌بعدی آزمایشی'); status.setObjectName('status'); layout.addWidget(status)
        self.setCentralWidget(root)
        self.setStyleSheet('''QMainWindow,QWidget{background:#20242c;color:#edf1f7;font-family:Segoe UI;font-size:10pt;} QLabel#brand{font-size:18pt;font-weight:bold;color:#70b7ff;} QLabel#muted{color:#aab4c2;} QFrame#sidePanel{background:#292f39;border:1px solid #3b4350;border-radius:6px;} QPushButton{background:#286ca8;color:white;border:0;border-radius:5px;padding:8px 14px;} QPushButton:hover{background:#347fbe;} QListWidget{background:#20242c;border:1px solid #414a58;border-radius:4px;padding:4px;} QLabel#status{color:#9ba8b8;padding:4px;}''')
    def add_cube(self):
        name = self.viewport.add_cube(); self.object_list.addItem(name)
        self.object_list.setCurrentRow(self.object_list.count()-1)
    def reset_camera(self):
        self.viewport.yaw, self.viewport.pitch, self.viewport.zoom = -35.0, 25.0, 1.0
        self.viewport.update()

def main():
    fmt = QSurfaceFormat(); fmt.setRenderableType(QSurfaceFormat.OpenGL)
    fmt.setVersion(2,1); fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication(sys.argv); app.setApplicationName('Persian Game Maker')
    window = MainWindow(); window.show(); sys.exit(app.exec_())

if __name__ == '__main__': main()