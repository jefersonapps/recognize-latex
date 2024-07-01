import sys
from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QShortcut, QTextEdit
)
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QBuffer, QIODevice
import pyperclip
from rapid_latex_ocr import LatexOCR
import tempfile

class RecognizeLatexApp(QWidget):
    def __init__(self):
        super().__init__()
        self.model = LatexOCR()
        self.latex_code = ""
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.label = QLabel('Selecione uma imagem de equação ou cole uma imagem')
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.btn_load = QPushButton('Carregar Imagem', self)
        self.btn_load.clicked.connect(self.load_image)
        layout.addWidget(self.btn_load)
        
        self.btn_copy = QPushButton('Copiar Código LaTeX', self)
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.btn_copy)

        self.latex_edit = QTextEdit()
        layout.addWidget(self.latex_edit)
        
        self.setLayout(layout)
        self.setWindowTitle('Imagem para LaTeX')

        self.paste_shortcut = QShortcut(QKeySequence('Ctrl+V'), self)
        self.paste_shortcut.activated.connect(self.paste_image_from_clipboard)

    def load_image(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Selecione uma imagem", "", "Images (*.png *.jpg *.bmp);;All Files (*)", options=options)
        if filePath:
            self.process_image(filePath)

    def process_image(self, image_path):
        with open(image_path, "rb") as f:
            data = f.read()
        latex_code, _ = self.model(data)
        self.latex_code = latex_code
        self.latex_edit.setPlainText(self.latex_code)
        self.show_image(image_path)

    def show_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size()*3, Qt.KeepAspectRatio))

    def copy_to_clipboard(self):
        self.latex_code = self.latex_edit.toPlainText()
        if self.latex_code:
            pyperclip.copy(self.latex_code)
            self.label.setText('Código LaTeX copiado para a área de transferência!')

    def paste_image_from_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasImage():
            image = clipboard.image()
            image_path = self.save_image_from_clipboard(image)
            if image_path:
                self.process_image(image_path)

    def save_image_from_clipboard(self, image):
        try:
            buffer = QBuffer()
            buffer.open(QIODevice.ReadWrite)
            image.save(buffer, "PNG")
            buffer.seek(0)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                f.write(buffer.data())
                return f.name
        except Exception as e:
            print(f"Erro ao salvar a imagem da área de transferência: {e}")
            return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecognizeLatexApp()
    ex.show()
    sys.exit(app.exec_())
