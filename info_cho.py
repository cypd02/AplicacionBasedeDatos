import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, 
    QFormLayout, QLineEdit, QDateEdit, QMessageBox, QHBoxLayout, QLabel, QDialog, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QDate
import psycopg2
import psycopg2.extras
import sys

class DatabaseConnection:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="tu_db",
            user="tu_usuario",
            password="tu_contraseña",
            host="localhost",
            cursor_factory=psycopg2.extras.DictCursor
        )
        self.cursor = self.connection.cursor()

class InfoCho(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Lista de Choferes")
        self.resize(600, 600)

        self.layout = QVBoxLayout()
        
        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet("font-size: 16px;")  # Ajustar el tamaño de la fuente
        self.layout.addWidget(self.list_widget)

        self.load_data_btn = QPushButton('Cargar Datos', self)
        self.load_data_btn.setStyleSheet("font-size: 16px; background-color: rgb(255, 165, 0);")  # Ajustar el tamaño de la fuente y color
        self.load_data_btn.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_data_btn)

        self.setLayout(self.layout)

    def load_data(self):
        try:
            query = """
            SELECT e.id_chofer, e.nombre, e.apellido_paterno, e.apellido_materno, a.apodo
            FROM empleado_chofer e
            LEFT JOIN apodos a ON e.id_chofer = a.id_chofer
            WHERE e.estatus = 'ACTIVO'
            """
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()

            self.list_widget.clear()
            for row in rows:
                item_widget = QWidget()
                item_layout = QHBoxLayout()
                item_layout.setContentsMargins(0, 0, 0, 0)
                
                item_text = f"{row['id_chofer']} - {row['nombre']} {row['apellido_paterno']} {row['apellido_materno']}"
                if row['apodo']:
                    item_text += f" - \"<span style='color:red;'>{row['apodo']}</span>\""
                
                item_label = QLabel(item_text)
                item_label.setFixedHeight(25)
                item_label.setStyleSheet("font-size: 16px;")  # Ajustar el tamaño de la fuente
                item_label.setTextFormat(Qt.RichText)  # Para que el QLabel interprete el HTML

                view_btn = QPushButton("Ver")
                view_btn.setStyleSheet("background-color: rgb(255, 165, 0);")
                view_btn.setFixedSize(50, 36)
                view_btn.clicked.connect(lambda ch, row=row: self.view_item(row))
                
                item_layout.addWidget(item_label)
                item_layout.addWidget(view_btn)
                
                item_widget.setLayout(item_layout)
                
                list_item = QListWidgetItem(self.list_widget)
                list_item.setSizeHint(item_widget.sizeHint())
                self.list_widget.addItem(list_item)
                self.list_widget.setItemWidget(list_item, item_widget)
                
        except Exception as e:
            print(f"Error al cargar los datos: {e}")
            QMessageBox.critical(self, 'Error', f'No se pudieron cargar los datos: {e}', QMessageBox.Ok)

    def view_item(self, row):
        self.view_window = ViewWindow(self.db, row['id_chofer'])
        self.view_window.show()

