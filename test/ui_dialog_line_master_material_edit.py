# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_line_master_material_editoTDNxl.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MasterMaterialEdit(object):
    def setupUi(self, MasterMaterialEdit):
        if not MasterMaterialEdit.objectName():
            MasterMaterialEdit.setObjectName(u"MasterMaterialEdit")
        MasterMaterialEdit.resize(826, 571)
        self.verticalLayout_4 = QVBoxLayout(MasterMaterialEdit)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox = QGroupBox(MasterMaterialEdit)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widget_33 = QWidget(self.groupBox)
        self.widget_33.setObjectName(u"widget_33")
        self.horizontalLayout_18 = QHBoxLayout(self.widget_33)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.label_29 = QLabel(self.widget_33)
        self.label_29.setObjectName(u"label_29")

        self.horizontalLayout_18.addWidget(self.label_29)

        self.lineEditMaterialID = QLineEdit(self.widget_33)
        self.lineEditMaterialID.setObjectName(u"lineEditMaterialID")
        self.lineEditMaterialID.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditMaterialID.sizePolicy().hasHeightForWidth())
        self.lineEditMaterialID.setSizePolicy(sizePolicy)

        self.horizontalLayout_18.addWidget(self.lineEditMaterialID)


        self.verticalLayout_3.addWidget(self.widget_33)

        self.widget_34 = QWidget(self.groupBox)
        self.widget_34.setObjectName(u"widget_34")
        self.horizontalLayout_19 = QHBoxLayout(self.widget_34)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.label_30 = QLabel(self.widget_34)
        self.label_30.setObjectName(u"label_30")

        self.horizontalLayout_19.addWidget(self.label_30)

        self.lineEditMaterialName = QLineEdit(self.widget_34)
        self.lineEditMaterialName.setObjectName(u"lineEditMaterialName")
        sizePolicy.setHeightForWidth(self.lineEditMaterialName.sizePolicy().hasHeightForWidth())
        self.lineEditMaterialName.setSizePolicy(sizePolicy)

        self.horizontalLayout_19.addWidget(self.lineEditMaterialName)


        self.verticalLayout_3.addWidget(self.widget_34)


        self.verticalLayout_4.addWidget(self.groupBox)

        self.widget_3 = QWidget(MasterMaterialEdit)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout = QHBoxLayout(self.widget_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.widget_3)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.tableInputParameters = QTableWidget(self.widget)
        if (self.tableInputParameters.columnCount() < 1):
            self.tableInputParameters.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableInputParameters.setHorizontalHeaderItem(0, __qtablewidgetitem)
        if (self.tableInputParameters.rowCount() < 9):
            self.tableInputParameters.setRowCount(9)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(0, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(1, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(2, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(3, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(4, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(5, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(6, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(7, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableInputParameters.setVerticalHeaderItem(8, __qtablewidgetitem9)
        self.tableInputParameters.setObjectName(u"tableInputParameters")

        self.verticalLayout_2.addWidget(self.tableInputParameters)


        self.horizontalLayout.addWidget(self.widget)

        self.pbCalculate = QPushButton(self.widget_3)
        self.pbCalculate.setObjectName(u"pbCalculate")

        self.horizontalLayout.addWidget(self.pbCalculate)

        self.widget_2 = QWidget(self.widget_3)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout = QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget_2)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.tableCalculatedParameters = QTableWidget(self.widget_2)
        if (self.tableCalculatedParameters.columnCount() < 1):
            self.tableCalculatedParameters.setColumnCount(1)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableCalculatedParameters.setHorizontalHeaderItem(0, __qtablewidgetitem10)
        if (self.tableCalculatedParameters.rowCount() < 8):
            self.tableCalculatedParameters.setRowCount(8)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableCalculatedParameters.setVerticalHeaderItem(0, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableCalculatedParameters.setVerticalHeaderItem(1, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableCalculatedParameters.setVerticalHeaderItem(2, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableCalculatedParameters.setVerticalHeaderItem(3, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableCalculatedParameters.setVerticalHeaderItem(4, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableCalculatedParameters.setVerticalHeaderItem(5, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableCalculatedParameters.setVerticalHeaderItem(6, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableCalculatedParameters.setVerticalHeaderItem(7, __qtablewidgetitem18)
        self.tableCalculatedParameters.setObjectName(u"tableCalculatedParameters")

        self.verticalLayout.addWidget(self.tableCalculatedParameters)


        self.horizontalLayout.addWidget(self.widget_2)


        self.verticalLayout_4.addWidget(self.widget_3)

        self.buttonBox = QDialogButtonBox(MasterMaterialEdit)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_4.addWidget(self.buttonBox)


        self.retranslateUi(MasterMaterialEdit)
        self.buttonBox.accepted.connect(MasterMaterialEdit.accept)
        self.buttonBox.rejected.connect(MasterMaterialEdit.reject)

        QMetaObject.connectSlotsByName(MasterMaterialEdit)
    # setupUi

    def retranslateUi(self, MasterMaterialEdit):
        MasterMaterialEdit.setWindowTitle(QCoreApplication.translate("MasterMaterialEdit", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("MasterMaterialEdit", u"Materials", None))
        self.label_29.setText(QCoreApplication.translate("MasterMaterialEdit", u"Material ID", None))
        self.label_30.setText(QCoreApplication.translate("MasterMaterialEdit", u"Material Name", None))
        self.label.setText(QCoreApplication.translate("MasterMaterialEdit", u"Input Parameters", None))
        ___qtablewidgetitem = self.tableInputParameters.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MasterMaterialEdit", u"Value", None));
        ___qtablewidgetitem1 = self.tableInputParameters.verticalHeaderItem(0)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MasterMaterialEdit", u"Outer Diameter [m]", None));
        ___qtablewidgetitem2 = self.tableInputParameters.verticalHeaderItem(1)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MasterMaterialEdit", u"Wet Weight [kg/m]", None));
        ___qtablewidgetitem3 = self.tableInputParameters.verticalHeaderItem(2)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MasterMaterialEdit", u"Dry Weight [kg/m]", None));
        ___qtablewidgetitem4 = self.tableInputParameters.verticalHeaderItem(3)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MasterMaterialEdit", u"EA [kN]", None));
        ___qtablewidgetitem5 = self.tableInputParameters.verticalHeaderItem(4)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MasterMaterialEdit", u"EI [kN.m^2]", None));
        ___qtablewidgetitem6 = self.tableInputParameters.verticalHeaderItem(5)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MasterMaterialEdit", u"Ci", None));
        ___qtablewidgetitem7 = self.tableInputParameters.verticalHeaderItem(6)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MasterMaterialEdit", u"Cd", None));
        ___qtablewidgetitem8 = self.tableInputParameters.verticalHeaderItem(7)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MasterMaterialEdit", u"GAS [kg/m]", None));
        ___qtablewidgetitem9 = self.tableInputParameters.verticalHeaderItem(8)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MasterMaterialEdit", u"Break Tension [N.m^2]", None));
        self.pbCalculate.setText(QCoreApplication.translate("MasterMaterialEdit", u"Calculate", None))
        self.label_2.setText(QCoreApplication.translate("MasterMaterialEdit", u"Calculated Parameters", None))
        ___qtablewidgetitem10 = self.tableCalculatedParameters.horizontalHeaderItem(0)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MasterMaterialEdit", u"Value", None));
        ___qtablewidgetitem11 = self.tableCalculatedParameters.verticalHeaderItem(0)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MasterMaterialEdit", u"GAE [N]", None));
        ___qtablewidgetitem12 = self.tableCalculatedParameters.verticalHeaderItem(1)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MasterMaterialEdit", u"GEI [N.m^2]", None));
        ___qtablewidgetitem13 = self.tableCalculatedParameters.verticalHeaderItem(2)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MasterMaterialEdit", u"GRHOL [kg/m]", None));
        ___qtablewidgetitem14 = self.tableCalculatedParameters.verticalHeaderItem(3)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MasterMaterialEdit", u"GRHOA [kg/m]", None));
        ___qtablewidgetitem15 = self.tableCalculatedParameters.verticalHeaderItem(4)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MasterMaterialEdit", u"GCI [N.m^2]", None));
        ___qtablewidgetitem16 = self.tableCalculatedParameters.verticalHeaderItem(5)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MasterMaterialEdit", u"GCD [kg/m]", None));
        ___qtablewidgetitem17 = self.tableCalculatedParameters.verticalHeaderItem(6)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MasterMaterialEdit", u"GAS [kg/m]", None));
        ___qtablewidgetitem18 = self.tableCalculatedParameters.verticalHeaderItem(7)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MasterMaterialEdit", u"BKTEN [N.m^2]", None));
    # retranslateUi