class ViewWindow(QDialog):
    def __init__(self, db, item_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.item_id = item_id
        self.setWindowTitle("Ver Chofer")
        
        self.layout = QFormLayout()
        
        self.nombre = QLineEdit(self)
        self.nombre.setReadOnly(True)
        self.nombre.setStyleSheet("font-size: 16px;")
        self.layout.addRow('Nombre:', self.nombre)

        self.apellido_paterno = QLineEdit(self)
        self.apellido_paterno.setReadOnly(True)
        self.apellido_paterno.setStyleSheet("font-size: 16px;")
        self.layout.addRow('Apellido Paterno:', self.apellido_paterno)

        self.apellido_materno = QLineEdit(self)
        self.apellido_materno.setReadOnly(True)
        self.apellido_materno.setStyleSheet("font-size: 16px;")
        self.layout.addRow('Apellido Materno:', self.apellido_materno)

        self.rfc = QLineEdit(self)
        self.rfc.setReadOnly(True)
        self.rfc.setStyleSheet("font-size: 16px;")
        self.layout.addRow('RFC:', self.rfc)

        self.nss = QLineEdit(self)
        self.nss.setReadOnly(True)
        self.nss.setStyleSheet("font-size: 16px;")
        self.layout.addRow('NSS:', self.nss)

        self.curp = QLineEdit(self)
        self.curp.setReadOnly(True)
        self.curp.setStyleSheet("font-size: 16px;")
        self.layout.addRow('CURP:', self.curp)

        self.salario_base = QLineEdit(self)
        self.salario_base.setReadOnly(True)
        self.salario_base.setStyleSheet("font-size: 16px;")
        self.layout.addRow('Salario Base:', self.salario_base)

        self.tipo_jornada = QLineEdit(self)
        self.tipo_jornada.setReadOnly(True)
        self.tipo_jornada.setStyleSheet("font-size: 16px;")
        self.layout.addRow('Tipo de Jornada:', self.tipo_jornada)

        self.fecha_vencimiento_tarjeton = QDateEdit(self)
        self.fecha_vencimiento_tarjeton.setReadOnly(True)
        self.fecha_vencimiento_tarjeton.setCalendarPopup(True)
        self.layout.addRow('Fecha de Vencimiento del Tarjeton:', self.fecha_vencimiento_tarjeton)

        self.apodo = QLineEdit(self)
        self.apodo.setReadOnly(True)
        self.apodo.setStyleSheet("font-size: 16px;")
        self.layout.addRow('Apodo:', self.apodo)

        self.foto_labels = {
            'foto_chofer': QLabel(self)
        }
        
        for label in self.foto_labels.values():
            self.layout.addRow('Foto del Operador:', label)

        self.load_data()
        self.load_photos()

        accept_button = QPushButton('Cerrar', self)
        accept_button.clicked.connect(self.accept)
        self.layout.addWidget(accept_button)

        self.setLayout(self.layout)

    def load_data(self):
        try:
            query = """
            SELECT e.nombre, e.apellido_paterno, e.apellido_materno, e.rfc, e.nss, e.curp, e.salario_base, e.tipo_jornada, e.fecha_vencimiento_tarjeton, a.apodo
            FROM empleado_chofer e
            LEFT JOIN apodos a ON e.id_chofer = a.id_chofer
            WHERE e.id_chofer = %s
            """
            self.db.cursor.execute(query, (self.item_id,))
            row = self.db.cursor.fetchone()

            if row:
                self.nombre.setText(row['nombre'])
                self.apellido_paterno.setText(row['apellido_paterno'])
                self.apellido_materno.setText(row['apellido_materno'])
                self.rfc.setText(row['rfc'])
                self.nss.setText(row['nss'])
                self.curp.setText(row['curp'])
                self.salario_base.setText(str(row['salario_base']))
                self.tipo_jornada.setText(row['tipo_jornada'])
                self.fecha_vencimiento_tarjeton.setDate(QDate.fromString(str(row['fecha_vencimiento_tarjeton']), 'yyyy-MM-dd'))
                self.apodo.setText(row['apodo'] if row['apodo'] else "")
            else:
                QMessageBox.warning(self, 'Error', 'No se encontró el chofer con el ID proporcionado', QMessageBox.Ok)
        except Exception as e:
            print(f"Error al cargar los datos: {e}")
            QMessageBox.critical(self, 'Error', f'No se pudieron cargar los datos: {e}', QMessageBox.Ok)

    def load_photos(self):
        try:
            query = """
            SELECT foto_chofer
            FROM empleado_chofer
            WHERE id_chofer = %s
            """
            self.db.cursor.execute(query, (self.item_id,))
            row = self.db.cursor.fetchone()

            photo_keys = ['foto_chofer']
            for key, photo_data in zip(photo_keys, row):
                if photo_data:
                    label = QLabel(self)
                    pixmap = QPixmap()
                    pixmap.loadFromData(photo_data)
                    label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
                    self.layout.addRow(QLabel("Foto del Operador:"), label)
                else:
                    self.layout.addRow(QLabel("Foto del Operador:"), QLabel("Sin foto"))
        except Exception as e:
            print(f"Error al cargar las fotos: {e}")
            QMessageBox.critical(self, 'Error', f'No se pudieron cargar las fotos: {e}', QMessageBox.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = DatabaseConnection()
    info_choferes = InfoCho(db)
    info_choferes.show()
    sys.exit(app.exec_())
